"""
Module de personnalité d'Orlyne
"""

from src.personality.character import OrlynePersonality
from src.personality.prompts import PromptTemplates
from src.personality.memory import ConversationMemory
from src.personality.emotions import EmotionEngine
from src.personality.humor import HumorEngine
from src.personality.empathy import EmpathyEngine

__all__ = [
    "OrlynePersonality",
    "PromptTemplates",
    "ConversationMemory",
    "EmotionEngine",
    "HumorEngine",
    "EmpathyEngine"
]