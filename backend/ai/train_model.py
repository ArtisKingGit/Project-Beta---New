import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import (
    Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)

# ─────────────────────────── Paths ────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR        = os.path.join(BASE_DIR, "datasets")
MODEL_SAVE_PATH    = os.path.join(BASE_DIR, "crop_model.keras")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "class_indices.json")

# ─────────────────────────── Hyper-parameters ─────────────────────────────────
IMG_SIZE   = (224, 224)
BATCH_SIZE = 32

# Phase 1: Train the classification head with backbone frozen
PHASE1_EPOCHS = 20
PHASE1_LR     = 5e-4

# Phase 2: Fine-tune the top portion of MobileNetV2 backbone
PHASE2_EPOCHS         = 30   # additional epochs on top of phase 1
PHASE2_LR             = 5e-5
FINE_TUNE_FROM_LAYER  = 100  # unfreeze layers from this index onward (~top 54 layers of MobileNetV2-155 layers)


# ─────────────────────────── Data Generators ─────────────────────────────────
def build_generators():
    """
    Train generator uses aggressive but realistic augmentation to combat overfitting.
    Val generator only normalises.
    """
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.20,
        height_shift_range=0.20,
        shear_range=0.15,
        zoom_range=0.20,
        horizontal_flip=True,
        vertical_flip=False,         # leaf images don't appear upside-down
        brightness_range=[0.75, 1.25],
        fill_mode="reflect",          # reflect is more natural than 'nearest' for leaves
    )
    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_gen = train_datagen.flow_from_directory(
        os.path.join(DATASET_DIR, "train"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=True,
    )
    val_gen = val_datagen.flow_from_directory(
        os.path.join(DATASET_DIR, "val"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )
    return train_gen, val_gen


# ─────────────────────────── Class Weights ────────────────────────────────────
def compute_class_weights(train_gen):
    """
    Inverse-frequency class weights so minority classes (e.g. Potato_healthy)
    are not ignored by the loss function.
    """
    counts = np.array([0] * train_gen.num_classes)
    class_to_idx = train_gen.class_indices
    for class_name, idx in class_to_idx.items():
        class_dir = os.path.join(DATASET_DIR, "train", class_name)
        if os.path.isdir(class_dir):
            counts[idx] = len([
                f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])

    total = counts.sum()
    n_classes = len(counts)
    # sklearn-style balanced weighting: w_i = total / (n_classes * count_i)
    weights = {}
    for i, c in enumerate(counts):
        if c > 0:
            weights[i] = float(total) / (n_classes * c)
        else:
            weights[i] = 1.0

    print("\n[CLASS WEIGHTS] Top 5 minority classes:")
    sorted_w = sorted(weights.items(), key=lambda x: -x[1])
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    for idx, w in sorted_w[:5]:
        print(f"   {idx_to_class.get(idx, idx)}: {w:.3f}")
    return weights


# ─────────────────────────── Model Architecture ───────────────────────────────
def build_model(num_classes: int) -> Model:
    """
    MobileNetV2 backbone + strong classification head.
    BatchNorm in the head stabilises training when backbone is frozen.
    """
    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    # Phase 1: freeze entire backbone
    base.trainable = False

    x = base.output
    x = GlobalAveragePooling2D()(x)

    # Head: 512 → BN → Dropout → 256 → BN → Dropout → num_classes
    x = Dense(512, activation="relu")(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)

    x = Dense(256, activation="relu")(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    predictions = Dense(num_classes, activation="softmax")(x)

    return Model(inputs=base.input, outputs=predictions)


# ─────────────────────────── Callbacks ────────────────────────────────────────
def make_callbacks(phase: int) -> list:
    return [
        ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,        # more aggressive reduction
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_accuracy",
            patience=6 if phase == 1 else 8,
            restore_best_weights=True,
            verbose=1,
        ),
    ]


# ─────────────────────────── Main Training Loop ───────────────────────────────
def train():
    print(f"[INFO] Loading data from {DATASET_DIR}...")
    train_gen, val_gen = build_generators()

    if train_gen.samples == 0:
        print("[ERROR] No training images found! Please add images to datasets/train/")
        return

    num_classes = len(train_gen.class_indices)
    print(f"\n[OK] Classes  : {num_classes}")
    print(f"     Train    : {train_gen.samples} images")
    print(f"     Val      : {val_gen.samples} images")

    # Persist ordered class list for inference
    ordered_classes = [k for k, v in sorted(
        train_gen.class_indices.items(), key=lambda item: item[1]
    )]
    with open(CLASS_INDICES_PATH, "w") as f:
        json.dump(ordered_classes, f, indent=4)
    print(f"[SAVED] Class indices saved -> {CLASS_INDICES_PATH}")

    # Compute class weights for imbalanced classes
    class_weights = compute_class_weights(train_gen)

    model = None
    best_phase1_val = 0.0

    if os.path.exists(MODEL_SAVE_PATH):
        try:
            print(f"[INFO] Checking existing model at {MODEL_SAVE_PATH}...")
            temp_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
            if temp_model.output_shape[-1] == num_classes:
                print(f"[OK] Existing model output shape matches {num_classes} classes. Loading to resume Phase 2...")
                model = temp_model
                # Evaluate the loaded model on val_gen instead of assuming a
                # hardcoded accuracy from a previous, possibly different, run.
                _, best_phase1_val = model.evaluate(val_gen, verbose=0)
                print(f"[INFO] Loaded model's current val_accuracy: {best_phase1_val:.4f}")
            else:
                print(f"[WARN] Existing model has {temp_model.output_shape[-1]} classes, expected {num_classes}. Starting Phase 1 from scratch.")
        except Exception as e:
            print(f"[WARN] Failed to load existing model: {e}. Starting Phase 1 from scratch.")

    if model is None:
        # ─── Phase 1: Train head only (backbone frozen) ───────────────────────────
        print(f"\n{'='*60}")
        print(f"[PHASE 1] Head training (backbone frozen)")
        print(f"          Epochs: up to {PHASE1_EPOCHS}  |  LR: {PHASE1_LR}")
        print(f"{'='*60}")

        model = build_model(num_classes)
        model.compile(
            optimizer=Adam(learning_rate=PHASE1_LR),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary(line_length=80, print_fn=lambda x: None)  # silent summary

        history1 = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=PHASE1_EPOCHS,
            callbacks=make_callbacks(phase=1),
            class_weight=class_weights,
            verbose=1,
        )

        best_phase1_val = max(history1.history.get("val_accuracy", [0]))
        print(f"\n[RESULT] Phase 1 best val_accuracy: {best_phase1_val:.4f} ({best_phase1_val*100:.1f}%)")

    # ─── Phase 2: Fine-tune top layers of backbone ────────────────────────────
    print(f"\n{'='*60}")
    print(f"[PHASE 2] Fine-tuning backbone layers {FINE_TUNE_FROM_LAYER}+")
    print(f"          Additional epochs: up to {PHASE2_EPOCHS}  |  LR: {PHASE2_LR}")
    print(f"{'='*60}")

    # Unfreeze the backbone from FINE_TUNE_FROM_LAYER onward
    # Find the index of GlobalAveragePooling2D to identify the end of the backbone
    gap_idx = -1
    for i, layer in enumerate(model.layers):
        if isinstance(layer, GlobalAveragePooling2D):
            gap_idx = i
            break
    if gap_idx == -1:
        gap_idx = 154  # Fallback to default MobileNetV2 layer count

    # Unfreeze backbone layers
    for layer in model.layers[:gap_idx]:
        layer.trainable = True

    # Freeze the early backbone layers
    for layer in model.layers[:FINE_TUNE_FROM_LAYER]:
        layer.trainable = False

    trainable_layers = sum(1 for l in model.layers[:gap_idx] if l.trainable)
    print(f"   Trainable backbone layers: {trainable_layers} / {gap_idx}")

    # Recompile with a much smaller LR to preserve learned weights
    model.compile(
        optimizer=Adam(learning_rate=PHASE2_LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=PHASE2_EPOCHS,
        callbacks=make_callbacks(phase=2),
        class_weight=class_weights,
        verbose=1,
    )

    best_phase2_val = max(history2.history.get("val_accuracy", [0]))
    print(f"\n[RESULT] Phase 2 best val_accuracy: {best_phase2_val:.4f} ({best_phase2_val*100:.1f}%)")

    # ModelCheckpoint already saved the best weights during training
    print(f"\n[DONE] Training complete!")
    print(f"       Best val_accuracy overall: {max(best_phase1_val, best_phase2_val)*100:.1f}%")
    print(f"       Model saved -> {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    # Suppress verbose TF/CUDA logs, keep only errors
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    train()
