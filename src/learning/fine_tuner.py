"""
Fine-tuning en temps réel
"""

import torch
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from peft import LoraConfig, get_peft_model, TaskType
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FineTuner:
    """Fine-tuning en temps réel avec LoRA"""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.lora_config = None
        self.lora_model = None
        self.fine_tuning_history = []
        
        # Configuration LoRA par défaut
        self.default_lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,  # rang
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.1,
            bias="none"
        )
    
    def setup_lora(self, config: Optional[LoraConfig] = None):
        """Configure LoRA pour le fine-tuning efficace"""
        if config is None:
            config = self.default_lora_config
        
        self.lora_config = config
        self.lora_model = get_peft_model(self.model, config)
        
        logger.info(f"LoRA configuré avec {config.r} de rang")
        
        # Affiche le nombre de paramètres entraînables
        trainable_params = sum(p.numel() for p in self.lora_model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.lora_model.parameters())
        
        logger.info(f"Paramètres entraînables: {trainable_params} / {total_params} "
                   f"({100 * trainable_params / total_params:.2f}%)")
        
        return self.lora_model
    
    def fine_tune(self, examples: List[Dict[str, str]], 
                  learning_rate: float = 1e-4,
                  num_epochs: int = 1) -> Dict[str, Any]:
        """
        Fine-tuning en temps réel sur quelques exemples
        
        Args:
            examples: Liste d'exemples {"prompt": "...", "response": "..."}
            learning_rate: Taux d'apprentissage
            num_epochs: Nombre d'époques
            
        Returns:
            Métriques d'entraînement
        """
        if self.lora_model is None:
            self.setup_lora()
        
        logger.info(f"Démarrage du fine-tuning sur {len(examples)} exemples")
        
        # Préparation des données
        texts = []
        for ex in examples:
            text = f"Utilisateur: {ex['prompt']}\nOrlyne: {ex['response']}"
            texts.append(text)
        
        # Tokenization
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Configuration de l'optimiseur
        optimizer = torch.optim.AdamW(self.lora_model.parameters(), lr=learning_rate)
        
        # Passage en mode entraînement
        self.lora_model.train()
        
        losses = []
        
        for epoch in range(num_epochs):
            epoch_loss = 0
            num_batches = 0
            
            for i in range(0, len(texts), 4):  # batch size 4
                batch = {k: v[i:i+4] for k, v in encodings.items()}
                
                # Forward
                outputs = self.lora_model(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"],
                    labels=batch["input_ids"]
                )
                
                loss = outputs.loss
                epoch_loss += loss.item()
                num_batches += 1
                
                # Backward
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
            
            avg_loss = epoch_loss / num_batches
            losses.append(avg_loss)
            logger.info(f"Epoch {epoch + 1}/{num_epochs} - Loss: {avg_loss:.4f}")
        
        # Sauvegarde de l'historique
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "num_examples": len(examples),
            "final_loss": losses[-1] if losses else None,
            "losses": losses,
            "learning_rate": learning_rate,
            "num_epochs": num_epochs
        }
        
        self.fine_tuning_history.append(metrics)
        
        return metrics
    
    def fine_tune_from_feedback(self, feedback_data: List[Dict]):
        """Fine-tuning à partir des retours utilisateurs"""
        # Filtre les feedbacks positifs
        positive_examples = [
            f for f in feedback_data 
            if f.get("rating", 0) > 4 or f.get("feedback", "").lower() in ["good", "excellent", "👍"]
        ]
        
        if len(positive_examples) < 2:
            logger.info("Pas assez de feedbacks positifs pour le fine-tuning")
            return None
        
        # Extrait les paires prompt/réponse
        examples = []
        for ex in positive_examples[-10:]:  # Garde les 10 derniers
            if "prompt" in ex and "response" in ex:
                examples.append({
                    "prompt": ex["prompt"],
                    "response": ex["response"]
                })
        
        if examples:
            return self.fine_tune(examples)
        
        return None
    
    def save_lora_weights(self, path: Path):
        """Sauvegarde les poids LoRA"""
        if self.lora_model:
            self.lora_model.save_pretrained(path)
            logger.info(f"Poids LoRA sauvegardés dans {path}")
    
    def load_lora_weights(self, path: Path):
        """Charge les poids LoRA"""
        if self.lora_model:
            self.lora_model.load_adapter(path)
            logger.info(f"Poids LoRA chargés depuis {path}")
    
    def reset_lora(self):
        """Réinitialise les poids LoRA"""
        if self.lora_model:
            # Re-crée le modèle LoRA avec les poids d'origine
            self.lora_model = get_peft_model(self.model, self.lora_config)
            logger.info("Poids LoRA réinitialisés")
    
    def get_fine_tuning_history(self) -> List[Dict]:
        """Retourne l'historique des fine-tuning"""
        return self.fine_tuning_history