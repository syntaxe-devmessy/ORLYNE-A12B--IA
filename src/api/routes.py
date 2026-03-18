"""
Routes API pour Orlyne
"""

from fastapi import FastAPI, HTTPException, WebSocket, Request, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import asyncio
from pathlib import Path
import uuid

from src.core.engine import OrlyneEngine
from src.api.middlewares import setup_middlewares
from src.api.websocket import WebSocketManager
from src.api.rate_limiter import RateLimiter

# Modèles Pydantic
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="Message de l'utilisateur")
    max_length: Optional[int] = Field(2048, description="Longueur max de la réponse")
    temperature: Optional[float] = Field(0.7, description="Température de génération")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte additionnel")

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    personality_used: bool
    processing_time: float
    emotion: Optional[str] = None

class CodeRequest(BaseModel):
    code: str = Field(..., description="Code à exécuter")
    language: str = Field(..., description="Langage de programmation")
    timeout: Optional[int] = Field(30, description="Timeout en secondes")

class CodeResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    language: str
    execution_time: float

class FeedbackRequest(BaseModel):
    prompt: str
    response: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    user_id: Optional[str] = None

class TranslateRequest(BaseModel):
    code: str
    from_language: str
    to_language: str

class AnalyzeRequest(BaseModel):
    code: str
    language: str
    analysis_type: Optional[str] = "full"

def create_app(engine: OrlyneEngine) -> FastAPI:
    """Crée l'application FastAPI"""
    
    app = FastAPI(
        title="ORLYNE-A12B API",
        description="API de l'assistant IA Orlyne - Sans censure, amicale et codeuse",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup des middlewares
    setup_middlewares(app)
    
    # Gestionnaire WebSocket
    ws_manager = WebSocketManager()
    
    # Rate limiter
    rate_limiter = RateLimiter()
    
    # Templates
    templates_path = Path(__file__).parent.parent / "web" / "templates"
    templates = Jinja2Templates(directory=str(templates_path))
    
    # Fichiers statiques
    static_path = Path(__file__).parent.parent / "web" / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Routes Web
    @app.get("/")
    async def root(request: Request):
        """Page d'accueil"""
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "name": engine.personality.name,
                "version": engine.personality.version
            }
        )
    
    @app.get("/chat")
    async def chat_page(request: Request):
        """Page de chat"""
        return templates.TemplateResponse(
            "chat.html",
            {
                "request": request,
                "name": engine.personality.name
            }
        )
    
    @app.get("/code")
    async def code_page(request: Request):
        """Page d'exécution de code"""
        return templates.TemplateResponse(
            "code.html",
            {
                "request": request,
                "languages": list(engine.code_executor.executors.keys())
            }
        )
    
    # Routes API
    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Endpoint de chat principal"""
        # Rate limiting
        client_id = request.headers.get("X-Client-ID", "anonymous")
        if not rate_limiter.check(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        import time
        start_time = time.time()
        
        try:
            # Génération de la réponse
            result = engine.generate_response(
                request.prompt,
                max_length=request.max_length,
                temperature=request.temperature,
                context=request.context
            )
            
            processing_time = time.time() - start_time
            
            # Récupération de l'émotion actuelle
            emotion = engine.personality.current_emotion.get("primary", "neutre")
            
            return ChatResponse(
                response=result["response"],
                model=result["model"],
                tokens_used=result.get("tokens_used", 0),
                personality_used=result.get("personality_used", True),
                processing_time=processing_time,
                emotion=emotion
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/execute", response_model=CodeResponse)
    async def execute_code(request: CodeRequest):
        """Exécute du code"""
        import time
        start_time = time.time()
        
        try:
            result = engine.execute_code(request.code, request.language, request.timeout)
            
            execution_time = time.time() - start_time
            
            return CodeResponse(
                success=result.get("success", False),
                output=result.get("output"),
                error=result.get("error"),
                exit_code=result.get("exit_code"),
                language=request.language,
                execution_time=execution_time
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/translate")
    async def translate_code(request: TranslateRequest):
        """Traduit du code d'un langage à l'autre"""
        try:
            result = engine.code_engine.translate(
                request.code,
                request.from_language,
                request.to_language
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/analyze")
    async def analyze_code(request: AnalyzeRequest):
        """Analyse du code"""
        try:
            result = engine.code_engine.analyze(request.code, request.language)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/debug")
    async def debug_code(request: CodeRequest):
        """Débogue du code"""
        try:
            result = engine.code_engine.debug(request.code, request.language)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/languages")
    async def get_languages():
        """Liste des langages supportés"""
        return {
            "languages": list(engine.code_executor.executors.keys()),
            "count": len(engine.code_executor.executors)
        }
    
    @app.get("/api/status")
    async def get_status():
        """Statut du moteur"""
        status = engine.get_status()
        status["personality"] = engine.personality.get_personality_context()
        return status
    
    @app.post("/api/feedback")
    async def submit_feedback(feedback: FeedbackRequest):
        """Soumet un feedback"""
        try:
            engine.learner.add_feedback(feedback.dict())
            return {"status": "success", "message": "Merci pour ton feedback !"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/conversations/history")
    async def get_conversation_history(limit: int = 50):
        """Récupère l'historique des conversations"""
        try:
            history = engine.personality.memory.get_recent_context(limit)
            return {"history": history, "count": len(history)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/conversations/clear")
    async def clear_conversation():
        """Efface la conversation en cours"""
        try:
            engine.personality.memory.end_conversation()
            return {"status": "success", "message": "Conversation effacée"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Upload de fichier pour analyse"""
        try:
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Analyse basique
            result = {
                "filename": file.filename,
                "size": len(content),
                "type": file.content_type,
                "preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
            }
            
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # WebSocket
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        
        try:
            while True:
                # Réception du message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Génération de la réponse
                response = engine.generate_response(
                    message.get("prompt", ""),
                    max_length=message.get("max_length", 2048),
                    temperature=message.get("temperature", 0.7)
                )
                
                # Ajout de l'émotion
                response["emotion"] = engine.personality.current_emotion.get("primary")
                response["energy"] = engine.personality.emotions.get_energy_level()
                
                # Envoi de la réponse
                await websocket.send_json(response)
                
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            ws_manager.disconnect(websocket)
    
    # Routes admin
    @app.post("/admin/reset")
    async def reset_conversation(admin_key: str):
        """Reset la conversation (admin seulement)"""
        if admin_key != "orlyne-admin-2024":
            raise HTTPException(status_code=403, detail="Non autorisé")
        
        engine.personality.memory.end_conversation()
        return {"status": "success", "message": "Conversation réinitialisée"}
    
    @app.get("/admin/stats")
    async def get_admin_stats(admin_key: str):
        """Statistiques détaillées (admin)"""
        if admin_key != "orlyne-admin-2024":
            raise HTTPException(status_code=403, detail="Non autorisé")
        
        return {
            "personality": engine.personality.get_personality_context(),
            "feedback": engine.learner.get_feedback_stats(),
            "knowledge": engine.knowledge_base.get_stats() if hasattr(engine, 'knowledge_base') else None,
            "system": {
                "model": engine.model_name,
                "device": engine.device,
                "uptime": engine.uptime if hasattr(engine, 'uptime') else None
            }
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check pour monitoring"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "model_loaded": engine.model is not None
        }
    
    return app