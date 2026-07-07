# pyrefly: ignore [missing-import]
import os
import json
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
import tensorflow as tf
# pyrefly: ignore [missing-import]
import keras
import io
# pyrefly: ignore [missing-import]
import cv2
from .treatments import get_treatment, CROP_SOIL_REQUIREMENTS

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "crop_model.keras")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "class_indices.json")

# Global variables
model = None
CLASSES = []

def load_classes():
    """Loads class mapping dynamically from JSON file or falls back to legacy classes."""
    global CLASSES
    if not CLASSES:
        if os.path.exists(CLASS_INDICES_PATH):
            try:
                with open(CLASS_INDICES_PATH, "r") as f:
                    CLASSES = json.load(f)
                print(f"Loaded {len(CLASSES)} classes dynamically from {CLASS_INDICES_PATH}.")
            except Exception as e:
                print(f"Error loading class indices from JSON: {e}")
                CLASSES = ["coffee", "maize", "potato", "rice", "tomato", "wheat"]
        else:
            print("class_indices.json not found. Falling back to legacy classes.")
            CLASSES = ["coffee", "maize", "potato", "rice", "tomato", "wheat"]

def load_ai_model():
    """Loads the compiled keras model from disk."""
    global model
    load_classes()
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
        print(f"Loading model from {MODEL_PATH}...")
        model = keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully.")

def analyze_health(image_bytes):
    """
    Scans image for discoloration using HSV color analysis.
    Returns: health_status ("Healthy" or "Unhealthy")
    """
    try:
        # Convert bytes to opencv format
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return "Healthy"
            
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define Healthy Green Range
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Define Unhealthy Yellow/Brown Range
        lower_yellow = np.array([15, 40, 40])
        upper_yellow = np.array([35, 255, 255])

        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        green_pixels = cv2.countNonZero(green_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        total_pixels = img.shape[0] * img.shape[1]

        # Heuristic: If unhealthy pixels represent more than 5% of total, or 
        # if yellow/brown pixels are more than 30% of green pixels.
        if yellow_pixels > (total_pixels * 0.05) or (green_pixels > 0 and yellow_pixels / green_pixels > 0.3):
            return "Unhealthy"
    except Exception as e:
        print(f"Error in analyze_health HSV check: {e}")
    
    return "Healthy"

def predict_crop(image_bytes):
    # Ensure model and classes are loaded
    load_ai_model()

    # AI Prediction for Crop/Disease type
    img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_pil = img_pil.resize((224, 224))
    arr = np.array(img_pil) / 255.0
    arr = np.expand_dims(arr, axis=0)

    preds = model.predict(arr)[0]
    idx = np.argmax(preds)
    predicted_class = CLASSES[idx]
    confidence = preds[idx]

    # Check if the class is soil
    if "soil" in predicted_class.lower():
        # Soil scan lookup
        diagnosis_data = get_treatment(predicted_class)
    # Check if the class is one of the trained classes
    elif "__" in predicted_class or "___" in predicted_class or predicted_class in CLASSES:
        # Use direct class mapping
        diagnosis_data = get_treatment(predicted_class)
    else:
        # Legacy fallback using simple crop + HSV check
        crop_name = predicted_class
        health_status = analyze_health(image_bytes)
        diagnosis_data = get_treatment(crop_name, health_status)

    res = {
        "crop": diagnosis_data.get("crop", predicted_class),
        "confidence": f"{confidence*100:.2f}%",
        "disease": diagnosis_data.get("disease", "Unknown Disease"),
        "treatment": diagnosis_data.get("treatment", "Consult an agronomist.")
    }

    if diagnosis_data.get("is_soil"):
        res["is_soil"] = True
        res["soil_type"] = diagnosis_data.get("soil_type")
        res["npk_status"] = diagnosis_data.get("npk_status")
        res["ph"] = diagnosis_data.get("ph")
        res["ph_label"] = diagnosis_data.get("ph_label")
        res["suitable_crops"] = diagnosis_data.get("suitable_crops")
        res["balancing_advice"] = diagnosis_data.get("balancing_advice")
    else:
        res["is_soil"] = False
        # Add crop-specific soil requirements
        crop_name = res["crop"]
        reqs = None
        for key, req_val in CROP_SOIL_REQUIREMENTS.items():
            if key.lower() in crop_name.lower() or crop_name.lower() in key.lower():
                reqs = req_val
                break
        if reqs:
            res["soil_requirements"] = reqs

    return res

# Initialize on import
try:
    load_ai_model()
except Exception as e:
    print(f"Warning: Model could not be loaded on import: {e}")
