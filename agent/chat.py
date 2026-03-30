import logging
from agent.core import create_vgc_agent

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("🤖 Booting up VGC Analyst AI...")
    print("Ensure your FastAPI server is running on localhost:8000!\n")
    
    chat_session = create_vgc_agent()
    
    print("Ask me anything.! (Type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou (Type 'quit' to exit) : ")
        if user_input.lower() in ['quit', 'exit', '0']:
            break
            
        try:
            # Send the message to the AI. If it needs data, it will automatically
            # pause, run your Python tool, read the JSON, and then generate the final answer!
            response = chat_session.send_message(user_input)
            print(f"\nAnalyst: {response.text}")
            
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()