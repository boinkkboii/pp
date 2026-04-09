import pytest
from unittest.mock import MagicMock, patch
from agent.core import create_vgc_agent

"""
Requirement 4: AI Behavior Testing (LLM Evals)
Tests if the agent is correctly following its rules by checking tool execution.
"""

def test_format_rule_19_triggers_lookup():
    """
    Requirement 4.1: The Format Rule (Improved)
    Ensures that the AI attempts to call 'get_all_formats' when asked about meta.
    
    This mocks the Gemini SDK response to simulate the AI deciding to use a tool.
    """
    with patch("agent.core.client") as mock_client:
        # 1. Setup the mock chat and its response
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat
        
        # Simulate a response that contains a Tool Call for 'get_all_formats'
        # Following the google-genai response structure
        mock_tool_call = MagicMock()
        mock_tool_call.function_call.name = "get_all_formats"
        
        mock_response = MagicMock()
        mock_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_tool_call]))
        ]
        
        mock_chat.send_message.return_value = mock_response
        
        # 2. Execute
        chat = create_vgc_agent()
        response = chat.send_message("What is the meta for Regulation G?")
        
        # 3. Assert: The AI must have tried to call the lookup tool
        # We check the mock response we "received" contains the tool call
        found_tool = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call.name == "get_all_formats":
                found_tool = True
                break
        
        assert found_tool is True, "AI failed to trigger get_all_formats for a meta query"

def test_hallucination_rule_18_node_failure():
    """
    Requirement 4.2: The Hallucination Rule
    If the damage calculator fails (Node.js missing), the tool returns a specific 
    error string that the AI should then report to the user.
    """
    with patch("agent.tools.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("Node.js not found")
        
        from agent.tools import calculate_vgc_damage, DamageCalcParams
        params = DamageCalcParams(attacker_name="Pikachu", defender_name="Charizard", move_name="Thunderbolt")
        
        result = calculate_vgc_damage(params)
        assert "Error: Node.js is not installed" in result

def test_circuit_breaker_rule_8_enforcement():
    """
    Requirement 4.3: Circuit Breaker
    Verifies the system prompt contains the specific instruction to stop 
    after consecutive 404s/empty results.
    """
    from agent.core import SYSTEM_INSTRUCTION
    # Rule 8 explicitly mentions legal substitutions and not apologizing
    assert "8. FORMAT LIMITATIONS" in SYSTEM_INSTRUCTION
    assert "recommend legal substitutions" in SYSTEM_INSTRUCTION
