"""
Servizio di ricerca semantica con embedding per bandi ISS
OTTIMIZZATO PER OLLAMA (Rimuove dipendenza da torch/transformers locali)
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
import json
import pickle
import os
from datetime import datetime

from app.core.config import settings
from app.models.bando import Bando
from app.crud.bando import bando_crud

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Servizio per ricerca semantica avanzata sui bandi usando Ollama"""
    
    def __init__(self):
        # Configurazione Ollama per Embedding
        self.ollama_url = f"http://{settings.ollama_host}:{settings.ollama_port}/api/embeddings"
        self.model_name = "all-minilm" # Leggero e veloce
        self.bando_embeddings = {}
        
        # Cache locale per embedding
        cache_dir = os.path.expanduser("~/.cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.embeddings_cache_file = os.path.join(cache_dir, "bando_embeddings.pkl")
        self.last_update = None
        
    async def initialize(self):
        """Inizializza il servizio (carica cache)"""
        try:
            logger.info(f"🤖 Inizializzazione Ricerca Semantica con Ollama ({self.model_name})...")
            await self._load_cached_embeddings()
            logger.info("✅ Servizio Ricerca Semantica pronto!")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Ricerca Semantica: {e}")
    
    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Richiede un embedding a Ollama"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model_name,
                        "prompt": text
                    }
                )
                if response.status_code == 200:
                    return response.json().get("embedding")
                else:
                    logger.error(f"❌ Errore Ollama Embedding: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Errore chiamata Ollama Embedding: {e}")
        return None

    def _prepare_bando_text(self, bando: Bando) -> str:
        """Prepara il testo del bando per l'embedding"""
        text_parts = []
        if bando.title: text_parts.append(f"Titolo: {bando.title}")
        if bando.descrizione: text_parts.append(f"Descrizione: {bando.descrizione}")
        if bando.ente: text_parts.append(f"Ente: {bando.ente}")
        if bando.categoria: text_parts.append(f"Categoria: {bando.categoria}")
        return " ".join(text_parts)

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calcola cosine similarity tra due vettori"""
        a = np.array(v1)
        b = np.array(v2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def generate_embeddings(self, db: AsyncSession, force_refresh: bool = False) -> Dict[int, List[float]]:
        """Genera embedding per tutti i bandi nel database usando Ollama"""
        
        # Controlla se serve aggiornamento
        if not force_refresh and self.bando_embeddings and self._is_cache_valid():
            return self.bando_embeddings
        
        logger.info("🔄 Generazione embedding per tutti i bandi tramite Ollama...")
        
        # Recupera tutti i bandi attivi
        bandi, _ = await bando_crud.get_bandi(db, skip=0, limit=1000)
        
        new_embeddings = {}
        for bando in bandi:
            # Usa cache se disponibile per questo bando
            if not force_refresh and bando.id in self.bando_embeddings:
                new_embeddings[bando.id] = self.bando_embeddings[bando.id]
                continue
                
            text = self._prepare_bando_text(bando)
            embedding = await self._get_embedding(text)
            if embedding:
                new_embeddings[bando.id] = embedding
                # Evita di sovraccaricare Ollama
                await os.sched_yield()
        
        self.bando_embeddings = new_embeddings
        
        # Salva cache
        await self._save_embeddings_cache()
        self.last_update = datetime.now()
        
        logger.info(f"✅ Generati {len(self.bando_embeddings)} embedding tramite Ollama")
        return self.bando_embeddings
    
    async def semantic_search(self, query: str, db: AsyncSession, limit: int = 10, threshold: float = 0.3) -> List[Tuple[Bando, float]]:
        """Ricerca semantica sui bandi tramite Ollama"""
        
        # Assicurati che gli embedding siano caricati/generati
        if not self.bando_embeddings:
            await self.initialize()
            if not self.bando_embeddings:
                await self.generate_embeddings(db)
        
        if not self.bando_embeddings:
            return []
        
        # Genera embedding della query
        query_embedding = await self._get_embedding(query)
        if not query_embedding:
            return []
        
        # Calcola similarità con tutti i bandi
        similarities = []
        for bando_id, bando_v in self.bando_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, bando_v)
            if similarity >= threshold:
                similarities.append((bando_id, similarity))
        
        # Ordina per similarità
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:limit]
        
        # Recupera i bandi dal database
        results = []
        for bando_id, similarity in similarities:
            bando = await bando_crud.get_bando(db, bando_id=bando_id)
            if bando:
                results.append((bando, similarity))
        
        logger.info(f"🔍 Ricerca semantica Ollama '{query}': {len(results)} risultati")
        return results
    
    # ... Restante logica analoga a prima, ma senza dipendenza da SentenceTransformer ...
    # (Metodi suggest_similar_bandi, match_profile_to_bandi, ecc. usano semantic_search)

    async def suggest_similar_bandi(self, bando_id: int, db: AsyncSession, limit: int = 5) -> List[Tuple[Bando, float]]:
        if bando_id not in self.bando_embeddings:
            await self.generate_embeddings(db)
        
        if bando_id not in self.bando_embeddings:
            return []
        
        target_v = self.bando_embeddings[bando_id]
        similarities = []
        for other_id, other_v in self.bando_embeddings.items():
            if other_id != bando_id:
                similarity = self._cosine_similarity(target_v, other_v)
                similarities.append((other_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:limit]
        
        results = []
        for other_id, similarity in similarities:
            bando = await bando_crud.get_bando(db, bando_id=other_id)
            if bando: results.append((bando, float(similarity)))
        return results

    async def match_profile_to_bandi(self, profile: Dict, db: AsyncSession, limit: int = 10) -> List[Tuple[Bando, float]]:
        query_parts = []
        if profile.get('organization_type'): query_parts.append(f"organizzazione {profile['organization_type']}")
        if profile.get('sectors'): query_parts.append(f"settori: {', '.join(profile['sectors'])}")
        if profile.get('keywords'): query_parts.append(f"interesse: {', '.join(profile['keywords'])}")
        query = " ".join(query_parts)
        return await self.semantic_search(query, db, limit=limit, threshold=0.2)

    async def _load_cached_embeddings(self):
        try:
            if os.path.exists(self.embeddings_cache_file):
                with open(self.embeddings_cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.bando_embeddings = cache_data.get('embeddings', {})
                    self.last_update = cache_data.get('last_update')
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento cache embedding: {e}")

    async def _save_embeddings_cache(self):
        try:
            with open(self.embeddings_cache_file, 'wb') as f:
                pickle.dump({'embeddings': self.bando_embeddings, 'last_update': datetime.now()}, f)
        except Exception as e:
            logger.warning(f"⚠️ Errore salvataggio cache embedding: {e}")

    def _is_cache_valid(self) -> bool:
        if not self.last_update: return False
        return (datetime.now() - self.last_update).total_seconds() / 3600 < 24

# Singleton
semantic_search_service = SemanticSearchService()
