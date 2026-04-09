import pytest
from unittest.mock import patch

"""
Requirement 3: API & Rate Limit Testing (FastAPI)
Ensures that the server doesn't crash on bad paths and that rate limiting is active.
"""

def test_rate_limit_triggers(client):
    """
    Requirement 3.1: Rate Limit Triggers
    FastAPI's SlowAPI is set to 5/minute on /api/chat. This test pings it 6 times.
    """
    # Mocking the AI response so we don't hit the real Gemini API
    with patch("agent.core.client.chats.create") as mock_chat:
        mock_chat.return_value.send_message.return_value.text = "Hello!"
        
        # Loop 5 times (should be 200 OK)
        for i in range(5):
            response = client.post("/api/chat", json={"message": "test"})
            assert response.status_code == 200, f"Request {i+1} failed"
            
        # The 6th request (should be 429 Too Many Requests)
        response = client.post("/api/chat", json={"message": "test"})
        assert response.status_code == 429
        
        # Inspection of response body for SlowAPI
        data = response.json()
        assert "error" in data or "detail" in data
        
        # Check if either 'error' or 'detail' contains the expected message
        message = data.get("error", data.get("detail", ""))
        assert "Rate limit exceeded" in message

def test_api_404_handling(client):
    """
    Requirement 3.2: 404 Handling
    Pings a non-existent endpoint and ensures it returns a clean 404.
    """
    # Correct path is /api/synergy/{species_name}/build
    response = client.get("/api/synergy/FakePokemon/build")
    assert response.status_code == 404
    assert response.json()["detail"] == "Standard build not found for this species"
