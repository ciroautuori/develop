import asyncio
import os
import sys

# Add project root to path to resolve 'app' imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.domain.marketing.social_media_manager import SocialMediaManagerAgent
from app.infrastructure.agents.base_agent import AgentConfig

async def test_ollama_integration():
    print("Initializing Social Media Manager Agent...")
    config = AgentConfig(
        user_id="test_user",
        agent_id="test_social",
        agent_type="social_media_manager",
        name="Social Manager",
        role="Social Media Manager",
        goal="Manage social",
        backstory="Expert"
    )
    agent = SocialMediaManagerAgent(config)
    
    # Test 1: Sentiment Analysis
    print("\n--- Test 1: Sentiment Analysis (Ollama) ---", flush=True)
    text = "Io adoro assolutamente questo nuovo prodotto! È fantastico."
    print(f"Analyzing text: '{text}'", flush=True)

    # Debug client creation
    try:
        from app.core.config import settings
        print(f"DEBUG: OLLAMA_HOST={settings.OLLAMA_HOST}", flush=True)
        from app.core.llm.ollama_client import get_ollama_client
        client = get_ollama_client()
        print(f"DEBUG: Client created. Base URL: {client.base_url}", flush=True)
        is_avail = await client.is_available()
        print(f"DEBUG: Ollama Available: {is_avail}", flush=True)
    except Exception as e:
        print(f"DEBUG: Error in debug block: {e}", flush=True)
        import traceback
        traceback.print_exc()

    try:
        # calling private method for direct verification
        sentiment = await agent._analyze_sentiment(text) 
        print(f"Result: {sentiment}", flush=True)
        if sentiment in ["positive", "neutral", "negative"]:
            print("SUCCESS: Valid sentiment returned.")
        else:
            print(f"FAILURE: Invalid sentiment '{sentiment}'")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Generate Response
    print("\n--- Test 2: Generate Response (Ollama) ---")
    comment = "Il servizio clienti è terribile, nessuno risponde."
    sentiment = "negative"
    try:
        response = await agent._generate_response(comment, sentiment)
        print(f"Generated Response: {response}")
        if len(response) > 5:
             print("SUCCESS: Response generated.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama_integration())
