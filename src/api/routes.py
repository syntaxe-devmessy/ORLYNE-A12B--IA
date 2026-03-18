"""
API REST pour Orlyne
"""

from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from pathlib import Path

from src.core.engine import OrlyneEngine

# Modèles Pydantic
class ChatRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 2048
    temperature: Optional[float] = 0.7

class CodeRequest(BaseModel):
    code: str
    language: str
    timeout: Optional[int] = 30

def create_app(engine: OrlyneEngine) -> FastAPI:
    """Crée l'application FastAPI"""
    
    app = FastAPI(
        title="ORLYNE-A12B API",
        description="API de l'assistant IA Orlyne",
        version="1.0.0"
    )
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Montage des fichiers statiques
    static_path = Path(__file__).parent.parent / "web" / "static"
    templates_path = Path(__file__).parent.parent / "web" / "templates"
    
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    templates = Jinja2Templates(directory=str(templates_path))
    
    @app.get("/")
    async def root(request: Request):
        """Page d'accueil"""
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "name": engine.personality.name}
        )
    
    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Endpoint de chat"""
        try:
            response = engine.generate_response(
                request.prompt,
                max_length=request.max_length,
                temperature=request.temperature
            )
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/code/execute")
    async def execute_code(request: CodeRequest):
        """Endpoint d'exécution de code"""
        try:
            result = engine.execute_code(request.code, request.language)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/languages")
    async def get_languages():
        """Liste des langages supportés"""
        return {
            "languages": list(engine.code_executor.executors.keys())
        }
    
    @app.get("/status")
    async def get_status():
        """Statut du moteur"""
        return {
            "name": engine.personality.name,
            "version": engine.personality.version,
            "model": engine.model_name,
            "device": engine.device,
            "mood": engine.personality.current_mood,
            "energy": engine.personality.energy_level
        }
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket pour chat en temps réel"""
        await websocket.accept()
        try:
            while True:
                # Réception du message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Génération de la réponse
                response = engine.generate_response(
                    message.get("prompt", ""),
                    max_length=message.get("max_length", 2048)
                )
                
                # Envoi de la réponse
                await websocket.send_json(response)
                
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await websocket.close()
    
    return app