"""
Rate limiter pour l'API
"""

import time
from typing import Dict, Tuple, Optional
from collections import defaultdict
import threading

class RateLimiter:
    """Limiteur de taux de requêtes"""
    
    def __init__(self, requests_per_minute: int = 60, enabled: bool = False):
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def check(self, client_id: str) -> bool:
        """
        Vérifie si le client peut faire une requête
        
        Args:
            client_id: Identifiant du client
            
        Returns:
            True si la requête est autorisée
        """
        if not self.enabled:
            return True
        
        with self.lock:
            now = time.time()
            window = 60  # 1 minute
            
            # Nettoie les anciennes requêtes
            self.requests[client_id] = [
                t for t in self.requests[client_id]
                if now - t < window
            ]
            
            # Vérifie le nombre de requêtes
            if len(self.requests[client_id]) >= self.requests_per_minute:
                return False
            
            # Ajoute la nouvelle requête
            self.requests[client_id].append(now)
            return True
    
    def get_remaining(self, client_id: str) -> int:
        """Retourne le nombre de requêtes restantes"""
        if not self.enabled:
            return float('inf')
        
        with self.lock:
            now = time.time()
            window = 60
            
            # Nettoie les anciennes requêtes
            self.requests[client_id] = [
                t for t in self.requests[client_id]
                if now - t < window
            ]
            
            return max(0, self.requests_per_minute - len(self.requests[client_id]))
    
    def get_reset_time(self, client_id: str) -> Optional[float]:
        """Retourne le temps de reset du rate limit"""
        if not self.enabled or not self.requests[client_id]:
            return None
        
        with self.lock:
            # Le reset aura lieu 60 secondes après la première requête
            oldest = min(self.requests[client_id])
            return oldest + 60
    
    def reset(self, client_id: Optional[str] = None):
        """Reset le rate limit pour un client ou tous"""
        with self.lock:
            if client_id:
                self.requests[client_id] = []
            else:
                self.requests.clear()