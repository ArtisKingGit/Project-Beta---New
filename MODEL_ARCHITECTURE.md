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

## Result & Model Versioning

- **Active Model Version**: `AgroFast Vision v1.1` (tracked in [backend/ai/model_metadata.json](backend/ai/model_metadata.json))
- **Validation accuracy**: ~91.5%
- **Classes**: 56 total classes (46 crop disease & healthy states, 7 soil types, 3 pest classifications)
- **Model Metadata Schema**:
  ```json
  {
    "model_name": "AgroFast Vision Classifier",
    "model_version": "AgroFast Vision v1.1",
    "backbone": "MobileNetV2",
    "num_classes": 56,
    "input_resolution": [224, 224, 3],
    "metrics": { "val_accuracy": 0.9149 }
  }
  ```

## Pre-flight Image Quality Check ([quality.py](backend/ai/quality.py))

Before any image is evaluated by the neural network, it passes through an automated pre-flight validator:
1. **Blur Detection**: Computes the variance of the Laplacian (`cv2.Laplacian(gray).var()`). Variance below 45 indicates severe motion or focus blur.
2. **Exposure & Lighting**: Computes mean grayscale brightness. Images with average brightness < 30 are rejected as underexposed/too dark; brightness > 235 is rejected as overexposed/blown out.
3. **Foliage Detection**: Isolates green and agricultural vegetation HSV spectrums (`[22, 35, 25]` to `[88, 255, 255]`). Images with < 4.5% foliage coverage are flagged for missing visible leaf content.
4. **Resolution Validation**: Requires a minimum dimension of 80×80 pixels.

If an image fails pre-flight validation, `/predict` returns an actionable `422 Unprocessable Entity` with farmer-friendly guidance (e.g., *"Photo is too blurry"*, *"Ensure the crop leaf fills the camera frame"*) rather than producing an ungrounded classification.

## Full Request Pipeline ([main.py](backend/main.py) `/predict`)

```
Upload photo
     │
     ▼
validate_scan_quality() (quality.py) ──▶ Fails check? ──▶ 422 with clear retake guidance
     │ Passes
     ▼
predict_crop()  (classifier.py) ───────▶ runs model once ──▶ crop, disease, detection_type, confidence,
     │                                                            why_agrofast_thinks_this, causes, next steps
     ▼
detect_disease() (detector.py)  ───────▶ PlantCV spot segmentation ──▶ affected_area_pct, severity, boxes[]
     │
     ▼
JSON response: { crop, disease, confidence, severity, affected_area_pct, detection_type,
                 treatment, why_agrofast_thinks_this, causes, next_steps, re_scan_days,
                 boxes[], model_version }
```

### Detection Types & Pest Support
- `disease`: Standard fungal/bacterial leaf infections.
- `pest`: Specifically detects classes such as `Coffee__red_spider_mite`, `Rice__hispa`, and `Tomato_Spider_mites_Two_spotted_spider_mite`, returning targeted acaricide and integrated pest management (IPM) guidance.
- `soil`: Soil texture, NPK and pH classification.
- `healthy`: Certified vigorous foliage with maintenance recommendations.

### Severity & Affected Area Localization ([detector.py](backend/ai/detector.py))
- Uses **PlantCV** and HSV thresholding to compute the exact proportion of discolored/lesioned pixels over total leaf area (`affected_area_pct`).
- Calibrated severity categories:
  - `Healthy`: 0% affected
  - `Mild`: 0% – 12% affected
  - `Moderate`: 12% – 30% affected
  - `Severe`: > 30% affected
- Note: Bounding boxes are visual indicators to guide farmer field scouting and are clearly labeled as computer vision regions of interest, not biological boundaries.

### Conversational Assistant ([main.py](backend/main.py) `/chat`)
- Powered by **Google Gemini**, with automated system prompt injection containing:
  - User's actual registered farms (size, soil type, irrigation method, NPK balance, planting dates).
  - Current live weather (temperature, humidity, precipitation).
  - Last 5 diagnostic scans and severity ratings.
  - Expense balances and budget runway.
  - Pending farm tasks and calendar dates.
  - Proactive environmental alerts.
- Answers dynamically in the farmer's chosen language (English, Swahili, Zulu, Venda, Afrikaans).

## Agronomic Intelligence APIs

In addition to vision classification, AgroFast provides deterministic decision-support endpoints:
- `POST /farms/health-score`: Multi-factor transparent scoring (0–100) based on real scan history, disease severity, soil NPK balance, irrigation adequacy, and atmospheric stress.
- `POST /farms/disease-risk`: Environmental risk modeling calculating spore germination risk from humidity, temperature, wind, rainfall, and past plot outbreaks.
- `POST /farms/irrigation-advice`: Evaluates evapotranspiration demand, soil water holding capacity, and upcoming 48-hour rainfall probability.
- `POST /farms/fertilizer-advice`: Nutrient deficiency identification comparing crop stage requirements to measured NPK percentages.
- `POST /profitability/simulate`: Economic simulator computing gross revenue, itemized input costs, net margins, and break-even points per acre.

## Known Limitations & Fixes

| # | Issue | Impact | Status |
|---|---|---|---|
| 1 | **Duplicate inference** — `/predict` called `predict_crop()` *and* `detect_disease()`, each loading redundant model copies. | 2× memory and 2× inference latency. | ✅ **Fixed** — `detect_disease()` takes pre-computed results from `predict_crop()` and only runs PlantCV spot segmentation. |
| 2 | **Error messages leaked internals** — returned raw Python exception text (`str(e)`). | Information disclosure risk. | ✅ **Fixed** — exceptions logged server-side; client receives safe generic message. |
| 3 | **No upload validation** — accepted non-images and arbitrarily large payloads. | Memory exhaustion / DoS risk. | ✅ **Fixed** — validated via magic bytes (`image/jpeg`, `image/png`, `image/webp`), capped at 10MB. |
| 4 | **Unusable Image Hallucinations** — dark, blurry, or non-leaf photos produced confident disease predictions. | Erroneous farm advice. | ✅ **Fixed** — pre-flight Laplacian blur, exposure, and foliage mask checks in `backend/ai/quality.py`. |
| 5 | **Missing Model Versioning** — client and scan history had no traceability of the model used. | Inability to audit diagnostic drift. | ✅ **Fixed** — `AgroFast Vision v1.1` and `model_metadata.json` integrated end-to-end. |
| 6 | **Pest Classifier Architecture** — previous system had no distinct handling for pest infestations. | Farmers received generic disease recommendations for mite damage. | ✅ **Fixed** — modular pest classification added for spider mites and hispa with explicit IPM protocols. |
| 7 | **MobileNetV2 preprocessing** — current weights trained with `[0, 1]` rescaling instead of `[-1, 1]`. | Transfer learning efficiency slightly reduced. | ⚠️ **Documented for Next Retraining** — inference currently mirrors training (`1/255.0`) to maintain correctness. |
| 8 | **Permissive CORS** — default wildcard CORS. | Security surface. | ✅ **Hardened** — configurable via `CORS_ALLOWED_ORIGINS` environment variable. |

