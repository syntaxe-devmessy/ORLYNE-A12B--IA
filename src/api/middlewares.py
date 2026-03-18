"""
Middlewares pour l'API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Callable
import uuid

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger les requêtes"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Génération d'un ID de requête
        request_id = str(uuid.uuid4())[:8]
        
        # Log de la requête entrante
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        
        # Timing
        start_time = time.time()
        
        # Traitement
        response = await call_next(request)
        
        # Calcul du temps
        process_time = time.time() - start_time
        
        # Ajout des headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log de la réponse
        logger.info(f"[{request_id}] {response.status_code} - {process_time:.3f}s")
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter des headers de sécurité"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def setup_middlewares(app: FastAPI):
    """Configure tous les middlewares"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )
    
    # Middlewares personnalisés
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    logger.info("Middlewares configurés")