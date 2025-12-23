import sys
import os

# Add current dir to path to find 'src'
sys.path.append(os.getcwd())

from src.infrastructure.ai.rag_service import get_rag_service

def purge():
    print("Purging RAG Database...")
    try:
        rag = get_rag_service()
        # Default data_dir is ./data relative to execution
        # We will run from apps/backend, so ./data refers to apps/backend/data
        rag.reinitialize_knowledge_base(data_dir="./data")
        print("SUCCESS: RAG Purged and Reinitialized.")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    purge()
