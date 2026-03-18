"""
Moteur principal d'Orlyne
Gère l'initialisation des modèles et la logique centrale
"""

import torch
import logging
from typing import Optional, Dict, Any
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)

from src.personality.character import OrlynePersonality
from src.code_engine.base_executor import CodeExecutor
from src.learning.feedback import FeedbackLearner

logger = logging.getLogger(__name__)

class OrlyneEngine:
    """Moteur principal d'Orlyne"""
    
    def __init__(self, model_name: str = "meta-llama/Llama-3-8B"):
        """
        Initialisation du moteur
        
        Args:
            model_name: Nom du modèle à charger
        """
        self.model_name = model_name
        self.device = self._get_device()
        
        # Initialisation des composants
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # Modules fonctionnels
        self.personality = OrlynePersonality()
        self.code_executor = CodeExecutor()
        self.learner = FeedbackLearner()
        
        # Chargement du modèle
        self._load_model()
        
        logger.info(f"✅ Moteur initialisé sur {self.device}")
        
    def _get_device(self) -> str:
        """Détermine le périphérique à utiliser"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def _load_model(self):
        """Charge le modèle Llama 3 8B avec optimisations"""
        try:
            logger.info(f"📦 Chargement du modèle {self.model_name}...")
            
            # Configuration pour la quantification (économie de mémoire)
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            )
            
            # Chargement du tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Chargement du modèle
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
            
            # Création du pipeline de génération
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto"
            )
            
            logger.info("✅ Modèle chargé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        max_length: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une réponse avec la personnalité d'Orlyne
        
        Args:
            prompt: Prompt utilisateur
            max_length: Longueur maximale de la réponse
            temperature: Température pour la génération
            
        Returns:
            Réponse générée et métadonnées
        """
        try:
            # Ajout de la personnalité au prompt
            enhanced_prompt = self.personality.enhance_prompt(prompt)
            
            # Génération de la réponse
            response = self.pipeline(
                enhanced_prompt,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                **kwargs
            )[0]['generated_text']
            
            # Nettoyage de la réponse
            cleaned_response = self._clean_response(response, prompt)
            
            # Apprentissage par feedback (si disponible)
            self.learner.record_interaction(prompt, cleaned_response)
            
            return {
                "response": cleaned_response,
                "model": self.model_name,
                "tokens_used": len(self.tokenizer.encode(response)),
                "personality_used": True
            }
            
        except Exception as e:
            logger.error(f"Erreur de génération: {e}")
            return {
                "response": "Désolé, j'ai rencontré une erreur. Peux-tu reformuler ? 😅",
                "error": str(e)
            }
    
    def _clean_response(self, response: str, original_prompt: str) -> str:
        """Nettoie la réponse générée"""
        # Enlève le prompt original si présent
        if response.startswith(original_prompt):
            response = response[len(original_prompt):].strip()
        return response
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Exécute du code dans un environnement sécurisé
        
        Args:
            code: Code à exécuter
            language: Langage de programmation
            
        Returns:
            Résultat de l'exécution
        """
        return self.code_executor.execute(code, language)
    
    def shutdown(self):
        """Arrête proprement le moteur"""
        logger.info("🛑 Arrêt du moteur...")
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("✅ Moteur arrêté")