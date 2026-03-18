"""
Système de logging pour Orlyne
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import json
import traceback

class OrlyneLogger:
    """Logger personnalisé pour Orlyne"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = Path("data/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.setup_logging()
        
        # Création des loggers
        self.main_logger = self._create_logger('orlyne')
        self.api_logger = self._create_logger('api')
        self.code_logger = self._create_logger('code')
        self.error_logger = self._create_logger('errors')
        self.performance_logger = self._create_logger('performance')
        
        # Métriques
        self.metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'total_tokens': 0,
            'average_response_time': 0
        }
    
    def setup_logging(self):
        """Configure le système de logging"""
        # Format
        detailed_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        simple_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_format)
        
        # Handler fichier principal (rotation par taille)
        main_handler = RotatingFileHandler(
            self.log_dir / 'orlyne.log',
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(detailed_format)
        
        # Handler erreurs (rotation par temps)
        error_handler = TimedRotatingFileHandler(
            self.log_dir / 'errors.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_format)
        
        # Handler performance
        perf_handler = RotatingFileHandler(
            self.log_dir / 'performance.log',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(simple_format)
        
        # Configuration du logging racine
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(main_handler)
        root_logger.addHandler(error_handler)
    
    def _create_logger(self, name: str) -> logging.Logger:
        """Crée un logger spécifique"""
        logger = logging.getLogger(name)
        
        # Handler fichier spécifique
        handler = RotatingFileHandler(
            self.log_dir / f'{name}.log',
            maxBytes=5*1024*1024,
            backupCount=3
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        
        return logger
    
    def log_request(self, method: str, path: str, status: int, duration: float):
        """Log une requête API"""
        self.metrics['total_requests'] += 1
        self.metrics['average_response_time'] = (
            self.metrics['average_response_time'] * 0.9 + duration * 0.1
        )
        
        self.api_logger.info(
            f"Request: {method} {path} - Status: {status} - Duration: {duration:.3f}s"
        )
    
    def log_code_execution(self, language: str, success: bool, duration: float):
        """Log une exécution de code"""
        status = "SUCCESS" if success else "FAILURE"
        self.code_logger.info(f"Code: {language} - {status} - Duration: {duration:.3f}s")
    
    def log_error(self, error: Exception, context: dict = None):
        """Log une erreur"""
        self.metrics['total_errors'] += 1
        
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.error_logger.error(json.dumps(error_info, indent=2))
    
    def log_performance(self, operation: str, duration: float, metadata: dict = None):
        """Log une métrique de performance"""
        self.performance_logger.info(
            f"PERF: {operation} - {duration:.3f}s - {metadata or {}}"
        )
    
    def log_interaction(self, user_id: str, prompt: str, response: str, tokens: int):
        """Log une interaction utilisateur"""
        self.main_logger.info(
            f"Interaction - User: {user_id} - Tokens: {tokens}"
        )
        
        # Log détaillé dans un fichier séparé
        with open(self.log_dir / 'interactions.log', 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'prompt': prompt[:100] + ('...' if len(prompt) > 100 else ''),
                'tokens': tokens
            }) + '\n')
    
    def get_metrics(self) -> dict:
        """Retourne les métriques actuelles"""
        return {
            **self.metrics,
            'log_size': sum(
                f.stat().st_size for f in self.log_dir.glob('*.log')
            ),
            'log_files': list(self.log_dir.glob('*.log'))
        }
    
    def rotate_logs(self):
        """Force la rotation des logs"""
        for handler in logging.getLogger().handlers:
            if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                handler.doRollover()
    
    def cleanup_old_logs(self, days: int = 30):
        """Nettoie les logs de plus de X jours"""
        import time
        cutoff = time.time() - days * 24 * 3600
        
        for log_file in self.log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                self.main_logger.info(f"Log supprimé: {log_file}")

# Instance globale
logger = OrlyneLogger()