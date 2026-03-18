"""
Fonctions utilitaires pour Orlyne
"""

import json
import time
import random
import string
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import humanize
import psutil
import platform

class Helpers:
    """Collection de fonctions utilitaires"""
    
    @staticmethod
    def generate_id(prefix: str = "", length: int = 8) -> str:
        """Génère un ID unique"""
        random_part = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=length
        ))
        return f"{prefix}_{random_part}" if prefix else random_part
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Formate une taille en bytes"""
        return humanize.naturalsize(size_bytes)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formate une durée"""
        return humanize.naturaldelta(timedelta(seconds=seconds))
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Formate une date de façon lisible"""
        return humanize.naturaltime(dt)
    
    @staticmethod
    def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Tronque un texte"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """Extrait les blocs de code d'un texte"""
        import re
        pattern = r'```(\w*)\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        blocks = []
        for lang, code in matches:
            blocks.append({
                'language': lang.strip() or 'text',
                'code': code.strip()
            })
        
        return blocks
    
    @staticmethod
    def detect_language(code: str) -> str:
        """Détection basique du langage"""
        patterns = {
            'python': [r'def\s+\w+\s*\(', r'import\s+\w+', r'print\(', r'if\s+__name__'],
            'javascript': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'console\.log'],
            'java': [r'public\s+class', r'public\s+static\s+void\s+main', r'System\.out'],
            'cpp': [r'#include', r'std::', r'int\s+main\s*\('],
            'html': [r'<html', r'<body', r'<div'],
            'css': [r'{.*}', r'@media', r'#\w+\s*{'],
            'sql': [r'SELECT.*FROM', r'INSERT INTO', r'CREATE TABLE'],
        }
        
        for lang, lang_patterns in patterns.items():
            for pattern in lang_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return lang
        
        return 'unknown'
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Retourne des informations système"""
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': Helpers.format_size(psutil.virtual_memory().total),
                'available': Helpers.format_size(psutil.virtual_memory().available),
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': Helpers.format_size(psutil.disk_usage('/').total),
                'free': Helpers.format_size(psutil.disk_usage('/').free),
                'percent': psutil.disk_usage('/').percent
            }
        }
    
    @staticmethod
    def retry(func, max_attempts: int = 3, delay: float = 1.0):
        """Décorateur pour réessayer une fonction"""
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    
    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Divise une liste en chunks"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Fusionne deux dictionnaires profondément"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Helpers.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def clean_dict(data: Dict) -> Dict:
        """Nettoie un dictionnaire (enlève les valeurs None)"""
        return {k: v for k, v in data.items() if v is not None}
    
    @staticmethod
    def safe_json_loads(text: str, default: Any = None) -> Any:
        """Charge du JSON de façon sécurisée"""
        try:
            return json.loads(text)
        except:
            return default
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convertit un texte en slug URL-friendly"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extrait les emails d'un texte"""
        import re
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extrait les URLs d'un texte"""
        import re
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(pattern, text)
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
    @staticmethod
    def get_timestamp() -> str:
        """Retourne un timestamp formaté"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """S'assure qu'un dossier existe"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def human_readable_number(num: float) -> str:
        """Convertit un nombre en format lisible (1K, 1M, etc.)"""
        for unit in ['', 'K', 'M', 'B', 'T']:
            if abs(num) < 1000.0:
                return f"{num:.1f}{unit}"
            num /= 1000.0
        return f"{num:.1f}P"

# Instance globale
helpers = Helpers()