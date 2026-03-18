"""
Tests pour les routes API
"""

import pytest
from fastapi.testclient import TestClient
from src.api.routes import create_app
from src.core.engine import OrlyneEngine

class TestAPI:
    
    @pytest.fixture
    def client(self):
        engine = OrlyneEngine()
        app = create_app(engine)
        return TestClient(app)
    
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_chat_endpoint(self, client):
        response = client.post(
            "/api/chat",
            json={"prompt": "Test message"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "model" in data
    
    def test_code_execution(self, client):
        response = client.post(
            "/api/code/execute",
            json={
                "code": "print('Hello')",
                "language": "python"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "output" in data
    
    def test_languages_endpoint(self, client):
        response = client.get("/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0
    
    def test_status_endpoint(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_feedback_endpoint(self, client):
        response = client.post(
            "/api/feedback",
            json={
                "prompt": "Test",
                "response": "Test response",
                "rating": 5,
                "feedback": "Great!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_invalid_chat(self, client):
        response = client.post(
            "/api/chat",
            json={}  # Missing prompt
        )
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self, client):
        # Test avec rate limiting activé
        for _ in range(5):
            response = client.post(
                "/api/chat",
                json={"prompt": "Test"}
            )
            # Juste vérifier que ça ne crash pas
            assert response.status_code in [200, 429]