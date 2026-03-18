"""
Stockage vectoriel pour recherche sémantique
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class VectorStore:
    """Stockage et recherche vectorielle"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path("data/vectors")
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.vectors_file = self.storage_path / "vectors.json"
        self.metadata_file = self.storage_path / "metadata.json"
        
        # Chargement des données
        self.vectors = self._load_vectors()
        self.metadata = self._load_metadata()
        
        # Dimension des vecteurs (par défaut pour les embeddings)
        self.vector_dim = 768
        
        # Cache pour les calculs
        self.cache = {}
    
    def _load_vectors(self) -> Dict[str, List[float]]:
        """Charge les vecteurs"""
        if self.vectors_file.exists():
            with open(self.vectors_file, 'r') as f:
                data = json.load(f)
                # Conversion en float
                return {k: [float(x) for x in v] for k, v in data.items()}
        return {}
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Charge les métadonnées"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def add_vector(self, key: str, vector: List[float], metadata: Optional[Dict] = None):
        """
        Ajoute un vecteur
        
        Args:
            key: Identifiant unique
            vector: Vecteur d'embeddings
            metadata: Métadonnées associées
        """
        # Normalisation du vecteur
        vector = self._normalize_vector(vector)
        
        self.vectors[key] = vector
        
        # Métadonnées
        self.metadata[key] = {
            "added": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "dimension": len(vector),
            **(metadata or {})
        }
        
        self._save()
        
        logger.info(f"Vecteur ajouté: {key}")
    
    def add_vectors_batch(self, vectors: Dict[str, Tuple[List[float], Optional[Dict]]]):
        """
        Ajoute plusieurs vecteurs en lot
        
        Args:
            vectors: Dictionnaire {key: (vector, metadata)}
        """
        for key, (vector, metadata) in vectors.items():
            self.vectors[key] = self._normalize_vector(vector)
            self.metadata[key] = {
                "added": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "dimension": len(vector),
                **(metadata or {})
            }
        
        self._save()
        
        logger.info(f"{len(vectors)} vecteurs ajoutés en lot")
    
    def search(self, query_vector: List[float], top_k: int = 10, threshold: float = 0.0) -> List[Dict]:
        """
        Recherche les vecteurs les plus proches
        
        Args:
            query_vector: Vecteur de requête
            top_k: Nombre de résultats
            threshold: Seuil de similarité minimal
            
        Returns:
            Liste des résultats avec scores
        """
        if not self.vectors:
            return []
        
        # Normalisation du vecteur de requête
        query_vector = self._normalize_vector(query_vector)
        
        # Calcul des similarités
        similarities = []
        for key, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            if similarity >= threshold:
                similarities.append({
                    "key": key,
                    "similarity": similarity,
                    "metadata": self.metadata.get(key, {})
                })
        
        # Tri par similarité décroissante
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_k]
    
    def search_by_text(self, text: str, embedding_function, top_k: int = 10) -> List[Dict]:
        """
        Recherche par texte (nécessite une fonction d'embedding)
        
        Args:
            text: Texte à rechercher
            embedding_function: Fonction qui transforme texte en vecteur
            top_k: Nombre de résultats
            
        Returns:
            Liste des résultats
        """
        # Génération du vecteur pour le texte
        query_vector = embedding_function(text)
        
        return self.search(query_vector, top_k)
    
    def get_similar(self, key: str, top_k: int = 5) -> List[Dict]:
        """
        Trouve les vecteurs similaires à un vecteur existant
        
        Args:
            key: Clé du vecteur de référence
            top_k: Nombre de résultats
            
        Returns:
            Liste des vecteurs similaires
        """
        if key not in self.vectors:
            return []
        
        vector = self.vectors[key]
        results = self.search(vector, top_k + 1)  # +1 pour exclure le vecteur lui-même
        
        # Exclure le vecteur lui-même
        return [r for r in results if r["key"] != key][:top_k]
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calcule la similarité cosinus entre deux vecteurs"""
        # Utilisation du cache si possible
        cache_key = f"{hashlib.md5(str(v1).encode()).hexdigest()}_{hashlib.md5(str(v2).encode()).hexdigest()}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Conversion en numpy pour efficacité
        a = np.array(v1)
        b = np.array(v2)
        
        # Calcul
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (norm_a * norm_b)
        
        # Mise en cache
        self.cache[cache_key] = similarity
        
        return float(similarity)
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalise un vecteur (L2 normalization)"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return [float(x / norm) for x in vector]
    
    def _save(self):
        """Sauvegarde les vecteurs et métadonnées"""
        with open(self.vectors_file, 'w') as f:
            json.dump(self.vectors, f)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def delete_vector(self, key: str):
        """Supprime un vecteur"""
        if key in self.vectors:
            del self.vectors[key]
        if key in self.metadata:
            del self.metadata[key]
        
        self._save()
        
        logger.info(f"Vecteur supprimé: {key}")
    
    def clear(self):
        """Vide le store"""
        self.vectors = {}
        self.metadata = {}
        self.cache = {}
        self._save()
        
        logger.info("Store vectoriel vidé")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques"""
        if not self.vectors:
            return {"count": 0}
        
        dimensions = [len(v) for v in self.vectors.values()]
        
        return {
            "count": len(self.vectors),
            "dimensions": {
                "min": min(dimensions),
                "max": max(dimensions),
                "avg": sum(dimensions) / len(dimensions)
            },
            "metadata_fields": list(set(
                k for meta in self.metadata.values() for k in meta.keys()
            )),
            "last_updated": max(
                (meta.get("updated", "") for meta in self.metadata.values()),
                default=""
            )
        }
    
    def export_vectors(self, format: str = "json") -> Dict:
        """Exporte tous les vecteurs"""
        return {
            "vectors": self.vectors,
            "metadata": self.metadata,
            "stats": self.get_stats()
        }