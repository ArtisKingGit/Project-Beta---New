# AgroFast Crop Scanner — Model Architecture

Source: [backend/ai/train_model.py](backend/ai/train_model.py), [backend/ai/classifier.py](backend/ai/classifier.py), [backend/ai/detector.py](backend/ai/detector.py), [backend/ai/prepare_dataset.py](backend/ai/prepare_dataset.py), [backend/ai/treatments.py](backend/ai/treatments.py), [backend/main.py](backend/main.py)

## Overview

The Crop Scanner is a CNN built with **transfer learning**: a pretrained **MobileNetV2** backbone extracts visual features, and a custom dense "head" classifies leaf photos into crop/disease categories.

## Input

| Property | Value |
|---|---|
| Image size | 224 × 224 px |
| Channels | 3 (RGB) |
| Preprocessing | Pixel values rescaled to `0–1` (divide by 255) |

## Architecture

```
Input (224, 224, 3)
        │
        ▼
MobileNetV2 backbone (ImageNet-pretrained, include_top=False)
        │
        ▼
GlobalAveragePooling2D
        │
        ▼
Dense(512, activation="relu")
        │
        ▼
BatchNormalization
        │
        ▼
Dropout(0.4)
        │
        ▼
Dense(256, activation="relu")
        │
        ▼
BatchNormalization
        │
        ▼
Dropout(0.3)
        │
        ▼
Dense(num_classes, activation="softmax")
        │
        ▼
Output: class probabilities
```

## Training Strategy — Two-Phase Fine-Tuning

### Phase 1 — Head training (backbone frozen)
- Entire MobileNetV2 backbone frozen (`base.trainable = False`)
- Only the custom head (512 → 256 → output) is trained
- Optimizer: Adam, learning rate `5e-4`
- Up to 20 epochs

### Phase 2 — Backbone fine-tuning
- Unfreezes MobileNetV2 layers from index `100` onward (top ~54 of 155 layers)
- Earlier layers (generic edge/texture detectors) stay frozen
- Recompiled with a much smaller learning rate: `5e-5`, to avoid destroying pretrained weights
- Up to 30 additional epochs

### Loss, metrics, and imbalance handling
- Loss: categorical cross-entropy
- Metric: accuracy
- **Inverse-frequency class weights** — minority classes (e.g. `Potato_healthy`) get a higher loss weight so the model doesn't ignore them:
  `weight_i = total_samples / (num_classes × count_i)`

### Data augmentation (training set only)
| Augmentation | Range |
|---|---|
| Rotation | ±30° |
| Width/height shift | ±20% |
| Shear | ±0.15 |
| Zoom | ±20% |
| Horizontal flip | Yes |
| Vertical flip | No (leaves don't appear upside-down) |
| Brightness | 0.75×–1.25× |
| Fill mode | `reflect` |

### Callbacks
- `ModelCheckpoint` — saves best model by `val_accuracy`
- `ReduceLROnPlateau` — cuts learning rate ×0.3 if `val_loss` plateaus for 3 epochs
- `EarlyStopping` — stops if `val_accuracy` plateaus (patience 6 in Phase 1, 8 in Phase 2), restores best weights

## Result

- **Validation accuracy: ~91–92%**
- Across 15 classes covering Apple, Maize, Mango, Pepper, Potato, and Tomato leaf varieties (healthy + disease states), plus soil-type classes

## Dataset Pipeline ([prepare_dataset.py](backend/ai/prepare_dataset.py))

- Merges two source datasets — **PlantVillage** and a second `archive (2)` dataset — into unified `datasets/train/` and `datasets/val/` folders, one subfolder per class.
- Caps each class at **150 training images / 30 validation images** (`TRAIN_LIMIT`, `VAL_LIMIT`) to keep training feasible on a CPU.
- Preserves any folder with "soil" in its name across cleanups (soil-type classes are curated separately, not sourced from PlantVillage/archive).
- Deletes the original source folders after merging to save disk space.

## Full Request Pipeline ([main.py](backend/main.py) `/predict`)

```
Upload photo
     │
     ▼
predict_crop()  (classifier.py) ──▶ runs the model ONCE → crop, disease, confidence, treatment
     │
     ▼
detect_disease() (detector.py)  ──▶ reuses that result; only runs PlantCV spot
     │                               segmentation to draw bounding boxes around
     │                               diseased regions (skipped for healthy/soil results)
     ▼
JSON response → crop, disease, confidence, treatment, soil info (if applicable), boxes[]
```

### Classification ([classifier.py](backend/ai/classifier.py))
1. Load `crop_model.keras` and `class_indices.json` (ordered class list) once, kept in memory.
2. Resize uploaded image to 224×224, normalize to 0–1.
3. `model.predict()` → softmax probabilities → `argmax` = predicted class, its probability = confidence.
4. Map predicted class to a diagnosis/treatment via [treatments.py](backend/ai/treatments.py) — a static lookup table covering ~58 PlantVillage/archive classes plus soil-type entries.
5. A secondary **HSV color heuristic** (`analyze_health`) acts as a legacy fallback health check — flags "Unhealthy" if yellow/brown pixels exceed thresholds relative to green pixels — used only when the predicted class isn't a recognized disease/soil label.

### Spot localization ([detector.py](backend/ai/detector.py))
- Takes the classification result from `predict_crop()` (no second model pass).
- Skips box-drawing entirely for **healthy** or **soil** results.
- For diseased results: converts to HSV, thresholds the "Value" channel to isolate dark/discolored regions (**PlantCV**), fills small holes, then finds contours with OpenCV and draws a bounding box around each region ≥ 500px².
- Falls back to a single full-image bounding box if no discrete spots are found on a diseased leaf.

### Conversational layer ([main.py](backend/main.py) `/chat`)
- Google **Gemini 2.5 Flash**, given a system prompt describing AgroFast's features and instructed to reply in the user's detected language (English, Swahili, Zulu, Venda, Afrikaans).
- The user's farms and last 5 diagnostic scans are injected into the prompt as live context, so the assistant can reference the user's actual data.

## Known Limitations & Fixes

| # | Issue | Impact | Status |
|---|---|---|---|
| 1 | **Duplicate inference** — `/predict` called `predict_crop()` *and* `detect_disease()`, and each loaded its own copy of `crop_model.keras` and ran the same 224×224 image through the model independently. | 2× memory (two full model copies in RAM) and 2× inference latency per request, for identical output. | ✅ **Fixed** — `detect_disease()` no longer loads a model or classifies; it now takes the already-computed result from `predict_crop()` and only does PlantCV box-finding. |
| 2 | **Error messages leaked internals** — `/predict` and `/chat` returned raw Python exception text (`str(e)`) to the client on failure. | Could expose file paths, library internals, or stack details to any caller — an information-disclosure risk. | ✅ **Fixed** — exceptions are logged server-side; the client now gets a generic, safe message. |
| 3 | **No upload validation** — `/predict` accepted any file of any size, with no content-type or size check before decoding. | A non-image or very large file could crash the decode step or be used to exhaust server memory/CPU (basic DoS vector). | ✅ **Fixed** — content-type is restricted to JPEG/PNG/WEBP and uploads are capped at 10MB before processing. |
| 4 | **Hardcoded "legacy" accuracy** — when resuming training from an existing checkpoint, Phase 1 accuracy was hardcoded to `0.9149` instead of measured. | If the existing checkpoint wasn't actually that accuracy (e.g. retrained differently), early-stopping/reporting logic would silently use a wrong baseline. | ✅ **Fixed** — now calls `model.evaluate(val_gen)` to get the real current accuracy. |
| 5 | **MobileNetV2 preprocessing mismatch** — training and inference rescale pixels to `0–1` via `rescale=1/255`, but the ImageNet weights `MobileNetV2` was pretrained with expect `[-1, 1]` scaling (Keras's `mobilenet_v2.preprocess_input`). | The frozen backbone (Phase 1) sees inputs in a different range than it was trained on, which can weaken the transfer-learning benefit and slightly cap achievable accuracy. | ⚠️ **Not changed** — fixing this requires retraining from scratch, since inference must always match training preprocessing. Changing `classifier.py`/`detector.py` now (without retraining) would silently corrupt predictions from the *currently deployed* model. Recommendation: switch to `preprocess_input` next time the model is retrained, and update inference preprocessing in the same commit. |
| 6 | **No held-out test set** — only `train/` and `val/` splits exist; `val_accuracy` is used for both early-stopping/checkpointing *and* as the reported accuracy figure. | The reported ~91–92% is optimistically biased — the validation set influences model selection, so it's not a fully independent measure of real-world accuracy. | ⚠️ **Not changed** — would require re-splitting the dataset (e.g. train/val/test) and retraining. Documented here as a methodology caveat. |
| 7 | **Small per-class dataset cap** (150 train / 30 val images) for CPU feasibility. | Limits how well the model generalizes, especially for visually similar diseases; higher risk of overfitting on rare classes. | ⚠️ **Not changed** — a deliberate CPU-time/accuracy trade-off. Raising the cap (and training on GPU) would likely improve accuracy further. |
| 8 | **Permissive CORS** (`allow_origins=["*"]`) on the FastAPI app, even though the same app already serves the frontend itself (same-origin). | Any external website could call `/predict` or the Gemini-backed `/chat` endpoint directly, potentially running up Gemini API costs or hammering the ML endpoint. | ⚠️ **Not changed** — tightening this could break an existing dev setup (e.g. frontend opened via a separate local server/port). Recommendation: restrict `allow_origins` to the app's actual deployed origin(s) once the deployment setup is finalized. |
