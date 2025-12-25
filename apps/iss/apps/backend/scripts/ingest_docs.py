
import os
import sys
import glob
from pathlib import Path

# Add backend directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.rag_service import rag_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = "/app/docs/ISS_OPERATIVO" # Inside container path (will map via volume) or local relative path if running locally

# Local path fallback
if not os.path.exists(DOCS_DIR):
    DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../docs/ISS_OPERATIVO"))

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def ingest_docs():
    logger.info(f"📂 Reading docs from: {DOCS_DIR}")
    files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
    
    total_chunks = 0
    
    for filepath in files:
        filename = os.path.basename(filepath)
        logger.info(f"Processing {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = chunk_text(content)
        
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "category": "operational"} for _ in range(len(chunks))]
        
        rag_service.add_documents(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        total_chunks += len(chunks)
        
    logger.info(f"✅ Ingestion Complete! Added {total_chunks} chunks to ChromaDB.")

if __name__ == "__main__":
    ingest_docs()
