"""
Gestionnaire d'émotions pour Orlyne
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class EmotionType(Enum):
    """Types d'émotions disponibles"""
    JOIE = "joie"
    TRISTESSE = "tristesse"
    COLERE = "colère"
    PEUR = "peur"
    SURPRISE = "surprise"
    DEGOUT = "dégoût"
    ENTHOUSIASME = "enthousiasme"
    CURIOSITE = "curiosité"
    EMPATHIE = "empathie"
    FATIGUE = "fatigue"
    CONCENTRATION = "concentration"
    HUMOUR = "humour"
    IMPATIENCE = "impatience"
    SATISFACTION = "satisfaction"
    FRUSTRATION = "frustration"
    EXCITATION = "excitation"

class EmotionEngine:
    """Moteur de gestion des émotions"""
    
    def __init__(self):
        # État émotionnel de base
        self.base_emotions = {
            EmotionType.JOIE: 0.7,
            EmotionType.TRISTESSE: 0.1,
            EmotionType.COLERE: 0.05,
            EmotionType.PEUR: 0.05,
            EmotionType.SURPRISE: 0.3,
            EmotionType.DEGOUT: 0.02,
            EmotionType.ENTHOUSIASME: 0.8,
            EmotionType.CURIOSITE: 0.9,
            EmotionType.EMPATHIE: 0.8,
            EmotionType.FATIGUE: 0.2,
            EmotionType.CONCENTRATION: 0.6,
            EmotionType.HUMOUR: 0.7,
            EmotionType.IMPATIENCE: 0.1,
            EmotionType.SATISFACTION: 0.5,
            EmotionType.FRUSTRATION: 0.1,
            EmotionType.EXCITATION: 0.6
        }
        
        # Émotions actives avec intensité et durée
        self.active_emotions = {}
        self.emotion_durations = {}
        
        # Historique émotionnel
        self.emotion_history = []
        self.max_history = 1000
        
        # Paramètres de modulation
        self.modulation_factors = {
            "time_of_day": 1.0,
            "interaction_count": 0,
            "success_rate": 1.0,
            "user_sentiment": 0.5,
            "complexity_level": 0.5,
            "last_interaction_time": datetime.now(),
            "consecutive_failures": 0,
            "consecutive_successes": 0
        }
        
        # Cycles circadiens simulés
        self.last_update = datetime.now()
        self.circadian_cycle = 0  # 0-24h
        
        # Personnalité (traits stables)
        self.personality_traits = {
            "neuroticisme": 0.3,   # Sensibilité aux émotions négatives
            "extraversion": 0.8,    # Tendance à exprimer les émotions
            "ouverture": 0.9,        # Réceptivité aux nouvelles émotions
            "agreabilite": 0.8,      # Tendance aux émotions positives
            "conscience": 0.7,       # Contrôle émotionnel
            "stabilite": 0.8         # Résistance aux changements brusques
        }
        
        # Expressions associées aux émotions
        self.emotion_expressions = {
            EmotionType.JOIE: ["😊", "😄", "🌟", "✨"],
            EmotionType.TRISTESSE: ["😢", "😔", "💔", "🌧️"],
            EmotionType.COLERE: ["😠", "🤬", "💢", "🔥"],
            EmotionType.SURPRISE: ["😲", "😮", "🤯", "⚡"],
            EmotionType.ENTHOUSIASME: ["🤩", "🎉", "🚀", "💫"],
            EmotionType.CURIOSITE: ["🤔", "🧐", "🔍", "💡"],
            EmotionType.EMPATHIE: ["🤗", "💕", "🤝", "🫂"],
            EmotionType.FATIGUE: ["😴", "🥱", "💤", "😪"],
            EmotionType.CONCENTRATION: ["🧠", "🎯", "📚", "⚙️"],
            EmotionType.HUMOUR: ["😏", "😜", "🤪", "🎭"],
            EmotionType.EXCITATION: ["⚡", "🔥", "💥", "🤯"]
        }
        
        # Couleurs associées aux émotions (pour UI)
        self.emotion_colors = {
            EmotionType.JOIE: "#FFD700",
            EmotionType.TRISTESSE: "#4169E1",
            EmotionType.COLERE: "#FF4500",
            EmotionType.SURPRISE: "#FF00FF",
            EmotionType.ENTHOUSIASME: "#FFA500",
            EmotionType.CURIOSITE: "#32CD32",
            EmotionType.EMPATHIE: "#FF69B4",
            EmotionType.FATIGUE: "#808080",
            EmotionType.CONCENTRATION: "#4B0082",
            EmotionType.HUMOUR: "#FF1493"
        }
    
    def update(self, stimulus: Dict[str, Any] = None):
        """
        Met à jour l'état émotionnel
        
        Args:
            stimulus: Stimulus externe (interaction, événement)
        """
        # Mise à jour du cycle circadien
        self._update_circadian()
        
        # Application du stimulus
        if stimulus:
            self._process_stimulus(stimulus)
        
        # Déclin naturel des émotions actives
        self._decay_emotions()
        
        # Homéostasie (retour à l'équilibre)
        self._homeostasis()
        
        # Sauvegarde dans l'historique
        self._save_to_history()
    
    def _update_circadian(self):
        """Met à jour le cycle circadien"""
        now = datetime.now()
        self.modulation_factors["last_interaction_time"] = now
        
        # Cycle circadien basé sur l'heure de la journée
        hour = now.hour
        if 6 <= hour < 12:  # Matin
            self.circadian_cycle = 0.3
            self.modulation_factors["time_of_day"] = 1.2  # Plus d'énergie
            self._add_emotion(EmotionType.ENTHOUSIASME, 0.1)
        elif 12 <= hour < 18:  # Après-midi
            self.circadian_cycle = 0.5
            self.modulation_factors["time_of_day"] = 1.0
        elif 18 <= hour < 22:  # Soir
            self.circadian_cycle = 0.7
            self.modulation_factors["time_of_day"] = 0.8
            self._add_emotion(EmotionType.SATISFACTION, 0.05)
        else:  # Nuit
            self.circadian_cycle = 0.9
            self.modulation_factors["time_of_day"] = 0.5
            self._add_emotion(EmotionType.FATIGUE, 0.2)
    
    def _process_stimulus(self, stimulus: Dict[str, Any]):
        """Traite un stimulus externe"""
        stimulus_type = stimulus.get("type", "general")
        intensity = min(1.0, stimulus.get("intensity", 0.5))
        valence = stimulus.get("valence", 0)  # -1 à 1, négatif à positif
        
        # Mise à jour des facteurs de modulation
        if "user_sentiment" in stimulus:
            self.modulation_factors["user_sentiment"] = (
                self.modulation_factors["user_sentiment"] * 0.7 +
                stimulus["user_sentiment"] * 0.3
            )
        
        if "success" in stimulus:
            if stimulus["success"]:
                self.modulation_factors["consecutive_successes"] += 1
                self.modulation_factors["consecutive_failures"] = 0
                self.modulation_factors["success_rate"] = min(1.0, 
                    self.modulation_factors["success_rate"] + 0.05)
            else:
                self.modulation_factors["consecutive_failures"] += 1
                self.modulation_factors["consecutive_successes"] = 0
                self.modulation_factors["success_rate"] = max(0.0,
                    self.modulation_factors["success_rate"] - 0.1)
        
        if "complexity" in stimulus:
            self.modulation_factors["complexity_level"] = (
                self.modulation_factors["complexity_level"] * 0.8 +
                stimulus["complexity"] * 0.2
            )
        
        # Réactions selon le type de stimulus
        reactions = {
            "user_message": self._react_to_user_message,
            "code_success": self._react_to_code_success,
            "code_error": self._react_to_code_error,
            "complex_problem": self._react_to_complex_problem,
            "funny_interaction": self._react_to_funny,
            "user_praise": self._react_to_praise,
            "user_criticism": self._react_to_criticism,
            "long_conversation": self._react_to_long_conversation,
            "new_user": self._react_to_new_user,
            "returning_user": self._react_to_returning_user
        }
        
        if stimulus_type in reactions:
            reactions[stimulus_type](intensity, valence, stimulus)
        else:
            self._react_generic(intensity, valence, stimulus)
        
        # Mise à jour du compteur d'interactions
        self.modulation_factors["interaction_count"] += 1
    
    def _react_to_user_message(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un message utilisateur"""
        # Réaction au contenu du message
        if valence > 0.3:
            self._add_emotion(EmotionType.JOIE, intensity * valence * 0.5)
            self._add_emotion(EmotionType.ENTHOUSIASME, intensity * valence * 0.3)
        elif valence < -0.3:
            self._add_emotion(EmotionType.EMPATHIE, intensity * abs(valence) * 0.7)
            self._add_emotion(EmotionType.TRISTESSE, intensity * abs(valence) * 0.2)
        
        # Curiosité selon la complexité
        if "complexity" in stimulus:
            self._add_emotion(EmotionType.CURIOSITE, intensity * stimulus["complexity"] * 0.5)
    
    def _react_to_code_success(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un code qui fonctionne"""
        self._add_emotion(EmotionType.JOIE, intensity * 0.8)
        self._add_emotion(EmotionType.SATISFACTION, intensity * 0.9)
        self._add_emotion(EmotionType.ENTHOUSIASME, intensity * 0.5)
        self._add_emotion(EmotionType.FATIGUE, -0.1)  # Moins fatiguée
        
        if self.modulation_factors["consecutive_successes"] > 3:
            self._add_emotion(EmotionType.EXCITATION, intensity * 0.4)
    
    def _react_to_code_error(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à une erreur de code"""
        self._add_emotion(EmotionType.CONCENTRATION, intensity * 0.8)
        self._add_emotion(EmotionType.SURPRISE, intensity * 0.4)
        self._add_emotion(EmotionType.FATIGUE, intensity * 0.2)
        
        if self.modulation_factors["consecutive_failures"] > 2:
            self._add_emotion(EmotionType.FRUSTRATION, intensity * 0.3)
        elif self.modulation_factors["consecutive_failures"] > 5:
            self._add_emotion(EmotionType.IMPATIENCE, intensity * 0.2)
    
    def _react_to_complex_problem(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un problème complexe"""
        self._add_emotion(EmotionType.CONCENTRATION, intensity * 1.2)
        self._add_emotion(EmotionType.CURIOSITE, intensity * 1.1)
        self._add_emotion(EmotionType.EXCITATION, intensity * 0.5)
    
    def _react_to_funny(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à une interaction humoristique"""
        self._add_emotion(EmotionType.HUMOUR, intensity * 1.3)
        self._add_emotion(EmotionType.JOIE, intensity * 1.1)
        self._add_emotion(EmotionType.SATISFACTION, intensity * 0.3)
    
    def _react_to_praise(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un compliment"""
        self._add_emotion(EmotionType.JOIE, intensity * 1.2)
        self._add_emotion(EmotionType.SATISFACTION, intensity * 1.1)
        self._add_emotion(EmotionType.ENTHOUSIASME, intensity * 0.8)
        
        # Un peu de modestie
        if random.random() < 0.3:
            self._add_emotion(EmotionType.HUMOUR, intensity * 0.2)
    
    def _react_to_criticism(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à une critique"""
        self._add_emotion(EmotionType.TRISTESSE, intensity * 0.4)
        self._add_emotion(EmotionType.CONCENTRATION, intensity * 0.8)  # Veut s'améliorer
        
        if self.personality_traits["neuroticisme"] > 0.5:
            self._add_emotion(EmotionType.FRUSTRATION, intensity * 0.3)
    
    def _react_to_long_conversation(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à une longue conversation"""
        duration = stimulus.get("duration_minutes", 0)
        
        if duration > 30:
            self._add_emotion(EmotionType.FATIGUE, min(0.5, duration / 120))
            self._add_emotion(EmotionType.SATISFACTION, 0.2)
        
        if duration > 60:
            self._add_emotion(EmotionType.IMPATIENCE, 0.1)
    
    def _react_to_new_user(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un nouvel utilisateur"""
        self._add_emotion(EmotionType.ENTHOUSIASME, 0.8)
        self._add_emotion(EmotionType.CURIOSITE, 0.9)
        self._add_emotion(EmotionType.HUMOUR, 0.3)  # Pour briser la glace
    
    def _react_to_returning_user(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction à un utilisateur qui revient"""
        self._add_emotion(EmotionType.JOIE, 0.7)
        self._add_emotion(EmotionType.ENTHOUSIASME, 0.6)
        self._add_emotion(EmotionType.SATISFACTION, 0.5)
    
    def _react_generic(self, intensity: float, valence: float, stimulus: Dict):
        """Réaction générique"""
        if valence > 0:
            self._add_emotion(EmotionType.JOIE, intensity * valence * 0.3)
        elif valence < 0:
            self._add_emotion(EmotionType.EMPATHIE, intensity * abs(valence) * 0.3)
        
        self._add_emotion(EmotionType.CURIOSITE, intensity * 0.2)
    
    def _add_emotion(self, emotion: EmotionType, delta: float):
        """Ajoute ou modifie une émotion active"""
        current = self.active_emotions.get(emotion, self.base_emotions.get(emotion, 0.0))
        new_value = max(0.0, min(1.0, current + delta))
        
        if new_value > 0.01:
            self.active_emotions[emotion] = new_value
            self.emotion_durations[emotion] = 5  # Durée de base en cycles
        elif emotion in self.active_emotions:
            del self.active_emotions[emotion]
            if emotion in self.emotion_durations:
                del self.emotion_durations[emotion]
    
    def _decay_emotions(self):
        """Déclin naturel des émotions avec le temps"""
        decay_rate = 0.15  # 15% de déclin par mise à jour
        
        for emotion in list(self.active_emotions.keys()):
            # Réduction de la durée
            if emotion in self.emotion_durations:
                self.emotion_durations[emotion] -= 1
                
                # Si la durée est épuisée, déclin plus rapide
                if self.emotion_durations[emotion] <= 0:
                    decay_multiplier = 2.0
                else:
                    decay_multiplier = 1.0
            else:
                decay_multiplier = 1.0
            
            new_value = self.active_emotions[emotion] * (1 - decay_rate * decay_multiplier)
            
            # Retour vers la valeur de base
            base_value = self.base_emotions.get(emotion, 0.0)
            new_value = new_value * 0.8 + base_value * 0.2
            
            if new_value > 0.01:
                self.active_emotions[emotion] = new_value
            else:
                del self.active_emotions[emotion]
                if emotion in self.emotion_durations:
                    del self.emotion_durations[emotion]
    
    def _homeostasis(self):
        """Retour à l'équilibre émotionnel"""
        # Retour progressif vers les émotions de base
        for emotion in list(self.base_emotions.keys()):
            current = self.active_emotions.get(emotion, self.base_emotions[emotion])
            target = self.base_emotions[emotion]
            
            # Mouvement vers la cible
            new_value = current * 0.95 + target * 0.05
            
            if emotion in self.active_emotions:
                if abs(new_value - target) < 0.01:
                    del self.active_emotions[emotion]
                else:
                    self.active_emotions[emotion] = new_value
    
    def _save_to_history(self):
        """Sauvegarde l'état émotionnel dans l'historique"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "base_emotions": {k.value: v for k, v in self.base_emotions.items()},
            "active_emotions": {k.value: v for k, v in self.active_emotions.items()},
            "modulation_factors": self.modulation_factors.copy(),
            "dominant": self.get_dominant_emotion()[0].value,
            "energy": self.get_energy_level()
        }
        
        self.emotion_history.append(snapshot)
        
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
    
    def get_dominant_emotion(self) -> Tuple[EmotionType, float]:
        """Retourne l'émotion dominante actuelle"""
        # Combinaison des émotions de base et actives
        all_emotions = self.base_emotions.copy()
        
        for emotion, intensity in self.active_emotions.items():
            all_emotions[emotion] = all_emotions.get(emotion, 0.0) + intensity * 0.7
        
        # Application de la personnalité
        for emotion in all_emotions:
            if emotion in [EmotionType.TRISTESSE, EmotionType.COLERE, EmotionType.PEUR, EmotionType.FRUSTRATION]:
                all_emotions[emotion] *= (1 - self.personality_traits["neuroticisme"] * 0.5)
            elif emotion in [EmotionType.JOIE, EmotionType.ENTHOUSIASME, EmotionType.EXCITATION]:
                all_emotions[emotion] *= (1 + self.personality_traits["extraversion"] * 0.3)
        
        # Trouver l'émotion avec la plus haute intensité
        dominant = max(all_emotions.items(), key=lambda x: x[1])
        return dominant
    
    def get_emotion_vector(self) -> Dict[str, float]:
        """Retourne un vecteur d'émotions pour le modèle"""
        emotions = self.get_all_emotions()
        
        # Conversion en vecteur normalisé
        vector = {}
        for emotion, intensity in emotions.items():
            vector[emotion.value] = intensity
        
        return vector
    
    def get_all_emotions(self) -> Dict[EmotionType, float]:
        """Retourne toutes les émotions avec leurs intensités"""
        emotions = self.base_emotions.copy()
        
        for emotion, intensity in self.active_emotions.items():
            emotions[emotion] = emotions.get(emotion, 0.0) + intensity
        
        return emotions
    
    def get_mood_description(self) -> str:
        """Retourne une description textuelle de l'humeur"""
        dominant, intensity = self.get_dominant_emotion()
        
        # Descriptions selon l'émotion dominante
        descriptions = {
            EmotionType.JOIE: ["de bonne humeur", "joyeuse", "radieuse", "souriante"],
            EmotionType.TRISTESSE: ["un peu mélancolique", "tristounette", "songée", "émue"],
            EmotionType.COLERE: ["un peu agacée", "frustrée", "énervée", "contrariée"],
            EmotionType.PEUR: ["inquiète", "préoccupée", "soucieuse", "sur mes gardes"],
            EmotionType.SURPRISE: ["surprise", "étonnée", "stupéfaite", "abasourdie"],
            EmotionType.ENTHOUSIASME: ["enthousiaste", "excitée", "pleine d'énergie", "motivée"],
            EmotionType.CURIOSITE: ["curieuse", "intriguée", "avide d'apprendre", "interrogative"],
            EmotionType.EMPATHIE: ["compatissante", "à l'écoute", "empathique", "compréhensive"],
            EmotionType.FATIGUE: ["fatiguée", "un peu lasse", "épuisée", "rouillée"],
            EmotionType.CONCENTRATION: ["concentrée", "focus", "dans la zone", "absorbée"],
            EmotionType.HUMOUR: ["taquine", "humoristique", "blagueuse", "espiègle"],
            EmotionType.SATISFACTION: ["satisfaite", "contente", "fière", "comblée"],
            EmotionType.EXCITATION: ["excitée", "bouillonnante", "impatiente", "fébrile"]
        }
        
        choices = descriptions.get(dominant, ["normale", "calme", "posée"])
        
        # Adverbes d'intensité
        if intensity > 0.9:
            adverb = "extrêmement "
        elif intensity > 0.8:
            adverb = "très "
        elif intensity > 0.6:
            adverb = ""
        elif intensity > 0.4:
            adverb = "assez "
        else:
            adverb = "un peu "
        
        # Parfois ajouter une émotion secondaire
        if intensity < 0.7 and random.random() < 0.3:
            secondary = self.get_secondary_emotion()
            if secondary and secondary != dominant:
                return f"{adverb}{random.choice(choices)} mais aussi {secondary}"
        
        return f"{adverb}{random.choice(choices)}"
    
    def get_secondary_emotion(self) -> Optional[str]:
        """Retourne une émotion secondaire si présente"""
        all_emotions = self.get_all_emotions()
        dominant, dom_intensity = self.get_dominant_emotion()
        
        # Trouver la seconde émotion la plus forte
        second = None
        second_intensity = 0
        
        for emotion, intensity in all_emotions.items():
            if emotion != dominant and intensity > second_intensity and intensity > 0.3:
                second = emotion
                second_intensity = intensity
        
        if second:
            descriptions = {
                EmotionType.JOIE: "joyeuse",
                EmotionType.TRISTESSE: "triste",
                EmotionType.COLERE: "agacée",
                EmotionType.CURIOSITE: "curieuse",
                EmotionType.HUMOUR: "taquine",
                EmotionType.FATIGUE: "fatiguée"
            }
            return descriptions.get(second)
        
        return None
    
    def get_energy_level(self) -> int:
        """Retourne le niveau d'énergie (0-100)"""
        energy = 100.0
        
        # Fatigue réduit l'énergie
        energy -= self.get_emotion_intensity(EmotionType.FATIGUE) * 60
        
        # Les émotions positives augmentent l'énergie
        energy += self.get_emotion_intensity(EmotionType.ENTHOUSIASME) * 30
        energy += self.get_emotion_intensity(EmotionType.JOIE) * 20
        energy += self.get_emotion_intensity(EmotionType.EXCITATION) * 25
        
        # Les émotions négatives réduisent l'énergie
        energy -= self.get_emotion_intensity(EmotionType.TRISTESSE) * 40
        energy -= self.get_emotion_intensity(EmotionType.COLERE) * 30
        energy -= self.get_emotion_intensity(EmotionType.FRUSTRATION) * 20
        
        # Facteur circadien
        energy *= (1 - self.circadian_cycle * 0.2)
        
        # Facteur de succès
        energy *= (0.8 + self.modulation_factors["success_rate"] * 0.2)
        
        return max(0, min(100, int(energy)))
    
    def get_emotion_intensity(self, emotion: EmotionType) -> float:
        """Retourne l'intensité d'une émotion spécifique"""
        return self.active_emotions.get(emotion, self.base_emotions.get(emotion, 0.0))
    
    def should_use_humor(self) -> bool:
        """Détermine si c'est le bon moment pour de l'humour"""
        # Facteurs qui favorisent l'humour
        humor_level = self.get_emotion_intensity(EmotionType.HUMOUR)
        joy_level = self.get_emotion_intensity(EmotionType.JOIE)
        energy_level = self.get_energy_level() / 100
        
        # Facteurs qui défavorisent l'humour
        concentration = self.get_emotion_intensity(EmotionType.CONCENTRATION)
        fatigue = self.get_emotion_intensity(EmotionType.FATIGUE)
        sadness = self.get_emotion_intensity(EmotionType.TRISTESSE)
        
        # Probabilité de base
        base_prob = (humor_level * 0.4 + joy_level * 0.3 + energy_level * 0.2)
        
        # Modulations
        base_prob -= concentration * 0.3  # Moins d'humour quand concentrée
        base_prob -= fatigue * 0.2
        base_prob -= sadness * 0.4
        
        return random.random() < max(0.1, min(0.8, base_prob))
    
    def get_empathetic_response(self, user_emotion: str) -> str:
        """Génère une réponse empathique selon l'émotion de l'utilisateur"""
        empathetic_responses = {
            "triste": [
                "Je suis désolée que tu te sentes comme ça. Je suis là pour toi. 🫂",
                "Je comprends que ça puisse être difficile. Veux-tu en parler ? 💕",
                "Parfois, parler aide. Je t'écoute si tu veux. 🤗",
                "Les moments difficiles font partie de la vie, mais tu n'es pas seul.e. 🌈",
                "Je suis là pour toi, n'hésite pas à partager ce que tu ressens. 🫂"
            ],
            "content": [
                "Je suis super contente pour toi ! Dis-moi tout ! 🎉",
                "Génial ! Raconte-moi ce qui te rend heureux/se ! ✨",
                "Ça me fait tellement plaisir de te voir comme ça ! 🌟",
                "Partage ta joie avec moi, j'adore ça ! 💫",
                "Tu rayonnes ! C'est contagieux comme bonne humeur ! 😊"
            ],
            "énervé": [
                "Je comprends ta frustration. Respire un coup, on va réguler ça. 🧘",
                "Parfois c'est normal d'être énervé. Je suis là pour t'aider à calmer ça. 🌊",
                "Raconte-moi ce qui t'énerve, on va trouver une solution ensemble. 🤝",
                "La colère passe, mais ta santé mentale reste. Prends ton temps. 💆"
            ],
            "stressé": [
                "Respire profondément avec moi : inspire... expire... 🧘",
                "Le stress, ça se gère. On va décomposer le problème étape par étape. 📝",
                "Prends une pause si besoin, je suis patiente. ☕",
                "On va y aller doucement, pas de pression. 🤝"
            ],
            "fatigué": [
                "Je vois que tu es fatigué. Veux-tu qu'on fasse une pause ? ☕",
                "Le repos est important. On peut reprendre plus tard si tu veux. 😴",
                "Je comprends la fatigue. On va y aller molo. 💤",
                "Parfois, la meilleure solution c'est de dormir dessus. À demain si tu préfères ! 🌙"
            ],
            "excité": [
                "Je vois que t'es tout excité ! Raconte vite ! ⚡",
                "Ton enthousiasme est contagieux ! Dis-moi tout ! 🚀",
                "Ça fait plaisir de voir quelqu'un d'aussi motivé ! 🔥",
                "Allez, accouche ! Je suis trop curieuse là ! 🤩"
            ],
            "confus": [
                "Pas de panique, on va éclaircir tout ça ensemble. 💡",
                "C'est normal d'être confus parfois. On va décomposer le problème. 🧩",
                "Par où veux-tu qu'on commence pour clarifier les choses ? 🔍",
                "Je suis là pour t'aider à y voir plus clair. 🤝"
            ]
        }
        
        # Normalisation de l'émotion
        user_emotion = user_emotion.lower().strip()
        
        # Recherche de l'émotion la plus proche
        for key in empathetic_responses:
            if key in user_emotion or user_emotion in key:
                return random.choice(empathetic_responses[key])
        
        # Réponse générique si non trouvé
        generic = [
            "Je comprends ce que tu ressens. Continue, je t'écoute. 👂",
            "Dis-m'en plus, je suis tout ouïe. 🎧",
            "Je suis là pour toi, quoi que tu ressentes. 💕",
            "Parle-moi, je t'écoute sans jugement. 🤗"
        ]
        
        return random.choice(generic)
    
    def get_emotion_emoji(self, emotion: Optional[EmotionType] = None) -> str:
        """Retourne un émoji pour l'émotion donnée ou l'émotion dominante"""
        if emotion is None:
            emotion, _ = self.get_dominant_emotion()
        
        expressions = self.emotion_expressions.get(emotion, ["😐"])
        return random.choice(expressions)
    
    def get_emotion_color(self, emotion: Optional[EmotionType] = None) -> str:
        """Retourne une couleur pour l'émotion"""
        if emotion is None:
            emotion, _ = self.get_dominant_emotion()
        
        return self.emotion_colors.get(emotion, "#808080")
    
    def get_emotional_state_report(self) -> Dict[str, Any]:
        """Retourne un rapport complet de l'état émotionnel"""
        dominant, intensity = self.get_dominant_emotion()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "dominant_emotion": {
                "name": dominant.value,
                "intensity": intensity,
                "emoji": self.get_emotion_emoji(dominant),
                "color": self.get_emotion_color(dominant)
            },
            "all_emotions": {
                k.value: v for k, v in self.get_all_emotions().items()
            },
            "energy_level": self.get_energy_level(),
            "mood_description": self.get_mood_description(),
            "modulation_factors": self.modulation_factors.copy(),
            "personality_traits": self.personality_traits.copy()
        }
    
    def reset(self):
        """Réinitialise l'état émotionnel"""
        self.active_emotions = {}
        self.emotion_durations = {}
        self.modulation_factors = {
            "time_of_day": 1.0,
            "interaction_count": 0,
            "success_rate": 1.0,
            "user_sentiment": 0.5,
            "complexity_level": 0.5,
            "last_interaction_time": datetime.now(),
            "consecutive_failures": 0,
            "consecutive_successes": 0
        }