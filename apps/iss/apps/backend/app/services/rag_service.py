import httpx
import logging
from app.core.config import settings
import json

logger = logging.getLogger(__name__)

class RAGService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_url = "http://central-chromadb:8000/api/v2"
        self.tenant = "default_tenant"
        self.database = "default_database"
        self.api_root = f"{self.base_url}/tenants/{self.tenant}/databases/{self.database}"
        
        self.ollama_url = "http://central-ollama:11434/api/embeddings"
        self.collection_name = "iss_knowledge_base"
        self.collection_id = None
        
        self._initialized = True
        logger.info(f"🔌 RAG Service Initialized (HTTP V2 Mode). API Root: {self.api_root}")

    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings from Ollama"""
        embeddings = []
        async with httpx.AsyncClient() as client:
            for text in texts:
                try:
                    response = await client.post(self.ollama_url, json={
                        "model": "llama3.2:3b",
                        "prompt": text
                    }, timeout=60.0)
                    if response.status_code == 200:
                        embeddings.append(response.json()["embedding"])
                    else:
                        logger.error(f"Ollama embedding failed: {response.text}")
                        embeddings.append([0.0]*1024) 
                except Exception as e:
                    logger.error(f"Embedding error: {e}")
                    embeddings.append([0.0]*1024)
        return embeddings
        
    def _get_embeddings_sync(self, texts: list[str]) -> list[list[float]]:
        """Sync version for ingestion script"""
        embeddings = []
        with httpx.Client() as client:
            for text in texts:
                try:
                    response = client.post(self.ollama_url, json={
                        "model": "llama3.2:3b",
                        "prompt": text
                    }, timeout=60.0)
                    if response.status_code == 200:
                        embeddings.append(response.json()["embedding"])
                    else:
                        embeddings.append([])
                except Exception as e:
                    logger.error(f"Embedding error: {e}")
                    embeddings.append([])
        return embeddings

    def _ensure_collection(self):
        """Get or create collection ID using V2 paths"""
        if self.collection_id:
            return self.collection_id
            
        try:
            with httpx.Client() as client:
                # List collections
                resp = client.get(f"{self.api_root}/collections")
                
                if resp.status_code == 200:
                    cols = resp.json()
                    for col in cols:
                        if col['name'] == self.collection_name:
                            self.collection_id = col['id']
                            return self.collection_id
                
                # Create if not exists
                resp = client.post(f"{self.api_root}/collections", json={
                    "name": self.collection_name,
                    "metadata": {"hnsw:space": "cosine"}
                })
                if resp.status_code == 200:
                    self.collection_id = resp.json()['id']
                    return self.collection_id
                else:
                    logger.error(f"Failed to create collection: {resp.text}")
        except Exception as e:
            logger.error(f"Chroma connection error: {e}")
        return None

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Add documents via V2 /add endpoint"""
        col_id = self._ensure_collection()
        if not col_id:
            logger.error("Could not get collection ID")
            return
            
        embeddings = self._get_embeddings_sync(documents)
        
        payload = {
            "ids": ids,
            "embeddings": embeddings,
            "metadatas": metadatas,
            "documents": documents
        }
        
        try:
            with httpx.Client() as client:
                resp = client.post(f"{self.api_root}/collections/{col_id}/add", json=payload)
                if resp.status_code not in [200, 201]:
                     logger.error(f"Failed to add docs: {resp.text}")
        except Exception as e:
            logger.error(f"Add docs error: {e}")

    async def query(self, query_text: str, n_results: int = 3):
        """Query via V2 /query endpoint"""
        col_id = self._ensure_collection()
        if not col_id:
            return {}
            
        embeddings = await self._get_embeddings([query_text])
        if not embeddings or not embeddings[0]:
            return {}
            
        async with httpx.AsyncClient() as client:
            payload = {
                "query_embeddings": embeddings,
                "n_results": n_results
            }
            resp = await client.post(f"{self.api_root}/collections/{col_id}/query", json=payload)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error(f"Query failed: {resp.text}")
                return {}

rag_service = RAGService()
