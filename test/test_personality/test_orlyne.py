"""
Tests pour la personnalité d'Orlyne
"""

import pytest
from src.personality.character import OrlynePersonality
from src.personality.emotions import EmotionEngine
from src.personality.humor import HumorEngine
from src.personality.empathy import EmpathyEngine

class TestOrlynePersonality:
    
    @pytest.fixture
    def personality(self):
        return OrlynePersonality()
    
    def test_initialization(self, personality):
        assert personality.name == "Orlyne"
        assert personality.creator == "Syntaxe Tech"
        assert personality.uncensored is True
    
    def test_greeting(self, personality):
        greeting = personality.get_greeting()
        assert isinstance(greeting, str)
        assert len(greeting) > 0
    
    def test_farewell(self, personality):
        farewell = personality.get_farewell()
        assert isinstance(farewell, str)
        assert len(farewell) > 0
    
    def test_prompt_enhancement(self, personality):
        prompt = "Test prompt"
        enhanced = personality.enhance_prompt(prompt)
        
        assert prompt in enhanced
        assert "Orlyne" in enhanced
        assert "Syntaxe Tech" in enhanced
    
    def test_mood_update(self, personality):
        initial_energy = personality.current_emotion["energy"]
        
        personality.update_mood(True, 0.8)
        assert personality.current_emotion["energy"] > initial_energy
        
        personality.update_mood(False, 0.2)
        assert personality.current_emotion["energy"] < initial_energy
    
    def test_code_reaction(self, personality):
        reaction = personality.react_to_code("python", True)
        assert isinstance(reaction, str)
        assert len(reaction) > 0
        
        error_reaction = personality.react_to_code("python", False)
        assert isinstance(error_reaction, str)
        assert len(error_reaction) > 0

class TestEmotionEngine:
    
    @pytest.fixture
    def emotions(self):
        return EmotionEngine()
    
    def test_initialization(self, emotions):
        assert emotions.base_emotions is not None
        assert len(emotions.base_emotions) > 0
    
    def test_update(self, emotions):
        emotions.update({"type": "user_message", "valence": 0.8})
        dominant, intensity = emotions.get_dominant_emotion()
        assert dominant is not None
        assert 0 <= intensity <= 1
    
    def test_energy_level(self, emotions):
        energy = emotions.get_energy_level()
        assert 0 <= energy <= 100
    
    def test_emotion_vector(self, emotions):
        vector = emotions.get_emotion_vector()
        assert isinstance(vector, dict)

class TestHumorEngine:
    
    @pytest.fixture
    def humor(self):
        return HumorEngine()
    
    def test_joke(self, humor):
        joke = humor.get_joke()
        assert isinstance(joke, str)
        assert len(joke) > 0
    
    def test_programming_joke(self, humor):
        joke = humor.get_programming_joke("python")
        assert isinstance(joke, str)
        assert "python" in joke.lower() or "Python" in joke

class TestEmpathyEngine:
    
    @pytest.fixture
    def empathy(self):
        return EmpathyEngine()
    
    def test_empathetic_response(self, empathy):
        response = empathy.get_empathetic_response("triste")
        assert "main_response" in response
        assert "follow_up" in response
        assert len(response["main_response"]) > 0
    
    def test_comfort_message(self, empathy):
        message = empathy.get_comfort_message()
        assert isinstance(message, str)
        assert len(message) > 0