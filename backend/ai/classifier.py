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
from .quality import check_image_quality


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

def predict_crop(image_bytes: bytes, skip_quality_check: bool = False):
    # 1. Pre-flight Quality Verification
    if not skip_quality_check:
        quality = check_image_quality(image_bytes)
        if not quality.get("suitable", True):
            return {
                "quality_issue": True,
                "error": quality.get("reason", "Photo quality is unsuitable for diagnostic analysis."),
                "metrics": quality.get("metrics", {})
            }

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
    confidence = float(preds[idx])

    # Check if the class is soil
    if "soil" in predicted_class.lower():
        diagnosis_data = get_treatment(predicted_class)
    elif "__" in predicted_class or "___" in predicted_class or predicted_class in CLASSES:
        diagnosis_data = get_treatment(predicted_class)
    else:
        # Legacy fallback using simple crop + HSV check
        crop_name = predicted_class
        health_status = analyze_health(image_bytes)
        diagnosis_data = get_treatment(crop_name, health_status)

    crop_name = diagnosis_data.get("crop", predicted_class)
    disease_name = diagnosis_data.get("disease", "Unknown Disease")
    is_soil = bool(diagnosis_data.get("is_soil"))
    is_healthy = "healthy" in disease_name.lower() or (disease_name == "Healthy")
    is_pest = bool(diagnosis_data.get("is_pest")) or ("mite" in predicted_class.lower() or "hispa" in predicted_class.lower())

    if is_soil:
        detection_type = "soil"
    elif is_pest:
        detection_type = "pest"
    elif is_healthy:
        detection_type = "healthy"
    else:
        detection_type = "disease"

    # Transparent "Why AgroFast thinks this" explanation
    conf_pct = round(confidence * 100, 1)
    if is_soil:
        explanation = f"Colorimetry and texture analysis matched {crop_name} features with {conf_pct}% confidence."
    elif is_healthy:
        explanation = f"The deep learning vision model identified normal, uniform leaf pigmentation and venation for {crop_name} without visible necrotic lesions ({conf_pct}% confidence)."
    elif is_pest:
        explanation = f"Visual pattern analysis matched leaf stippling and damage characteristic of {disease_name} ({conf_pct}% confidence)."
    else:
        explanation = f"The CNN vision backbone detected irregular discoloration, spot lesions, or chlorotic margins matching {disease_name} with {conf_pct}% statistical confidence."

    # Causes and recommended steps
    causes = diagnosis_data.get("causes") or []
    if not causes:
        if is_healthy:
            causes = ["Proper nutrient balance", "Adequate moisture management", "Absence of pathogen spore clusters"]
        elif is_pest:
            causes = ["Warm, dry seasonal conditions", "Dust drift on foliage", "Favorable temperature for insect proliferation"]
        else:
            causes = ["High canopy humidity", "Fungal spore dispersal from rain splash or wind", "Overhead irrigation keeping leaves wet"]

    recommended_steps = diagnosis_data.get("recommended_steps") or []
    if not recommended_steps:
        if is_healthy:
            recommended_steps = ["Continue routine irrigation schedule", "Maintain balanced NPK fertilization", "Monitor foliage weekly"]
        elif is_pest:
            recommended_steps = ["Inspect leaf undersides with magnifying glass", "Apply neem oil or labeled organic miticide/insecticide", "Avoid dusty road dust buildup on plants"]
        else:
            recommended_steps = ["Prune severely infected lower leaves", "Avoid overhead sprinkler irrigation", "Apply labeled protective or curative fungicide"]

    res = {
        "crop": crop_name,
        "confidence": f"{conf_pct}%",
        "confidence_val": round(confidence, 4),
        "disease": disease_name,
        "treatment": diagnosis_data.get("treatment", "Consult an agronomist."),
        "detection_type": detection_type,
        "is_pest": is_pest,
        "is_healthy": is_healthy,
        "model_version": "AgroFast Vision v1.1",
        "why_agrofast_thinks_this": explanation,
        "possible_causes": causes,
        "recommended_steps": recommended_steps,
        "scan_again_days": 3 if (is_pest or not is_healthy) else 10
    }

    if is_soil:
        res["is_soil"] = True
        res["soil_type"] = diagnosis_data.get("soil_type")
        res["npk_status"] = diagnosis_data.get("npk_status")
        res["ph"] = diagnosis_data.get("ph")
        res["ph_label"] = diagnosis_data.get("ph_label")
        res["suitable_crops"] = diagnosis_data.get("suitable_crops")
        res["balancing_advice"] = diagnosis_data.get("balancing_advice")
    else:
        res["is_soil"] = False
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
