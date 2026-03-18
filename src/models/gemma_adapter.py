"""
Adaptateur pour Google Gemma
"""

import torch
import logging
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

class GemmaAdapter:
    """Adaptateur pour Google Gemma"""
    
    def __init__(self, model_name: str = "google/gemma-7b"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load(self):
        """Charge le modèle Gemma"""
        logger.info(f" Loading Gemma...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
    def generate(self, prompt: str, **kwargs) -> str:
        """Génère une réponse"""
        if not self.model:
            self.load()
            
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, **kwargs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)