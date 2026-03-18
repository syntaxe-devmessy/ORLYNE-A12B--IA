"""
Adaptateur pour le modèle Llama 3 8B
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

from src.core.exceptions import ModelLoadError
from src.core.config import Config

logger = logging.getLogger(__name__)

class LlamaAdapter:
    """Adaptateur pour Llama 3 8B"""
    
    def __init__(self, model_name: str = "meta-llama/Llama-3-8B"):
        self.model_name = model_name
        self.config = Config()
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """Détermine le périphérique à utiliser"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def load(self):
        """Charge le modèle avec quantification 4-bit"""
        try:
            logger.info(f"🦙 Chargement de Llama 3 8B sur {self.device}...")
            
            # Configuration de quantification
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
            
            # Tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Modèle
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
                attn_implementation="flash_attention_2" if self.device == "cuda" else "sdpa"
            )
            
            # Pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto",
                max_new_tokens=self.config.model.max_length,
                temperature=self.config.model.temperature,
                top_p=self.config.model.top_p,
                repetition_penalty=self.config.model.repetition_penalty,
                do_sample=True
            )
            
            logger.info("✅ Llama 3 8B chargé avec succès")
            
        except Exception as e:
            raise ModelLoadError(f"Impossible de charger Llama 3: {e}", self.model_name)
    
    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Génère une réponse
        
        Args:
            prompt: Prompt d'entrée
            max_length: Longueur maximale
            temperature: Température
            
        Returns:
            Texte généré
        """
        if not self.pipeline:
            self.load()
        
        # Paramètres de génération
        gen_kwargs = {
            "max_new_tokens": max_length or self.config.model.max_length,
            "temperature": temperature or self.config.model.temperature,
            "top_p": self.config.model.top_p,
            "repetition_penalty": self.config.model.repetition_penalty,
            "do_sample": True,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        gen_kwargs.update(kwargs)
        
        # Génération
        outputs = self.pipeline(prompt, **gen_kwargs)
        return outputs[0]['generated_text']
    
    def get_embeddings(self, text: str) -> torch.Tensor:
        """Obtient les embeddings du texte"""
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # Utilise la dernière couche cachée
            embeddings = outputs.hidden_states[-1].mean(dim=1)
        return embeddings
    
    def unload(self):
        """Décharge le modèle pour libérer la mémoire"""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        # Nettoyage CUDA
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("🦙 Modèle déchargé")