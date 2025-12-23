import sys
import os
from pathlib import Path

# Add project root to path
import site
project_root = str(Path(__file__).parent.parent)
backend_path = os.path.join(project_root, "apps/backend")
sys.path.append(backend_path)

from src.infrastructure.ai.rag_service import get_rag_service, RAGService

def purge():
    print("Purging RAG Database...")
    rag = get_rag_service()
    
    # Force re-init (clears collection)
    # Note: reinitialize_knowledge_base takes data_dir
    # Container default is /app/data, but locally it is apps/backend/data
    
    # We need to detect environment or pass correct path
    # Assuming running from project root (apps/backend or similar)
    
    data_dir = os.path.join(project_root, "apps/backend/data")
    if not os.path.exists(data_dir):
        # Maybe we are IN apps/backend
        data_dir = "data"
        
    print(f"Using data dir: {data_dir}")
    
    try:
        count = rag.reinitialize_knowledge_base(data_dir=data_dir)
        print(f"SUCCESS: RAG Reinitialized with {count} documents.")
        print("Stale food data should be gone.")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    purge()
