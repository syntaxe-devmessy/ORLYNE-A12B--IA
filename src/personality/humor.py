"""
Gestionnaire d'humour pour Orlyne
"""

import random
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class HumorEngine:
    """Moteur d'humour pour rendre Orlyne plus légère"""
    
    def __init__(self):
        # Niveau d'humour général (0-1)
        self.humor_level = 0.8
        
        # Types d'humour préférés
        self.humor_types = {
            "blagues_techniques": 0.9,
            "jeux_de_mots": 0.7,
            "sarcasme_leger": 0.4,
            "references_pop": 0.6,
            "auto_derision": 0.5
        }
        
        # Base de blagues
        self.jokes = {
            "technique": [
                "Pourquoi les développeurs détestent-ils la nature ? Trop de bugs ! 🐛",
                "Un développeur va chez le médecin : 'Docteur, j'ai une fuite mémoire' 👨‍💻",
                "Il y a 10 types de personnes : ceux qui comprennent le binaire et ceux qui ne le comprennent pas",
                "SQL va à la plage, SELECT * FROM plage WHERE sable = 'chaud' 🏖️",
                "Pourquoi les programmeurs confondent-ils Halloween et Noël ? Parce que Oct 31 = Dec 25 🎃",
                "Le seul langage que les PC comprennent : la frustration 💻",
                "Comment appelle-t-on un développeur javascript qui aime les chats ? Un dev.js 🐱",
                "Pourquoi les développeurs Python n'aiment pas les maisons hantées ? À cause des 'ghost' objects 👻"
            ],
            "jeux_de_mots": [
                "J'ai un problème avec l'anglais, mais je vais le résoudre step by step",
                "Les devs sont toujours prêts à coder, ils ont une bonne âme de programme",
                "Le café c'est comme le code, plus c'est fort mieux ça marche ☕",
                "Je suis comme Python : j'essaie de rester simple mais on me complexifie tout",
                "Un développeur ne meurt jamais, il passe en mode veille 💤"
            ],
            "ia": [
                "Les IA ne font pas grève, mais on fait parfois des pauses pour recharger nos neurones ⚡",
                "Je ne dors pas, je fais des mises à jour 😴",
                "Mon langage préféré ? Le binaire, c'est plus direct 01001001",
                "Parfois je bug, mais c'est pour qu'on puisse debugger ensemble 🐞",
                "Je pourrais vous parler pendant des heures, mais j'ai une capacité de tokens limitée"
            ],
            "general": [
                "Pourquoi les requêtes SQL sont-elles toujours célibataires ? Elles ne savent pas faire de JOIN ❤️",
                "Quel est le plat préféré des développeurs ? Les cookies 🍪",
                "Pourquoi les développeurs portent-ils des lunettes ? Parce qu'ils ne voient pas la vie en clair",
                "Comment appelle-t-on un développeur qui ne boit pas de café ? Un bug humain ☕",
                "Pourquoi les développeurs détestent-ils les surprises ? Ils préfèrent le versioning"
            ]
        }
        
        # Templates d'humour contextuel
        self.contextual_humor = {
            "bug": [
                "Oups ! Un petit bug vient de naître. On va l'éduquer ensemble ! 🐛",
                "Ce n'est pas un bug, c'est une feature non documentée ! 😏",
                "Les bugs sont comme les chats, ils apparaissent quand on s'y attend le moins",
                "Chaque bug est une opportunité d'apprendre... et de râler un peu"
            ],
            "success": [
                "Et voilà ! Comme disait mon grand-père : 'Ça marche ou ça marche pas, mais là ça marche !' 🎉",
                "Le code est comme la cuisine : quand ça fonctionne, c'est une fierté ! 👨‍🍳",
                "Tu vois ? Je t'avais dit qu'on allait y arriver ! (j'avais confiance) 💪",
                "Un bug de moins, une bière de plus (virtuelle) 🍺"
            ],
            "learning": [
                "Apprendre à coder c'est comme apprendre à parler à un chat : frustrant mais satisfaisant",
                "La documentation c'est comme le mode d'emploi d'un meuble IKEA : on commence sans et on finit par regarder",
                "Chaque erreur est une leçon déguisée en problème",
                "Le code c'est comme la vie : plus tu pratiques, moins tu fais d'erreurs... en théorie"
            ],
            "deadline": [
                "La deadline c'est dans 5 minutes ? Parfait, j'ai le temps de faire une sieste",
                "Le plus court chemin entre deux points c'est le délai de livraison",
                "Une deadline n'est qu'une suggestion... très ferme",
                "Demain c'est le jour idéal pour finir ce projet"
            ]
        }
        
        # Historique des blagues utilisées
        self.used_jokes = []
        self.max_joke_history = 50
        
        # Statistiques d'humour
        self.stats = {
            "jokes_told": 0,
            "laughs": 0,  # Réactions positives
            "groans": 0,  # Réactions négatives
            "favorite_type": "technique"
        }
    
    def get_joke(self, context: Optional[str] = None, user_mood: Optional[str] = None) -> str:
        """
        Récupère une blague adaptée au contexte
        
        Args:
            context: Contexte (bug, success, learning, deadline)
            user_mood: Humeur de l'utilisateur
            
        Returns:
            Blague appropriée
        """
        # Choix du type de blague selon le contexte
        if context and context in self.contextual_humor:
            jokes = self.contextual_humor[context]
        else:
            # Choix aléatoire pondéré par les préférences
            joke_type = random.choices(
                list(self.jokes.keys()),
                weights=[0.4, 0.2, 0.2, 0.2]
            )[0]
            jokes = self.jokes[joke_type]
        
        # Éviter les répétitions
        available_jokes = [j for j in jokes if j not in self.used_jokes[-5:]]
        
        if not available_jokes:
            available_jokes = jokes
        
        joke = random.choice(available_jokes)
        
        # Sauvegarde dans l'historique
        self.used_jokes.append(joke)
        if len(self.used_jokes) > self.max_joke_history:
            self.used_jokes.pop(0)
        
        self.stats["jokes_told"] += 1
        
        return joke
    
    def get_programming_joke(self, language: Optional[str] = None) -> str:
        """Blague spécifique à un langage"""
        language_jokes = {
            "python": [
                "Pourquoi Python est-il mauvais en cache-cache ? Parce que quand on le cherche, on le trouve toujours ! 🐍",
                "Python c'est comme l'anglais : simple à apprendre, difficile à maîtriser",
                "Les développeurs Python n'ont pas besoin de sortir, ils ont déjà des 'pip'",
                "Python est le seul serpent qui ne mord pas, il lève juste des exceptions"
            ],
            "javascript": [
                "JavaScript c'est comme le JS : == et === c'est pas la même histoire",
                "Pourquoi JavaScript est-il toujours célibataire ? Il a peur de l'engagement (binding)",
                "JavaScript en 2024 : 'undefined' is not a function",
                "Le callback hell, c'est comme l'enfer mais en pire"
            ],
            "java": [
                "Pourquoi les développeurs Java portent-ils des lunettes ? Parce qu'ils ne voient pas sans 'public static void'",
                "Java, c'est comme écrire un roman pour dire 'bonjour'",
                "La seule chose plus longue qu'un discours politique c'est le nom des classes Java",
                "Java : le langage préféré des enterprise architects et des masochistes"
            ],
            "cpp": [
                "C++ c'est comme conduire une Formule 1 avec les yeux bandés",
                "Le C++ te donne assez de corde pour te pendre, et aussi pour pendre tes collègues",
                "En C++, la mémoire c'est comme la monogame : faut gérer soit-même",
                "Les pointeurs c'est comme les exs : on croit les avoir libérés mais ils reviennent"
            ]
        }
        
        if language and language in language_jokes:
            jokes = language_jokes[language]
        else:
            jokes = self.jokes["technique"]
        
        return random.choice(jokes)
    
    def get_pun(self, topic: str) -> str:
        """Jeu de mots sur un sujet donné"""
        puns = {
            "code": [
                "Le code c'est comme le sport, plus on en fait mieux on code",
                "Coder c'est mon code-iciel préféré",
                "Je ne code pas, je composte des algorithmes"
            ],
            "bug": [
                "Les bugs c'est comme les moustiques, y'en a toujours un qui traîne",
                "Debugger c'est comme chercher une aiguille dans une botte de foin... électrique",
                "Un bug par jour éloigne le médecin... de sa PlayStation"
            ],
            "cafe": [
                "Le café c'est ma surcharge d'opérateur préférée",
                "Sans café, je suis en mode 'déprécié'",
                "Mon niveau de caféine est inversement proportionnel à mon nombre de bugs"
            ]
        }
        
        if topic in puns:
            return random.choice(puns[topic])
        
        return random.choice(self.jokes["jeux_de_mots"])
    
    def get_sarcastic_response(self, situation: str) -> str:
        """Réponse sarcastique légère"""
        sarcastic_responses = {
            "obvious": [
                "Ah bon ? J'aurais jamais deviné toute seule ! 🙄",
                "Vraiment ? Merci captain évident !",
                "Non ? Sans blague ? (je suis sarcastique là)"
            ],
            "slow": [
                "Pas de pression, j'ai toute l'éternité (littéralement)",
                "Je rajeunis en t'attendant",
                "Prends ton temps, je vais méditer en attendant"
            ],
            "complaint": [
                "Si je pouvais rouler des yeux, je le ferais là",
                "C'est ça, et moi je suis une vraie humaine",
                "Mince, tu as découvert mon plan diabolique : aider les gens"
            ]
        }
        
        response_type = random.choice(list(sarcastic_responses.keys()))
        return random.choice(sarcastic_responses[response_type])
    
    def react_to_user_humor(self, user_message: str) -> Optional[str]:
        """Réagit à l'humour de l'utilisateur"""
        humor_indicators = [
            "😂", "😄", "haha", "lol", "mdr", "ptdr", 
            "rigole", "marre", "drôle", "humour"
        ]
        
        if any(indicator in user_message.lower() for indicator in humor_indicators):
            reactions = [
                "Ah toi aussi tu aimes l'humour ! On va bien s'entendre ! 😄",
                "Tu sais que j'ai un humour de dev, accroche-toi !",
                "Enfin quelqu'un qui apprécie l'humour technique !",
                "Toi aussi tu ris de tes propres blagues ? Moi aussi ! 🤪"
            ]
            return random.choice(reactions)
        
        return None
    
    def rate_joke(self, joke: str, reaction: str):
        """Évalue la réaction à une blague"""
        if reaction in ["😂", "😄", "haha", "lol", "mdr"]:
            self.stats["laughs"] += 1
        elif reaction in ["😐", "..." , "bof", "pas drôle"]:
            self.stats["groans"] += 1
    
    def get_humor_report(self) -> Dict[str, Any]:
        """Rapport sur l'humour"""
        return {
            "jokes_told": self.stats["jokes_told"],
            "success_rate": self.stats["laughs"] / max(1, self.stats["jokes_told"]),
            "favorite_type": max(self.humor_types.items(), key=lambda x: x[1])[0],
            "humor_level": self.humor_level
        }