"""
Base de connaissances pour Orlyne
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """Base de connaissances évolutive"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path("data/knowledge")
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_file = self.storage_path / "knowledge_base.json"
        self.index_file = self.storage_path / "index.json"
        
        # Chargement des connaissances
        self.knowledge_base = self._load_knowledge()
        self.index = self._load_index()
        
        # Catégories de connaissances
        self.categories = {
            "programming": {},
            "concepts": {},
            "tutorials": {},
            "faq": {},
            "best_practices": {},
            "code_patterns": {},
            "debugging": {},
            "algorithms": {}
        }
    
    def _load_knowledge(self) -> Dict:
        """Charge la base de connaissances"""
        if self.knowledge_file.exists():
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {cat: {} for cat in self.categories}
    
    def _load_index(self) -> Dict:
        """Charge l'index des connaissances"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {
            "keywords": {},
            "last_updated": datetime.now().isoformat(),
            "total_entries": 0
        }
    
    def add_knowledge(self, category: str, key: str, content: Dict[str, Any]):
        """
        Ajoute une connaissance
        
        Args:
            category: Catégorie (programming, concepts, etc.)
            key: Identifiant unique
            content: Contenu de la connaissance
        """
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        # Ajout des métadonnées
        content["_metadata"] = {
            "added": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "version": 1,
            "id": hashlib.md5(f"{category}_{key}".encode()).hexdigest()[:8]
        }
        
        self.knowledge_base[category][key] = content
        
        # Mise à jour de l'index
        self._update_index(category, key, content)
        
        self._save()
        
        logger.info(f"Connaissance ajoutée: {category}/{key}")
    
    def update_knowledge(self, category: str, key: str, content: Dict[str, Any]):
        """Met à jour une connaissance existante"""
        if category in self.knowledge_base and key in self.knowledge_base[category]:
            # Incrémente la version
            metadata = self.knowledge_base[category][key].get("_metadata", {})
            metadata["updated"] = datetime.now().isoformat()
            metadata["version"] = metadata.get("version", 1) + 1
            
            content["_metadata"] = metadata
            self.knowledge_base[category][key].update(content)
            
            # Mise à jour de l'index
            self._update_index(category, key, content)
            
            self._save()
            
            logger.info(f"Connaissance mise à jour: {category}/{key}")
        else:
            self.add_knowledge(category, key, content)
    
    def get_knowledge(self, category: str, key: str) -> Optional[Dict]:
        """Récupère une connaissance"""
        return self.knowledge_base.get(category, {}).get(key)
    
    def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Recherche dans la base de connaissances"""
        results = []
        query_lower = query.lower()
        
        categories = [category] if category else self.knowledge_base.keys()
        
        for cat in categories:
            for key, content in self.knowledge_base.get(cat, {}).items():
                score = 0
                
                # Recherche dans le titre
                if query_lower in key.lower():
                    score += 10
                
                # Recherche dans le contenu
                content_str = json.dumps(content).lower()
                score += content_str.count(query_lower)
                
                # Recherche par mots-clés
                keywords = self.index["keywords"].get(key, [])
                for kw in keywords:
                    if query_lower in kw.lower():
                        score += 5
                
                if score > 0:
                    results.append({
                        "category": cat,
                        "key": key,
                        "content": content,
                        "relevance": score
                    })
        
        # Tri par pertinence
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results[:limit]
    
    def _update_index(self, category: str, key: str, content: Dict):
        """Met à jour l'index pour la recherche"""
        # Extraction des mots-clés
        text = f"{key} {json.dumps(content)}"
        words = set(text.lower().split())
        
        for word in words:
            if len(word) > 3:  # Ignore les mots trop courts
                if word not in self.index["keywords"]:
                    self.index["keywords"][word] = []
                if key not in self.index["keywords"][word]:
                    self.index["keywords"][word].append(key)
        
        self.index["last_updated"] = datetime.now().isoformat()
        self.index["total_entries"] = sum(len(v) for v in self.knowledge_base.values())
    
    def _save(self):
        """Sauvegarde la base de connaissances"""
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories"""
        return list(self.knowledge_base.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base"""
        return {
            "total_entries": self.index["total_entries"],
            "categories": {
                cat: len(entries) for cat, entries in self.knowledge_base.items()
            },
            "last_updated": self.index["last_updated"],
            "keywords_count": len(self.index["keywords"])
        }
    
    def import_from_file(self, file_path: Path):
        """Importe des connaissances depuis un fichier JSON"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for category, entries in data.items():
            for key, content in entries.items():
                self.add_knowledge(category, key, content)
        
        logger.info(f"Importé depuis {file_path}")
    
    def export_to_file(self, file_path: Path):
        """Exporte la base vers un fichier JSON"""
        with open(file_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Exporté vers {file_path}")