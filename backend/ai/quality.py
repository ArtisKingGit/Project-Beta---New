"""
Pre-flight scan quality analyzer for AgroFast Crop Scanner.
Detects images that are too blurry, too dark, overexposed, or lack visible plant/soil subject matter
before feeding them to the deep learning classifier.
"""

import cv2
import numpy as np
from PIL import Image
import io

def check_image_quality(image_bytes: bytes) -> dict:
    """
    Analyzes an uploaded image for diagnostic suitability.
    Returns:
        {
            "suitable": bool,
            "reason": str or None,
            "metrics": {
                "blur_score": float,
                "brightness": float,
                "foliage_ratio": float,
                "width": int,
                "height": int
            }
        }
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "suitable": False,
                "reason": "Invalid or unreadable image format. Please upload a standard JPEG, PNG, or WEBP photo.",
                "metrics": {}
            }

        height, width = img.shape[:2]

        # 1. Dimension Check
        if width < 100 or height < 100:
            return {
                "suitable": False,
                "reason": f"Image resolution is too low ({width}x{height}px). Minimum recommended size is 120x120px for reliable diagnosis.",
                "metrics": {"width": width, "height": height}
            }

        # Convert to Grayscale for Blur & Brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Brightness Check
        brightness = float(np.mean(gray))
        if brightness < 35.0:
            return {
                "suitable": False,
                "reason": "Image is too dark. Please take another photo with better lighting or flash so leaf details are visible.",
                "metrics": {"brightness": round(brightness, 1), "width": width, "height": height}
            }
        if brightness > 240.0:
            return {
                "suitable": False,
                "reason": "Image is heavily overexposed or washed out. Please shade the leaf or avoid direct flash reflection.",
                "metrics": {"brightness": round(brightness, 1), "width": width, "height": height}
            }

        # 3. Blur Check (Variance of Laplacian)
        # Higher score = sharper; lower score = blurrier
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        # For small images or very smoothed photos, < 35 is reliably blurry
        if laplacian_var < 35.0:
            return {
                "suitable": False,
                "reason": "Image is too blurry. Please hold camera steady, tap to focus on the leaf, and retake the photo.",
                "metrics": {
                    "blur_score": round(laplacian_var, 1),
                    "brightness": round(brightness, 1),
                    "width": width,
                    "height": height
                }
            }

        # 4. Foliage / Soil Content Check
        # Check if the photo contains organic plant or soil colors (green, yellow, brown, red-brown)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Green foliage
        mask_green = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([90, 255, 255]))
        # Yellow/brown/soil tones
        mask_brown = cv2.inRange(hsv, np.array([8, 25, 25]), np.array([25, 255, 220]))
        # Combine
        combined_mask = cv2.bitwise_or(mask_green, mask_brown)
        organic_pixels = cv2.countNonZero(combined_mask)
        total_pixels = width * height
        foliage_ratio = organic_pixels / float(total_pixels)

        # If less than 3% organic/plant/soil pixels, it's likely a non-agricultural photo (e.g. keyboard, car, wall)
        if foliage_ratio < 0.03:
            return {
                "suitable": False,
                "reason": "No clear crop leaf or soil detected in this photo. Please ensure the plant leaf fills most of the frame.",
                "metrics": {
                    "foliage_ratio": round(foliage_ratio, 3),
                    "blur_score": round(laplacian_var, 1),
                    "brightness": round(brightness, 1)
                }
            }

        return {
            "suitable": True,
            "reason": None,
            "metrics": {
                "blur_score": round(laplacian_var, 1),
                "brightness": round(brightness, 1),
                "foliage_ratio": round(foliage_ratio, 3),
                "width": width,
                "height": height
            }
        }

    except Exception as e:
        # Fallback to permissive if cv2 check encounters unexpected error
        return {
            "suitable": True,
            "reason": None,
            "metrics": {"error": str(e)}
        }
