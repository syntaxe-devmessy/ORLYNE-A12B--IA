"""
Entraînement du modèle
"""

import torch
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from transformers import Trainer, TrainingArguments
from datasets import Dataset
import json

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Gestionnaire d'entraînement du modèle"""
    
    def __init__(self, model, tokenizer, config: Dict[str, Any] = None):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or {}
        self.training_history = []
        
        # Configuration par défaut
        self.training_args = TrainingArguments(
            output_dir="./data/models/checkpoints",
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="./data/logs/training",
            logging_steps=100,
            save_steps=1000,
            eval_steps=500,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available(),
            dataloader_num_workers=2
        )
    
    def prepare_dataset(self, data_path: Path) -> Dataset:
        """Prépare le dataset pour l'entraînement"""
        logger.info(f"Préparation du dataset depuis {data_path}")
        
        # Chargement des données
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Formatage pour l'entraînement
        formatted_data = []
        for item in data:
            if "prompt" in item and "response" in item:
                text = f"Utilisateur: {item['prompt']}\nOrlyne: {item['response']}"
                formatted_data.append({"text": text})
        
        # Création du dataset
        dataset = Dataset.from_list(formatted_data)
        
        # Tokenization
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train(self, train_dataset: Dataset, eval_dataset: Optional[Dataset] = None):
        """Lance l'entraînement"""
        logger.info("Démarrage de l'entraînement...")
        
        # Création du trainer
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer
        )
        
        # Entraînement
        train_result = trainer.train()
        
        # Sauvegarde
        trainer.save_model()
        self.tokenizer.save_pretrained(self.training_args.output_dir)
        
        # Enregistrement des métriques
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "train_loss": train_result.training_loss,
            "global_step": train_result.global_step,
            "epoch": train_result.epoch
        }
        
        self.training_history.append(metrics)
        
        logger.info(f"Entraînement terminé. Loss: {train_result.training_loss}")
        
        return metrics
    
    def continue_training(self, additional_data_path: Path):
        """Continue l'entraînement avec de nouvelles données"""
        logger.info("Reprise de l'entraînement...")
        
        # Chargement des nouvelles données
        new_dataset = self.prepare_dataset(additional_data_path)
        
        # Reprise de l'entraînement
        return self.train(new_dataset)
    
    def evaluate(self, eval_dataset: Dataset) -> Dict[str, float]:
        """Évalue le modèle"""
        logger.info("Évaluation du modèle...")
        
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer
        )
        
        metrics = trainer.evaluate()
        
        logger.info(f"Métriques d'évaluation: {metrics}")
        
        return metrics
    
    def save_checkpoint(self, path: Path):
        """Sauvegarde un checkpoint"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        logger.info(f"Checkpoint sauvegardé dans {path}")
    
    def load_checkpoint(self, path: Path):
        """Charge un checkpoint"""
        self.model = self.model.from_pretrained(path)
        self.tokenizer = self.tokenizer.from_pretrained(path)
        logger.info(f"Checkpoint chargé depuis {path}")
    
    def get_training_history(self) -> List[Dict]:
        """Retourne l'historique des entraînements"""
        return self.training_history