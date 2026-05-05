import json
import os
import time
from agent.core import create_vgc_agent
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_503_error(exception):
    return isinstance(exception, APIError) and hasattr(exception, 'code') and exception.code == 503

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=5, max=20),
    retry=retry_if_exception(is_503_error),
    reraise=True
)
def send_with_retry(chat, prompt):
    return chat.send_message(prompt)

def evaluate_case(item, chat):
    print(f"\n--- Testing Case {item['id']} ---")
    print(f"Prompt: {item['prompt']}")
    
    try:
        history_start_idx = len(chat.get_history())
        response = send_with_retry(chat, item['prompt'])
        
        # 1. Evaluate Retrieval (Tool Calling)
        tool_calls = []
        current_history = chat.get_history()
        for msg in current_history[history_start_idx:]:
            if hasattr(msg, 'parts') and msg.parts:
                for part in msg.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_calls.append(part.function_call.name)
        
        expected_tool_name = item['tool_call'].split('(')[0]
        
        if expected_tool_name in tool_calls:
            print(f"✅ Tool Retrieval Success: Found {expected_tool_name}")
        else:
            print(f"❌ Tool Retrieval Failure: Expected {expected_tool_name}, got {tool_calls}")

        # 2. Evaluate Generation (Entity Check)
        response_text = response.text.lower().replace('-', ' ').replace('_', ' ')
        missing_entities = []
        for entity in item.get('expected_entities', []):
            clean_entity = entity.lower().replace('-', ' ').replace('_', ' ')
            if clean_entity not in response_text:
                missing_entities.append(entity)
        
        if not missing_entities:
            print(f"✅ Generation Success: All expected entities found.")
        else:
            print(f"⚠️  Generation Warning: Missing entities: {missing_entities}")
            print(f"Response: {response.text[:100]}...")

        return True
    except APIError as e:
        if hasattr(e, 'code') and e.code == 503:
            print(f"🚨 API High Demand: Case {item['id']} failed because Gemini is currently unavailable (503) after retries.")
        else:
            print(f"🔥 Gemini API Error: {e}")
        return False
    except Exception as e:
        print(f"🔥 Unexpected Error during evaluation: {e}")
        return False

def run_evaluation():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment.")
        return

    print("Initializing VGC Agent...")
    chat = create_vgc_agent()
    
    with open('tests/ai_tests/golden_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    results = []
    for item in dataset:
        time.sleep(2)
        success = evaluate_case(item, chat)
        results.append(success)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    print(f"\nEvaluation Complete: {passed}/{total} cases processed.")

if __name__ == "__main__":
    run_evaluation()
