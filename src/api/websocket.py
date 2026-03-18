"""
Gestionnaire WebSocket pour chat en temps réel
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Gestionnaire de connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accepte une nouvelle connexion"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_data[websocket] = {
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0
        }
        logger.info(f"Nouvelle connexion WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Déconnecte un client"""
        self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        logger.info(f"Connexion WebSocket fermée. Restants: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envoie un message à un client spécifique"""
        try:
            await websocket.send_json(message)
            if websocket in self.connection_data:
                self.connection_data[websocket]["message_count"] += 1
        except Exception as e:
            logger.error(f"Erreur envoi message personnel: {e}")
    
    async def broadcast(self, message: dict):
        """Diffuse un message à tous les clients"""
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erreur broadcast: {e}")
                await self.disconnect(connection)
    
    async def broadcast_typing(self, is_typing: bool, user: str = "Orlyne"):
        """Diffuse un statut de frappe"""
        await self.broadcast({
            "type": "typing",
            "user": user,
            "is_typing": is_typing
        })
    
    async def broadcast_emotion(self, emotion: str):
        """Diffuse le changement d'émotion"""
        await self.broadcast({
            "type": "emotion_update",
            "emotion": emotion,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des connexions"""
        return {
            "active_connections": len(self.active_connections),
            "total_messages": sum(
                data["message_count"] for data in self.connection_data.values()
            ),
            "connections_detail": [
                {
                    "connected_for": asyncio.get_event_loop().time() - data["connected_at"],
                    "messages": data["message_count"]
                }
                for data in self.connection_data.values()
            ]
        }