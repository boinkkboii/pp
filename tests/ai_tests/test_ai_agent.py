import pytest
import json
import os
import time
from agent.core import create_vgc_agent
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_503_error(exception):
    return isinstance(exception, APIError) and hasattr(exception, 'code') and exception.code == 503

# Mark as AI test to allow filtering
@pytest.mark.ai
def test_ai_golden_dataset():
    """
    Evaluates the VGC agent against the golden dataset for retrieval and generation accuracy.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    chat = create_vgc_agent()
    
    with open('tests/ai_tests/golden_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=5, max=20),
        retry=retry_if_exception(is_503_error),
        reraise=True
    )
    def send_with_retry(prompt):
        return chat.send_message(prompt)

    for item in dataset:
        time.sleep(2) # Give the API a breather between complex turns
        print(f"\nEvaluating Case {item['id']}: {item['prompt']}")
        try:
            # We must track history length to check only the NEW messages for tool calls
            history_start_idx = len(chat.get_history())
            response = send_with_retry(item['prompt'])

            # 1. Verify Tool Call
            # Check all messages added to history during this send_message call
            tool_calls = []
            current_history = chat.get_history()
            for msg in current_history[history_start_idx:]:
                # msg is likely a UserContent or ModelContent object which has 'parts' directly
                if hasattr(msg, 'parts') and msg.parts:
                    for part in msg.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_calls.append(part.function_call.name)

            expected_tool_name = item['tool_call'].split('(')[0]

            assert expected_tool_name in tool_calls, f"Case {item['id']} failed: Expected tool {expected_tool_name} was not called. Called: {tool_calls}"

            # 2. Verify Generation (Entity Presence)
            response_text = response.text.lower().replace('-', ' ').replace('_', ' ')
            for entity in item.get('expected_entities', []):
                clean_entity = entity.lower().replace('-', ' ').replace('_', ' ')
                assert clean_entity in response_text, f"Case {item['id']} failed: Missing expected entity '{entity}' in response."
        
        except APIError as e:
            if hasattr(e, 'code') and e.code == 503:
                pytest.fail(f"Test failed due to persistent LLM API high demand (503 Service Unavailable) for Case {item['id']} after retries.")
            else:
                pytest.fail(f"Test failed due to Gemini API Error: {e}")
        except Exception as e:
            pytest.fail(f"Test failed due to unexpected error: {e}")
