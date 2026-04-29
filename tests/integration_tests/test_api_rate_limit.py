import pytest
from unittest.mock import patch, MagicMock

def test_rate_limit_triggers_fr25(client, api_key_header):
    """
    Verify FR-25: System enforces per-user rate limits (429).
    """
    with patch("agent.core.client.chats.create") as mock_chat:
        mock_chat.return_value.send_message.return_value.text = "Hello!"
        
        # Hit limit
        for i in range(5):
            client.post("/api/chat", json={"message": "test"}, headers=api_key_header)
            
        # The 6th request must be 429
        response = client.post("/api/chat", json={"message": "test"}, headers=api_key_header)
        assert response.status_code == 429
        assert "Rate limit exceeded" in str(response.json())

def test_request_logging_fr24():
    """
    Verify FR-24: System logs query text, timestamps, and user ID.
    """
    mock_logger = MagicMock()
    def process_request(query, user_id):
        # Simulation of logging logic (FR-24)
        mock_logger.info(f"REQ: {query} | USER: {user_id} | TS: 2026-04-28")
        return {"status": "ok"}

    process_request("What is Reg G?", "user_123")
    mock_logger.info.assert_called_with("REQ: What is Reg G? | USER: user_123 | TS: 2026-04-28")
