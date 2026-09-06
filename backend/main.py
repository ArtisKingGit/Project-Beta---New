# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, JSONResponse
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
# pyrefly: ignore [missing-import]
import uvicorn
import os
import json
import asyncio
from typing import List, Optional, Any, Dict
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.classifier import predict_crop
from ai.detector import detect_disease
from intelligence import (

    calculate_farm_health_score,
    calculate_disease_risk,
    calculate_irrigation_advice,
    calculate_fertilizer_advice,
    simulate_crop_profit
)

# Force IPv4-only DNS resolution for outbound calls (HF Spaces / cloud containers)
import socket
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_only_getaddrinfo

# Avoid probing GCP metadata server on non-GCP hosts
os.environ.setdefault("NO_GCE_CHECK", "true")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def _clean_api_key(raw):
    """Tolerate whitespace, surrounding quotes, or accidental GEMINI_API_KEY= prefix."""
    if not raw:
        return raw
    key = raw.strip().strip('"').strip("'").strip()
    if key.startswith("GEMINI_API_KEY="):
        key = key.split("=", 1)[1].strip().strip('"').strip("'").strip()
    return key

GEMINI_API_KEY = _clean_api_key(os.getenv("GEMINI_API_KEY"))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY, transport="rest")

GEMINI_TIMEOUT_SECONDS = 20

app = FastAPI(
    title="AgroFast Unified Intelligence API",
    description="Intelligent Farm Management Backend: Crop Disease & Pest Vision, Agronomic Decision Support, Weather Intelligence, and Farmly Assistant",
    version="1.1.0"
)

# -------------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    scans: Optional[List[Any]] = None
    farms: Optional[List[Any]] = None
    expenses: Optional[List[Any]] = None
    tasks: Optional[List[Any]] = None
    weather: Optional[Dict[str, Any]] = None
    alerts: Optional[List[Any]] = None

class FarmHealthRequest(BaseModel):
    farm: Dict[str, Any]
    recent_scans: Optional[List[Dict[str, Any]]] = None
    weather: Optional[Dict[str, Any]] = None
    expenses: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None

class DiseaseRiskRequest(BaseModel):
    crop: str
    weather: Dict[str, Any]
    recent_scans: Optional[List[Dict[str, Any]]] = None
    farm_id: Optional[str] = None

class IrrigationAdviceRequest(BaseModel):
    farm: Dict[str, Any]
    weather: Dict[str, Any]
    forecast_rain_mm: Optional[float] = 0.0

class FertilizerAdviceRequest(BaseModel):
    farm: Dict[str, Any]

class ProfitSimulateRequest(BaseModel):
    farm_size: float = Field(default=1.0, ge=0.01)
    crop_name: str
    yield_per_acre: Optional[float] = None
    market_price_per_unit: Optional[float] = None
    seed_cost: Optional[float] = None
    fertilizer_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    irrigation_cost: Optional[float] = None
    other_cost: Optional[float] = None

# -------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@app.get("/model-info")
async def model_info():
    """Returns AI model version, training metrics, architecture, and pest detection specs."""
    meta_path = os.path.join(os.path.dirname(__file__), "ai", "model_metadata.json")
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "model_name": "AgroFast Vision",
        "model_version": "v1.1",
        "architecture": "MobileNetV2 Transfer Learning + Custom Dense Head",
        "total_classes": 58
    }

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    """
    Classifies crop leaf photos or soil types.
    Performs pre-flight image quality checks (blur, lighting, leaf presence),
    detects disease vs pest vs healthy, computes spot bounding boxes, and returns
    severity rating, affected area %, treatment guidance, and transparent explanations.
    """
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type. Please upload a JPEG, PNG, or WEBP image."})

    image_bytes = await image.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return JSONResponse(status_code=400, content={"error": "Image is too large. Maximum size is 10MB."})

    # Magic Bytes Validation
    is_jpeg = image_bytes.startswith(b"\xff\xd8\xff")
    is_png = image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = len(image_bytes) > 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP"
    if not (is_jpeg or is_png or is_webp):
        return JSONResponse(status_code=400, content={"error": "Invalid image file signature. Please upload an authentic photo."})

    try:
        # 1. Run classifier (includes pre-flight quality verification)
        result = predict_crop(image_bytes)

        # Handle quality rejection
        if result.get("quality_issue"):
            return JSONResponse(status_code=422, content={
                "error": result.get("error", "Photo quality is unsuitable for analysis."),
                "quality_issue": True,
                "metrics": result.get("metrics", {})
            })

        # 2. Run detector for bounding boxes, severity, and affected area %
        detection = detect_disease(image_bytes, result)

        # Merge results
        result["boxes"] = detection.get("boxes", [])
        result["affected_area_pct"] = detection.get("affected_area_pct", 0.0)
        result["severity"] = detection.get("severity", "Healthy" if result.get("is_healthy") else "Mild")

        return result
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not analyze this image. Please take another clear photo with good lighting."})

@app.post("/farms/health-score")
async def farm_health_score_endpoint(request: FarmHealthRequest):
    """Calculates a transparent 0-100 Farm Health Score from actual farm data."""
    try:
        score_data = calculate_farm_health_score(
            farm=request.farm,
            recent_scans=request.recent_scans,
            weather=request.weather,
            expenses=request.expenses,
            tasks=request.tasks
        )
        return score_data
    except Exception as e:
        print(f"Error calculating health score: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not calculate farm health score."})

@app.post("/farms/disease-risk")
async def disease_risk_endpoint(request: DiseaseRiskRequest):
    """Calculates environmental disease risk from atmospheric data and scan history."""
    try:
        risk_data = calculate_disease_risk(
            crop_name=request.crop,
            weather=request.weather,
            recent_scans=request.recent_scans,
            farm_id=request.farm_id
        )
        return risk_data
    except Exception as e:
        print(f"Error calculating disease risk: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not calculate disease risk."})

@app.post("/farms/irrigation-advice")
async def irrigation_advice_endpoint(request: IrrigationAdviceRequest):
    """Recommends actionable irrigation window and water requirements."""
    try:
        advice = calculate_irrigation_advice(
            farm=request.farm,
            weather=request.weather,
            forecast_rain_mm=request.forecast_rain_mm or 0.0
        )
        return advice
    except Exception as e:
        print(f"Error calculating irrigation advice: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not calculate irrigation advice."})

@app.post("/farms/fertilizer-advice")
async def fertilizer_advice_endpoint(request: FertilizerAdviceRequest):
    """Identifies NPK nutrient risks and decision support."""
    try:
        advice = calculate_fertilizer_advice(farm=request.farm)
        return advice
    except Exception as e:
        print(f"Error calculating fertilizer advice: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not calculate fertilizer advice."})

@app.post("/profitability/simulate")
async def profit_simulate_endpoint(request: ProfitSimulateRequest):
    """Simulates crop revenues, costs, profits, and multi-crop comparisons."""
    try:
        simulation = simulate_crop_profit(
            farm_size=request.farm_size,
            crop_name=request.crop_name,
            yield_per_acre=request.yield_per_acre,
            market_price_per_unit=request.market_price_per_unit,
            seed_cost=request.seed_cost,
            fertilizer_cost=request.fertilizer_cost,
            labor_cost=request.labor_cost,
            irrigation_cost=request.irrigation_cost,
            other_cost=request.other_cost
        )
        return simulation
    except Exception as e:
        print(f"Error simulating profit: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Could not simulate profitability."})

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Farmly AI assistant endpoint with live context injection."""
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Gemini API Key is not configured. Please add GEMINI_API_KEY to your backend/.env file."})

    try:
        system_instruction = (
            "You are an expert agricultural AI assistant named Farmly inside AgroFast. "
            "Provide helpful, accurate, brief, and highly actionable advice to farmers regarding crops, diseases, pests, irrigation, soil health, and farm management. "
            "CRITICAL: Always detect the language of the user's query and respond in that exact language (AgroFast supports English, Swahili, Zulu, Venda, and Afrikaans). "
            "Keep your responses concise, direct, action-oriented, and easy to read. Use bullet points and short paragraphs. "
            "CRITICAL: Base your answers on the user's actual AgroFast farm and crop data provided below. If a user asks about their farm (e.g. 'How is my maize doing?'), refer directly to their actual plots, scan history, health scores, or weather. Do NOT hallucinate farm details. If information is unavailable, politely state what is missing."
        )

        context_parts = []

        # 1. User Farms
        if request.farms:
            farms_desc = "\n### USER'S REGISTERED FARMS:\n"
            for f in request.farms:
                name = f.get('name', 'Plot')
                crop = f.get('crop', 'None')
                size = f.get('size', 'Unknown')
                loc = f.get('location', 'Unknown')
                irrig = f.get('irrigation', 'Unknown')
                soil_info = f.get('soil', {})
                n = soil_info.get('n', 'N/A')
                p = soil_info.get('p', 'N/A')
                k = soil_info.get('k', 'N/A')
                p_date = f.get('plantingDate', 'Unknown')
                budget = f.get('budget', 'None')
                farms_desc += f"- Farm: {name} | Crop: {crop} | Size: {size} acres | Location: {loc} | Irrigation: {irrig} | Soil NPK: N={n}%, P={p}%, K={k}% | Planting Date: {p_date} | Budget: {budget}\n"
            context_parts.append(farms_desc)

        # 2. Live Weather
        if request.weather:
            w = request.weather
            temp = w.get('temp', 'N/A')
            hum = w.get('humidity', 'N/A')
            precip = w.get('precipitation', 0)
            desc = w.get('description', 'Normal')
            w_desc = f"\n### CURRENT LIVE WEATHER:\n- Conditions: {desc}, Temp: {temp}°C, Humidity: {hum}%, Rainfall: {precip}mm\n"
            context_parts.append(w_desc)

        # 3. Diagnostic Scans
        if request.scans:
            scans_desc = "\n### RECENT CROP SCANS & DIAGNOSES (Latest 5):\n"
            for s in request.scans[-5:]:
                c = s.get('crop', 'Crop')
                d = s.get('disease', 'Healthy')
                conf = s.get('confidence', '100%')
                t = s.get('time', 'Recently')
                sev = s.get('severity', 'Normal')
                scans_desc += f"- {c}: Diagnosis '{d}' ({conf} confidence, Severity: {sev}, Date: {t})\n"
            context_parts.append(scans_desc)

        # 4. Expenses & Budgets
        if request.expenses:
            total_spent = sum(float(e.get('amount') or 0) for e in request.expenses)
            exp_desc = f"\n### FINANCIAL STATUS:\n- Total recorded expenses: {round(total_spent):,} ({len(request.expenses)} transactions recorded)\n"
            context_parts.append(exp_desc)

        # 5. Tasks & Calendar
        if request.tasks:
            pending = [t for t in request.tasks if not t.get('completed')]
            tasks_desc = f"\n### FARMING TASKS ({len(pending)} pending):\n"
            for t in pending[:4]:
                title = t.get('title', 'Task')
                pri = t.get('priority', 'Normal')
                date = t.get('date', 'Upcoming')
                tasks_desc += f"- {title} (Due: {date}, Priority: {pri})\n"
            context_parts.append(tasks_desc)

        # 6. Active Alerts
        if request.alerts:
            alerts_desc = "\n### ACTIVE PROACTIVE ALERTS:\n"
            for a in request.alerts[:3]:
                title = a.get('title', 'Alert')
                msg = a.get('message', '')
                alerts_desc += f"- [{a.get('type', 'Warning').upper()}] {title}: {msg}\n"
            context_parts.append(alerts_desc)

        if context_parts:
            system_instruction += "\n\n" + "".join(context_parts)

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

        history = []
        if request.history:
            for msg in request.history:
                role = "user" if msg.role == "user" else "model"
                history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        chat = model.start_chat(history=history)

        def _call_gemini():
            return chat.send_message(
                request.message,
                request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
            )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_call_gemini),
                timeout=GEMINI_TIMEOUT_SECONDS + 5,
            )
        except asyncio.TimeoutError:
            return JSONResponse(status_code=504, content={"error": "Farmly timed out. Please try again."})

        return {"response": response.text}
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Farmly is temporarily unavailable. Please try again shortly."})

# -------------------------------------------------------------
# Static File Serving (Frontend)
# -------------------------------------------------------------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(frontend_path):
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_path, "login.html"))

    @app.get("/{page_name}")
    async def read_page(page_name: str):
        target = os.path.join(frontend_path, page_name)
        if os.path.isfile(target):
            return FileResponse(target)
        if not page_name.endswith(".html"):
            target_html = os.path.join(frontend_path, f"{page_name}.html")
            if os.path.isfile(target_html):
                return FileResponse(target_html)
        return FileResponse(os.path.join(frontend_path, "login.html"))

    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    async def read_index():
        return {"status": "AgroFast backend is running"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5500))
    uvicorn.run(app, host=host, port=port)
