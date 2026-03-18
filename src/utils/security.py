"""
Module de sécurité pour Orlyne
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
import jwt
from datetime import datetime, timedelta
import bcrypt

class SecurityManager:
    """Gestionnaire de sécurité"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_expiry = 24  # heures
        
        # Patterns pour détection de code malveillant
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/\s*',  # rm -rf /
            r'format\s+C:\s*',    # format C:
            r'dd\s+if=.*of=.*',   # dd command
            r'DROP\s+DATABASE',    # SQL injection
            r'DELETE\s+FROM.*WHERE', # SQL injection
        ]
        
        # Commandes shell dangereuses
        self.dangerous_commands = [
            'rm', 'del', 'format', 'dd', 'mkfs', 
            ':(){ :|:& };:',  # fork bomb
        ]
    
    def sanitize_input(self, text: str) -> str:
        """Nettoie l'entrée utilisateur"""
        # Suppression des caractères de contrôle
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        # Échappement HTML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
    
    def is_dangerous_code(self, code: str, language: str) -> Dict[str, Any]:
        """Vérifie si le code est potentiellement dangereux"""
        warnings = []
        
        # Vérification des patterns dangereux
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(f"Pattern dangereux détecté: {pattern}")
        
        # Vérification des commandes shell
        if language in ['bash', 'sh', 'shell']:
            for cmd in self.dangerous_commands:
                if re.search(rf'\b{cmd}\b', code):
                    warnings.append(f"Commande shell dangereuse: {cmd}")
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings,
            "level": "high" if warnings else "safe"
        }
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Vérifie un mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: str, data: Dict = None) -> str:
        """Génère un token JWT"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry),
            'iat': datetime.utcnow()
        }
        if data:
            payload.update(data)
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Vérifie un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_api_key(self) -> str:
        """Génère une clé API"""
        return f"orly_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash une clé API"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Valide un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier"""
        # Supprime les caractères dangereux
        filename = re.sub(r'[^\w\-_\. ]', '', filename)
        # Évite les path traversals
        filename = filename.replace('..', '')
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')
        return filename.strip()
    
    def check_rate_limit(self, user_id: str, action: str, 
                         max_requests: int, window: int) -> bool:
        """Vérifie le rate limiting (à implémenter avec Redis)"""
        # Implémentation basique en mémoire
        if not hasattr(self, '_rate_limits'):
            self._rate_limits = {}
        
        key = f"{user_id}:{action}"
        now = datetime.now()
        
        if key not in self._rate_limits:
            self._rate_limits[key] = []
        
        # Nettoie les anciennes requêtes
        self._rate_limits[key] = [
            t for t in self._rate_limits[key]
            if (now - t).total_seconds() < window
        ]
        
        if len(self._rate_limits[key]) >= max_requests:
            return False
        
        self._rate_limits[key].append(now)
        return True
    
    def encrypt_data(self, data: str) -> str:
        """Chiffre des données (simple pour l'exemple)"""
        # À implémenter avec AES ou autre
        return data  # Placeholder
    
    def decrypt_data(self, encrypted: str) -> str:
        """Déchiffre des données"""
        # À implémenter avec AES ou autre
        return encrypted  # Placeholder
    
    def generate_csrf_token(self) -> str:
        """Génère un token CSRF"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Valide un token CSRF"""
        return token == session_token
    
    def get_security_headers(self) -> Dict[str, str]:
        """Retourne les headers de sécurité recommandés"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

# Instance globale
security = SecurityManager()