"""
Apprentissage par feedback utilisateur
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

class FeedbackLearner:
    """Apprentissage continu par feedback"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path("data/feedback")
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.storage_path / "feedback_history.json"
        self.stats_file = self.storage_path / "feedback_stats.json"
        
        # Historique des feedbacks
        self.feedback_history = self._load_feedback()
        
        # Statistiques
        self.stats = self._load_stats()
        
        # Poids des différentes métriques
        self.metric_weights = {
            "accuracy": 0.3,
            "relevance": 0.25,
            "helpfulness": 0.25,
            "friendliness": 0.2
        }
    
    def _load_feedback(self) -> List[Dict]:
        """Charge l'historique des feedbacks"""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return []
    
    def _load_stats(self) -> Dict:
        """Charge les statistiques"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        
        return {
            "total_feedback": 0,
            "average_rating": 0,
            "ratings_distribution": {},
            "top_topics": [],
            "improvement_areas": [],
            "user_satisfaction_trend": []
        }
    
    def add_feedback(self, feedback: Dict[str, Any]):
        """
        Ajoute un feedback
        
        Args:
            feedback: {
                "prompt": str,
                "response": str,
                "rating": int (1-5),
                "feedback": str,
                "user_id": str (optionnel),
                "metadata": dict (optionnel)
            }
        """
        # Ajout du timestamp
        feedback["timestamp"] = datetime.now().isoformat()
        
        # ID unique
        feedback["id"] = f"fb_{len(self.feedback_history)}_{datetime.now().timestamp()}"
        
        # Sauvegarde
        self.feedback_history.append(feedback)
        
        # Mise à jour des stats
        self._update_stats(feedback)
        
        # Sauvegarde sur disque
        self._save_feedback()
        
        logger.info(f"Feedback ajouté: rating={feedback.get('rating')}")
        
        # Déclenchement d'apprentissage si assez de feedbacks
        if len(self.feedback_history) % 10 == 0:
            self.trigger_learning()
    
    def _update_stats(self, feedback: Dict):
        """Met à jour les statistiques avec le nouveau feedback"""
        self.stats["total_feedback"] += 1
        
        # Mise à jour de la moyenne
        rating = feedback.get("rating")
        if rating:
            current_total = self.stats["average_rating"] * (self.stats["total_feedback"] - 1)
            self.stats["average_rating"] = (current_total + rating) / self.stats["total_feedback"]
            
            # Distribution
            rating_key = str(rating)
            self.stats["ratings_distribution"][rating_key] = \
                self.stats["ratings_distribution"].get(rating_key, 0) + 1
        
        # Analyse des topics
        prompt = feedback.get("prompt", "")
        topics = self._extract_topics(prompt)
        
        for topic in topics:
            # Mise à jour des stats des topics
            if "top_topics" not in self.stats:
                self.stats["top_topics"] = []
            
            # Simple comptage pour l'instant
            topic_stats = next((t for t in self.stats["top_topics"] if t["name"] == topic), None)
            if topic_stats:
                topic_stats["count"] += 1
                # Met à jour le rating moyen pour ce topic
                if rating:
                    current = topic_stats.get("avg_rating", 0) * (topic_stats["count"] - 1)
                    topic_stats["avg_rating"] = (current + rating) / topic_stats["count"]
            else:
                self.stats["top_topics"].append({
                    "name": topic,
                    "count": 1,
                    "avg_rating": rating
                })
        
        # Sauvegarde des stats
        self._save_stats()
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrait les topics principaux d'un texte"""
        # Liste de mots-clés par topic
        topic_keywords = {
            "python": ["python", "django", "flask", "pandas"],
            "javascript": ["javascript", "js", "react", "node", "vue"],
            "web": ["html", "css", "site", "web", "frontend"],
            "database": ["sql", "base de données", "mongodb", "postgresql"],
            "api": ["api", "rest", "endpoint"],
            "debug": ["bug", "erreur", "debug", "problem"],
            "algorithm": ["algorithme", "complexité", "optimisation"]
        }
        
        found_topics = []
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_topics.append(topic)
                    break
        
        return found_topics if found_topics else ["general"]
    
    def _save_feedback(self):
        """Sauvegarde l'historique des feedbacks"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_history, f, indent=2)
    
    def _save_stats(self):
        """Sauvegarde les statistiques"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_recent_feedback(self, limit: int = 50) -> List[Dict]:
        """Récupère les feedbacks récents"""
        return sorted(
            self.feedback_history[-limit:],
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
    
    def get_high_rated_examples(self, min_rating: int = 4, limit: int = 20) -> List[Dict]:
        """Récupère les exemples les mieux notés"""
        good_examples = [
            f for f in self.feedback_history 
            if f.get("rating", 0) >= min_rating
        ]
        return good_examples[-limit:]
    
    def get_low_rated_examples(self, max_rating: int = 2, limit: int = 20) -> List[Dict]:
        """Récupère les exemples mal notés (pour amélioration)"""
        bad_examples = [
            f for f in self.feedback_history 
            if f.get("rating", 5) <= max_rating
        ]
        return bad_examples[-limit:]
    
    def get_improvement_suggestions(self) -> List[str]:
        """Génère des suggestions d'amélioration basées sur les feedbacks"""
        suggestions = []
        
        # Analyse des feedbacks récents
        recent = self.get_recent_feedback(100)
        low_rated = [f for f in recent if f.get("rating", 5) < 3]
        
        if low_rated:
            # Extrait les problèmes communs
            problems = defaultdict(int)
            for fb in low_rated:
                fb_text = fb.get("feedback", "").lower()
                if "compr" in fb_text or "pas clair" in fb_text:
                    problems["clarity"] += 1
                if "trop long" in fb_text or "long" in fb_text:
                    problems["conciseness"] += 1
                if "aide pas" in fb_text or "inutile" in fb_text:
                    problems["helpfulness"] += 1
            
            # Génère des suggestions
            if problems["clarity"] > len(low_rated) * 0.3:
                suggestions.append("Améliorer la clarté des explications")
            if problems["conciseness"] > len(low_rated) * 0.3:
                suggestions.append("Rendre les réponses plus concises")
            if problems["helpfulness"] > len(low_rated) * 0.3:
                suggestions.append("Être plus utile et pratique")
        
        # Suggestions basées sur les topics
        topics = self.stats.get("top_topics", [])
        low_rated_topics = [t for t in topics if t.get("avg_rating", 5) < 3.5]
        
        for topic in low_rated_topics:
            suggestions.append(f"Améliorer les réponses sur le sujet '{topic['name']}'")
        
        return suggestions
    
    def trigger_learning(self):
        """Déclenche un cycle d'apprentissage"""
        logger.info("Déclenchement du cycle d'apprentissage basé sur les feedbacks")
        
        # Récupère les exemples pour apprentissage
        good_examples = self.get_high_rated_examples(20)
        bad_examples = self.get_low_rated_examples(10)
        
        # Logique d'apprentissage à implémenter
        # (appel au fine_tuner)
        
        return {
            "good_examples_count": len(good_examples),
            "bad_examples_count": len(bad_examples),
            "triggered_at": datetime.now().isoformat()
        }
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques détaillées"""
        # Calculs supplémentaires
        recent = self.get_recent_feedback(50)
        avg_recent = np.mean([f.get("rating", 0) for f in recent if f.get("rating")]) if recent else 0
        
        # Évolution temporelle
        trend = []
        for i in range(0, len(self.feedback_history), 10):
            batch = self.feedback_history[i:i+10]
            if batch:
                avg = np.mean([f.get("rating", 0) for f in batch if f.get("rating")])
                trend.append({
                    "batch": i//10,
                    "average": avg
                })
        
        return {
            "total": self.stats["total_feedback"],
            "overall_average": self.stats["average_rating"],
            "recent_average": avg_recent,
            "distribution": self.stats["ratings_distribution"],
            "top_topics": sorted(
                self.stats.get("top_topics", []),
                key=lambda x: x["count"],
                reverse=True
            )[:5],
            "trend": trend[-10:],  # Dernières 10 périodes
            "improvement_suggestions": self.get_improvement_suggestions()
        }
    
    def export_for_training(self) -> List[Dict]:
        """Exporte les données pour l'entraînement"""
        training_data = []
        
        for fb in self.feedback_history:
            if fb.get("rating", 0) >= 4:  # Garde les bons exemples
                training_data.append({
                    "prompt": fb.get("prompt", ""),
                    "response": fb.get("response", ""),
                    "quality": "high"
                })
            elif fb.get("rating", 5) <= 2:  # Garde les mauvais exemples comme contre-exemples
                training_data.append({
                    "prompt": fb.get("prompt", ""),
                    "response": fb.get("response", ""),
                    "quality": "low"
                })
        
        return training_data