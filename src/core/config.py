"""
Configuration centralisée d'Orlyne
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Configuration du modèle"""
    name: str = "meta-llama/Llama-3-8B"
    quantization: str = "4bit"
    device: str = "auto"
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.95
    repetition_penalty: float = 1.1


@dataclass
class PersonalityConfig:
    """Configuration de la personnalité"""
    name: str = "Orlyne"
    traits: Dict[str, float] = field(default_factory=lambda: {
        "amical": 0.9,
        "enthousiaste": 0.85,
        "technique": 0.95,
        "humoristique": 0.8,
        "empathique": 0.85
    })
    uncensored: bool = True
    languages: list = field(default_factory=lambda: ["fr", "en"])


@dataclass
class CodeEngineConfig:
    """Configuration du moteur de code"""
    use_docker: bool = True
    timeout_seconds: int = 30
    max_memory_mb: int = 512
    max_cpu_cores: float = 0.5
    network_enabled: bool = False
    supported_languages: list = field(default_factory=lambda: [
        "python", "javascript", "typescript", "java", "cpp", "c",
        "rust", "go", "ruby", "php", "swift", "kotlin", "bash",
        "powershell", "sql", "r", "perl", "lua", "dart", "elixir",
        "haskell", "scala", "julia", "matlab"
    ])


@dataclass
class APIConfig:
    """Configuration de l'API"""
    host: str = "0.0.0.0"
    port: int = 8000
    rate_limit_enabled: bool = False
    requests_per_minute: int = 0
    websocket_enabled: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class LearningConfig:
    """Configuration de l'apprentissage"""
    memory_enabled: bool = True
    memory_size: int = 1000
    vector_store: str = "chromadb"
    feedback_learning: bool = True
    fine_tuning_enabled: bool = True


class Config:
    """Configuration principale"""
    
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
        self.root_dir = Path(__file__).parent.parent.parent
        
        # Chargement depuis les variables d'environnement
        self.env = os.getenv("ORLYNE_ENV", "development")
        
        # Chargement depuis le fichier de config
        self._load_from_file()
        
        # Initialisation des sous-configs
        self.model = ModelConfig()
        self.personality = PersonalityConfig()
        self.code_engine = CodeEngineConfig()
        self.api = APIConfig()
        self.learning = LearningConfig()
        
        # Surcharge avec variables d'env
        self._override_from_env()
    
    def _load_from_file(self):
        """Charge la configuration depuis orlyne.json"""
        config_file = self.root_dir / "orlyne.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                
                # Mise à jour des configurations
                if "model" in data:
                    for key, value in data["model"].items():
                        if hasattr(self, "model") and hasattr(self.model, key):
                            setattr(self.model, key, value)
                
                # etc...
    
    def _override_from_env(self):
        """Surcharge avec les variables d'environnement"""
        if os.getenv("ORLYNE_MODEL"):
            self.model.name = os.getenv("ORLYNE_MODEL")
        if os.getenv("ORLYNE_DEVICE"):
            self.model.device = os.getenv("ORLYNE_DEVICE")
        if os.getenv("ORLYNE_UNCENSORED"):
            self.personality.uncensored = os.getenv("ORLYNE_UNCENSORED").lower() == "true"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            "model": {
                "name": self.model.name,
                "quantization": self.model.quantization,
                "device": self.model.device,
                "max_length": self.model.max_length,
                "temperature": self.model.temperature
            },
            "personality": {
                "name": self.personality.name,
                "traits": self.personality.traits,
                "uncensored": self.personality.uncensored,
                "languages": self.personality.languages
            },
            "code_engine": {
                "use_docker": self.code_engine.use_docker,
                "timeout": self.code_engine.timeout_seconds,
                "max_memory_mb": self.code_engine.max_memory_mb,
                "supported_languages": self.code_engine.supported_languages
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "rate_limit_enabled": self.api.rate_limit_enabled
            },
            "learning": {
                "memory_enabled": self.learning.memory_enabled,
                "feedback_learning": self.learning.feedback_learning,
                "fine_tuning_enabled": self.learning.fine_tuning_enabled
            }
        }