
import sys
import os
sys.path.append('/app')

from src.infrastructure.ai.llm_service import LLMService

def test_llm():
    print("Testing LLMService...")
    try:
        service = LLMService()
        print("LLMService initialized.")
        # We don't invoke it to avoid API calls, just check initialization
    except Exception as e:
        print(f"LLMService failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm()
