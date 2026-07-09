# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, JSONResponse
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
import uvicorn
import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from ai.classifier import predict_crop
from ai.detector import detect_disease
 
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


app = FastAPI()

from typing import List, Optional, Any

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    scans: Optional[List[Any]] = None
    farms: Optional[List[Any]] = None

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    print(f"Received image: {image.filename} ({image.content_type})")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type. Please upload a JPEG, PNG, or WEBP image."})

    image_bytes = await image.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return JSONResponse(status_code=400, content={"error": "Image is too large. Maximum size is 10MB."})

    try:
        # Get AI classification and health summary (runs the model once)
        result = predict_crop(image_bytes)

        # Get detailed "Real Scanning" data (bounding boxes for spots),
        # reusing the classification above instead of re-running the model
        detection = detect_disease(image_bytes, result)

        # Merge results
        result["boxes"] = detection.get("boxes", [])

        return result
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        # Don't leak internal exception details to the client
        return JSONResponse(status_code=500, content={"error": "Could not analyze this image. Please try a different photo."})

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Gemini API Key is not configured. Please add GEMINI_API_KEY to your backend/.env file."})
    
    try:
        system_instruction = (
            "You are an expert agricultural AI assistant named Farmly. "
            "Provide helpful, accurate, brief, and highly effective advice to farmers regarding crops, diseases, pests, and farm management. "
            "CRITICAL: Always detect the language of the user's query and respond in that exact language (the application supports and translates to English, Swahili, Zulu, Venda, and Afrikaans). "
            "Keep your responses concise, direct, action-oriented, and easy to read. Avoid long paragraphs; use brief bullet points or short sentences. "
            "Base your answers on best farming practices. Format your responses using Markdown for better readability.\n\n"
            "You also have comprehensive knowledge about AgroFast (this application) and can explain its features to users if they ask. "
            "Key features of AgroFast (the app you power as Farmly) include:\n"
            "1. **Smart Auth**: Secure registration and login using Firebase, with customized farm profiles.\n"
            "2. **Manage Farms**: Add, edit, or delete multiple farm plots, specifying soil type, irrigation type, water source, planting dates, and soil nutrients (NPK % values) which can be updated live from the cards.\n"
            "3. **AI Leaf Diagnostics (AI Scanner / Crop Scanner)**: Scan crop leaf photos to detect diseases. It runs on a trained convolutional neural network (achieving a validation accuracy of 91% across 58 agricultural classes, covering apple, pepper, maize, mango, potato, tomato, coffee, cassava, rice, tea, and wheat leaf categories).\n"
            "4. **Smart Crop Recommendations Engine**: Auto-detects location via GPS to fetch live temperature, humidity, wind, and feels-like temperature (using Open-Meteo). Predicts month-by-month profitability based on a custom scoring algorithm: 40% Weather Fit (compares crop requirements with monthly forecasts) and 60% Revenue Score (based on market price and yield per acre).\n"
            "5. **Expense Tracker & Budget Safety**: Record and track farm expenses by category (e.g. Seeds, Fertilizer, Labor) for each farm plot. Displays visual color-coded budget progress meters (green to yellow to red) and has a Budget Warning System that cautions users when an expense exceeds their budget, suggesting a safe budget buffer.\n"
            "6. **User Interface & UX**: Sleek, modern, and dark-mode interface, featuring multi-language translations (dynamic translations file) and an interactive step-by-step tour tutorial guide."
        )

        # Inject real-time user context (farms and scans) to make the assistant "remember" them
        context_parts = []
        if request.farms:
            farms_desc = "\nHere are the user's farms that they currently manage:\n"
            for f in request.farms:
                name = f.get('name', 'Unnamed Plot')
                crop = f.get('crop', 'None')
                size = f.get('size', 'Unknown')
                soil = f.get('soil', 'Unknown')
                irrigation = f.get('irrigation', 'Unknown')
                farms_desc += f"- Plot Name: {name}, Main Crop: {crop}, Size: {size} acres, Soil: {soil}, Irrigation: {irrigation}\n"
            context_parts.append(farms_desc)

        if request.scans:
            scans_desc = "\nHere are the user's recent crop diagnostic scan records:\n"
            # Take last 5 scans to avoid context bloat
            recent_scans = request.scans[-5:]
            for s in recent_scans:
                crop_name = s.get('crop', 'Unknown Crop')
                disease = s.get('disease', 'Healthy')
                time_val = s.get('time', 'Unknown Time')
                confidence = s.get('confidence', '100%')
                scans_desc += f"- Scanned {crop_name}: result was '{disease}' with {confidence} confidence (date: {time_val})\n"
            context_parts.append(scans_desc)

        if context_parts:
            system_instruction += "\n\n### USER REAL-TIME CONTEXT (REMEMBERED FARMS AND SCANS):\n" + "\n".join(context_parts)

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
        
        # Format the chat history into the structure expected by the Gemini SDK
        history = []
        if request.history:
            for msg in request.history:
                role = "user" if msg.role == "user" else "model"
                history.append({
                    "role": role,
                    "parts": [msg.content]
                })
        
        chat = model.start_chat(history=history)
        response = chat.send_message(request.message)
        return {"response": response.text}
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "The AI assistant is temporarily unavailable. Please try again."})

# Serve Static Files (only present when running alongside the frontend locally;
# a backend-only deploy, e.g. a Docker/cloud host, won't have this directory)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(frontend_path):
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_path, "login.html"))

    # Mount frontend at root BUT after specific API routes to ensure they take precedence
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    async def read_index():
        return {"status": "AgroFast backend is running"}

if __name__ == "__main__":
    # HOST/PORT are set by cloud hosts (e.g. Hugging Face Spaces needs 0.0.0.0:7860);
    # defaults to 127.0.0.1:5500 locally to match the dashboard's compatibility checks.
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5500))
    uvicorn.run(app, host=host, port=port)
