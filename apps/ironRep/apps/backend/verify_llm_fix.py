
import asyncio
import os
import sys

# Set up path to import backend modules
sys.path.append("/home/autcir_gmail_com/develop/apps/ironRep/apps/backend")

# Mock environment variables
os.environ["OLLAMA_HOST"] = "central-ollama"
os.environ["OLLAMA_PORT"] = "11434"
os.environ["USE_OLLAMA"] = "true"
os.environ["GROQ_API_KEY"] = "mock_key"
os.environ["OPENROUTER_API_KEY"] = "mock_key"
os.environ["GOOGLE_API_KEY"] = "mock_key"

from src.infrastructure.ai.llm_service import LLMService, LLMProvider

async def test_llm_service_initialization():
    print("Initializing LLMService...")
    try:
        service = LLMService()
        print("LLMService initialized successfully.")
        
        print("Checking Ollama provider in fallback chain...")
        ollama_entry = next((entry for entry in service.fallback_chain if entry[0] == LLMProvider.OLLAMA), None)
        
        if ollama_entry:
            provider, client, name, model = ollama_entry
            print(f"Ollama provider found: {name}")
            if client is not None:
                print(f"✅ Success: ChatOllama client is initialized: {type(client)}")
            else:
                print("❌ Failure: ChatOllama client is None!")
        else:
            print("❌ Failure: Ollama provider not found in fallback chain.")

        # Test get_client_for_agent
        print("\nTesting get_client_for_agent()...")
        try:
            client = service.get_client_for_agent()
            print(f"✅ Success: get_client_for_agent returned: {type(client)}")
        except Exception as e:
            print(f"❌ Failure during get_client_for_agent: {e}")

    except Exception as e:
        print(f"❌ Critical Error during initialization: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_service_initialization())
