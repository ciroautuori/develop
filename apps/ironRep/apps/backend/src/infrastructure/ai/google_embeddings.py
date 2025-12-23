import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
import logging

logger = logging.getLogger(__name__)

class CustomGoogleEmbeddingFunction(EmbeddingFunction):
    """
    Custom Embedding Function for Google Generative AI.
    Bypasses ChromaDB's internal serialization issues by handling API calls directly.
    """
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate embeddings for a list of documents.
        """
        try:
            # Google GenAI expects a list of strings
            result = genai.embed_content(
                model=self.model_name,
                content=input,
                task_type="retrieval_document",
                title=None
            )
            # Result is usually a dict with 'embedding' key
            if 'embedding' in result:
               return result['embedding']
            return []
        except Exception as e:
            logger.error(f"Error generating Google embeddings: {e}")
            # Fallback or raise? For now raise to see error
            raise e
