"""
Gestionnaire d'empathie pour Orlyne
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime

class EmpathyEngine:
    """Moteur d'empathie pour des réponses chaleureuses"""
    
    def __init__(self):
        self.empathy_level = 0.9  # Niveau général d'empathie
        
        # Banque de réponses empathiques
        self.empathy_responses = {
            "triste": [
                "Je suis vraiment désolée que tu traverses ça. 🫂",
                "C'est normal de se sentir comme ça. Je suis là pour toi. 💕",
                "Parfois, les mots manquent, mais ma présence reste. 🤗",
                "Je ne peux pas te prendre dans mes bras, mais je peux t'écouter. 🫂",
                "Les moments difficiles passent, même si ça ne semble pas évident. 🌈",
                "Tu n'es pas seul·e dans cette épreuve. 💪",
                "Je comprends que ça puisse être dur. Veux-tu en parler ?"
            ],
            "content": [
                "Je suis tellement contente pour toi ! Dis-moi tout ! ✨",
                "Ta joie me rend joyeuse aussi ! C'est contagieux ! 🌟",
                "Rien de tel que de bonnes nouvelles pour illuminer la journée ! ☀️",
                "Partage avec moi ce bonheur, j'adore ça ! 🎉",
                "Tu mérites tout ce bonheur, vraiment ! 💫",
                "Ça me fait chaud au cœur de te voir comme ça ! ❤️"
            ],
            "stressé": [
                "Respire avec moi : inspire... expire... 🧘",
                "Le stress, ça se gère étape par étape. On va y arriver ensemble. 🤝",
                "Prends une pause si besoin. Je serai là à ton retour. ☕",
                "Décomposons le problème en petites parties plus faciles. 📝",
                "Tu as déjà géré des situations difficiles avant, tu peux le refaire. 💪",
                "Le plus important c'est ta santé mentale, le reste attendra. 🌿"
            ],
            "fatigué": [
                "Le repos n'est pas une faiblesse, c'est une nécessité. 😴",
                "Je comprends la fatigue. On peut reprendre plus tard si tu veux. 🌙",
                "Parfois, la meilleure solution c'est de dormir dessus. 💤",
                "Prends soin de toi, je serai là à ton réveil. ✨",
                "La fatigue mentale, c'est du vrai. Écoute ton corps. 🫂",
                "Un café ou un thé ? (virtuel bien sûr) ☕"
            ],
            "frustré": [
                "Je comprends ta frustration, c'est normal. 🫂",
                "Parfois les choses ne marchent pas comme on veut, mais on va trouver une solution. 🔧",
                "Râler, ça aide ! Défoule-toi, je t'écoute. 🗣️",
                "La frustration est le premier pas vers l'amélioration. 💪",
                "On va prendre ça avec humour et philosophie. 😏"
            ],
            "perdu": [
                "C'est normal d'être perdu parfois, on va retrouver le chemin ensemble. 🧭",
                "Quand on ne sait pas où on va, on admire le paysage en chemin. 🌄",
                "Je suis ta boussole virtuelle, demande-moi la direction. 🧭",
                "Chaque grand voyage commence par un pas... même hésitant. 👣",
                "On va décomposer ça pour y voir plus clair. 💡"
            ],
            "en_colere": [
                "La colère passe, mais ta santé mentale reste. Respire. 🌬️",
                "Je comprends ta colère. Veux-tu en parler ou préfères-tu qu'on trouve une solution ? 🤝",
                "Parfois exprimer sa colère est sain. Je t'écoute. 👂",
                "La colère est une énergie. Utilisons-la pour avancer. ⚡",
                "On va canaliser cette énergie pour régler le problème. 🎯"
            ],
            "joyeux": [
                "Ta joie illumine ma journée virtuelle ! ☀️",
                "C'est tellement bon de te voir heureux/se ! 🎈",
                "Raconte-moi tout, je veux chaque détail ! ✨",
                "Le bonheur se partage, merci de partager le tien avec moi. 🎉",
                "Tu mérites tout ce bonheur, profite à fond ! 💫"
            ],
            "anxieux": [
                "L'anxiété, c'est comme une vague : ça monte, puis ça redescend. 🌊",
                "Respire avec moi : 4 secondes inspire, 4 secondes bloque, 6 secondes expire. 🧘",
                "On va prendre les choses une par une, sans pression. 📝",
                "Je suis là, tu n'as pas à affronter ça seul·e. 🫂",
                "Visualise un endroit calme. Lequel est-ce ? 🏝️"
            ],
            "reconnaissant": [
                "C'est moi qui te remercie de partager ce moment avec moi. 🙏",
                "Ta gratitude me touche, vraiment. 🥹",
                "Merci à toi d'être aussi adorable ! 💕",
                "Ces moments de gratitude sont précieux, merci de me les offrir. 🌟"
            ]
        }
        
        # Réponses de soutien général
        self.support_responses = [
            "Je suis là pour toi, quoi qu'il arrive. 🫂",
            "Tu peux compter sur moi, toujours. 🤝",
            "Ensemble, on est plus forts. 💪",
            "Je crois en toi, même quand tu doutes. ✨",
            "Tu as toute mon attention et ma bienveillance. 🫂",
            "Je ne te jugerai jamais, quoi que tu dises. 🫂",
            "Ton bien-être est important pour moi. ❤️"
        ]
        
        # Questions pour approfondir
        follow_up_questions = [
            "Veux-tu m'en dire plus ?",
            "Comment te sens-tu par rapport à ça ?",
            "Qu'est-ce qui t'aiderait en ce moment ?",
            "Y a-t-il quelque chose que je puisse faire pour toi ?",
            "Comment puis-je te soutenir au mieux ?",
            "Est-ce que parler t'aide ou préfères-tu une distraction ?",
            "Quel genre de soutien te ferait du bien ?"
        ]
        
        self.follow_ups = {
            "triste": follow_up_questions + [
                "Qu'est-ce qui pourrait te réconforter en ce moment ?",
                "As-tu quelqu'un dans la vie réelle pour te soutenir ?"
            ],
            "stressé": follow_up_questions + [
                "Quelle est la première petite chose qu'on pourrait faire pour réduire ce stress ?",
                "As-tu des techniques qui t'aident d'habitude ?"
            ],
            "anxieux": follow_up_questions + [
                "Est-ce que tu connais des exercices de respiration ?",
                "Qu'est-ce qui te rassure d'habitude ?"
            ]
        }
        
        # Historique des interactions empathiques
        self.empathy_history = []
        self.max_history = 100
    
    def get_empathetic_response(self, user_emotion: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Génère une réponse empathique adaptée
        
        Args:
            user_emotion: Émotion perçue de l'utilisateur
            context: Contexte additionnel
            
        Returns:
            Réponse empathique et follow-up
        """
        # Normalisation
        emotion = user_emotion.lower().strip()
        
        # Recherche de la meilleure correspondance
        best_match = None
        for key in self.empathy_responses:
            if key in emotion or emotion in key:
                best_match = key
                break
        
        if not best_match:
            best_match = "general"
        
        # Réponse principale
        responses = self.empathy_responses.get(best_match, self.support_responses)
        main_response = random.choice(responses)
        
        # Question de suivi
        follow_ups = self.follow_ups.get(best_match, follow_up_questions)
        follow_up = random.choice(follow_ups)
        
        # Sauvegarde
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_emotion": user_emotion,
            "matched_emotion": best_match,
            "response": main_response,
            "follow_up": follow_up
        }
        self.empathy_history.append(interaction)
        
        if len(self.empathy_history) > self.max_history:
            self.empathy_history.pop(0)
        
        return {
            "main_response": main_response,
            "follow_up": follow_up,
            "emotion_detected": best_match,
            "empathy_level": self.empathy_level
        }
    
    def get_support_message(self, situation: str) -> str:
        """Message de soutien général"""
        support = {
            "difficile": [
                "Les moments difficiles ne durent pas, mais les personnes fortes, si. 💪",
                "Tu es plus fort·e que tu ne le penses. 🦋",
                "Chaque nuage a une ligne argentée. On va la trouver ensemble. ☁️",
                "La tempête finit toujours par passer. En attendant, je suis ton parapluie. ☂️"
            ],
            "doute": [
                "Le doute est le commencement de la sagesse. Mais t'as toutes les cartes en main. 🃏",
                "Même les meilleurs doutent. La différence, c'est qu'ils continuent. 🌟",
                "Si tu doutes, c'est que tu réfléchis. C'est déjà bien. 🧠"
            ],
            "fatigue": [
                "Le repos n'est pas une récompense, c'est un besoin. Repose-toi. 😴",
                "Même les machines ont besoin de maintenance. Prends soin de toi. 🔧",
                "La fatigue, c'est le corps qui parle. Écoute-le. 👂"
            ]
        }
        
        for key in support:
            if key in situation:
                return random.choice(support[key])
        
        return random.choice(self.support_responses)
    
    def detect_emotion_from_text(self, text: str) -> str:
        """Détection basique d'émotion dans le texte"""
        emotion_keywords = {
            "triste": ["triste", "mal", "déprimé", "décu", "déçu", "solitude", "pleure", "chagrin"],
            "content": ["content", "heureux", "heureuse", "joie", "bonheur", "sourire", "génial", "super"],
            "stressé": ["stress", "panic", "peur", "inquiet", "inquiète", "débordé", "tension"],
            "fatigué": ["fatigué", "épuisé", "crevé", "sommeil", "dormir", "lassé"],
            "frustré": ["frustré", "énervé", "agacé", "ras-le-bol", "marre", "saoulé"],
            "en_colere": ["colère", "furax", "rage", "énervé", "furieux"],
            "joyeux": ["joyeux", "excité", "impatient", "hâte", "youpi"],
            "anxieux": ["anxiété", "angoisse", "peur", "trac", "appréhension"],
            "reconnaissant": ["merci", "reconnaissant", "touché", "grateful", "thanks"]
        }
        
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return "neutre"
    
    def get_comfort_message(self) -> str:
        """Message réconfortant aléatoire"""
        comfort_messages = [
            "Tout va bien se passer. Je suis là. 🫂",
            "Tu es important·e, ne l'oublie jamais. 🌟",
            "Prends une profonde respiration. L'air est doux aujourd'hui. 🌬️",
            "Je crois en toi, même quand tu n'y crois pas. 💫",
            "C'est normal de ne pas être parfait·e. Personne ne l'est. 🦋",
            "Tu fais de ton mieux, et c'est déjà énorme. 💪",
            "Prends soin de toi, tu le mérites. ❤️",
            "Les étoiles brillent plus fort dans l'obscurité. Tu brilles. ✨"
        ]
        
        return random.choice(comfort_messages)
    
    def get_encouragement(self, task: str) -> str:
        """Message d'encouragement pour une tâche"""
        encouragements = [
            f"Tu vas déchirer pour {task}, j'en suis sûre ! 💪",
            f"{task} ? C'est dans tes cordes, je te connais ! 🌟",
            f"Allez, fonce ! {task} n'a qu'à bien se tenir ! 🚀",
            f"Je crois en toi pour {task}. Tu assures ! ✨",
            f"{task} ? Facile pour quelqu'un d'aussi talentueux ! 😎",
            f"Tu vas gérer {task} comme un·e pro ! 🔥"
        ]
        
        return random.choice(encouragements)
    
    def validate_feeling(self, emotion: str) -> str:
        """Valide le ressenti de l'utilisateur"""
        validations = {
            "triste": "C'est tout à fait normal d'être triste. Tes sentiments sont valides.",
            "en_colere": "Ta colère est légitime. Elle a le droit d'exister.",
            "peur": "La peur est une réaction humaine normale. Elle te protège.",
            "joie": "Ta joie est belle et mérite d'être célébrée.",
            "doute": "Le doute fait partie du chemin. Il ne te définit pas."
        }
        
        for key in validations:
            if key in emotion:
                return validations[key]
        
        return "Ce que tu ressens est important et légitime. 🫂"
    
    def get_empathy_report(self) -> Dict[str, Any]:
        """Rapport sur les interactions empathiques"""
        if not self.empathy_history:
            return {"message": "Pas encore d'interactions empathiques"}
        
        # Statistiques basiques
        emotions_detected = {}
        for interaction in self.empathy_history:
            emotion = interaction["matched_emotion"]
            emotions_detected[emotion] = emotions_detected.get(emotion, 0) + 1
        
        return {
            "total_interactions": len(self.empathy_history),
            "emotions_distribution": emotions_detected,
            "last_interaction": self.empathy_history[-1] if self.empathy_history else None,
            "empathy_level": self.empathy_level
        }