import os
import shutil
import random

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

# Target directories
TRAIN_DIR = os.path.join(DATASETS_DIR, "train")
VAL_DIR = os.path.join(DATASETS_DIR, "val")

# Source directories to merge
PV_SRC_TRAIN = os.path.join(DATASETS_DIR, "PlantVillage", "train")
PV_SRC_VAL = os.path.join(DATASETS_DIR, "PlantVillage", "val")
ARCHIVE_SRC_TRAIN = os.path.join(DATASETS_DIR, "archive (2)", "Train")
ARCHIVE_SRC_VAL = os.path.join(DATASETS_DIR, "archive (2)", "Validation")

# Capping limits for balanced training on CPU
TRAIN_LIMIT = 150
VAL_LIMIT = 30

def clean_directory(directory):
    """Deletes all folders and files inside a directory, preserving Soil datasets."""
    if os.path.exists(directory):
        print(f"Cleaning directory: {directory}")
        for item in os.listdir(directory):
            if "soil" in item.lower():
                print(f"Preserving soil directory: {item}")
                continue
            item_path = os.path.join(directory, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Failed to delete {item_path}: {e}")
    else:
        os.makedirs(directory, exist_ok=True)

def copy_class_data(src_dir, dest_dir, limit):
    """Copies subfolders and files from src_dir to dest_dir up to a limit per folder."""
    if not os.path.exists(src_dir):
        print(f"Source directory not found: {src_dir}")
        return

    classes = sorted([d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))])
    print(f"Merging {len(classes)} classes from {src_dir} into {dest_dir}...")

    for idx, class_name in enumerate(classes):
        src_class_path = os.path.join(src_dir, class_name)
        dest_class_path = os.path.join(dest_dir, class_name)
        os.makedirs(dest_class_path, exist_ok=True)

        # Get all image files
        images = [f for f in os.listdir(src_class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        random.shuffle(images)

        # Apply limits
        if limit is not None:
            images = images[:limit]

        # Copy images
        for img in images:
            shutil.copy2(os.path.join(src_class_path, img), os.path.join(dest_class_path, img))
        
        print(f"  [{idx+1}/{len(classes)}] Class '{class_name}': Copied {len(images)} images")

def cleanup_source_directories():
    """Deletes the source directories added by the user after successful copy."""
    folders_to_delete = [
        os.path.join(DATASETS_DIR, "PlantVillage"),
        os.path.join(DATASETS_DIR, "archive (2)")
    ]
    for folder in folders_to_delete:
        if os.path.exists(folder):
            print(f"Deleting source directory: {folder}")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Failed to delete folder {folder}: {e}")

def prepare_data():
    random.seed(42)

    # 1. Clean the target directories
    clean_directory(TRAIN_DIR)
    clean_directory(VAL_DIR)

    # 2. Copy and merge PlantVillage images
    print("\n--- Merging PlantVillage Dataset ---")
    copy_class_data(PV_SRC_TRAIN, TRAIN_DIR, TRAIN_LIMIT)
    copy_class_data(PV_SRC_VAL, VAL_DIR, VAL_LIMIT)

    # 3. Copy and merge archive (2) dataset
    print("\n--- Merging archive (2) Dataset ---")
    copy_class_data(ARCHIVE_SRC_TRAIN, TRAIN_DIR, TRAIN_LIMIT)
    copy_class_data(ARCHIVE_SRC_VAL, VAL_DIR, VAL_LIMIT)

    # 4. Clean up source folders
    print("\n--- Cleaning up temporary source directories ---")
    cleanup_source_directories()

    print("\nAll datasets merged and source directories cleaned up successfully!")

if __name__ == "__main__":
    prepare_data()
