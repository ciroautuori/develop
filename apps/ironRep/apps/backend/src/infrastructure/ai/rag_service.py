"""
RAG Service - Vector Database for IronRep Knowledge Base.

Manages document ingestion, embedding, and retrieval from ChromaDB.
"""
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.infrastructure.ai.google_embeddings import CustomGoogleEmbeddingFunction

from src.infrastructure.config.settings import settings
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class RAGService:
    """Service for Retrieval-Augmented Generation using ChromaDB (VPS local)."""

    def __init__(self):
        """Initialize RAG service with ChromaDB."""

        # Initialize ChromaDB with default embeddings
        self._init_chroma()

    def _init_chroma(self):
        """Initialize ChromaDB connection with default embeddings."""
        logger.info(f"Using Local ChromaDB at {settings.chroma_host}:{settings.chroma_port}")

        self.chroma_client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )

        # Use Custom Google Generative AI Embeddings
        logger.info("Using Custom Google Generative AI Embeddings")
        self.embedding_fn = CustomGoogleEmbeddingFunction(
            api_key=settings.google_api_key
        )

        # Get or create collection WITHOUT embedding function (manual handling)
        self.collection = self.chroma_client.get_or_create_collection(
            name="ironrep_knowledge_v2",
            embedding_function=None 
        )

    def ingest_document(self, filepath: str, metadata: Optional[Dict] = None):
        """
        Ingest a markdown document into the vector store.

        Args:
            filepath: Path to the document file
            metadata: Optional metadata to attach to chunks
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Document not found: {filepath}")

        # Load document
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into chunks manually
        chunks = self._split_text(content)

        if not chunks:
            logger.warning(f"No chunks generated from {filepath}")
            return 0

        # Prepare data for ChromaDB
        ids = [f"{Path(filepath).stem}_{i}" for i in range(len(chunks))]
        metadatas = [metadata.copy() if metadata else {} for _ in chunks]

        # Add source to metadata
        for m in metadatas:
            m["source"] = str(filepath)

        # Generate embeddings explicitly
        embeddings = self.embedding_fn(chunks)

        # Add to collection
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        logger.info(f"Ingested {len(chunks)} chunks from {Path(filepath).name}")
        return len(chunks)

    def _ingest_json_file(self, filepath: str, doc_type: str = "generic"):
        """
        Ingest any JSON file into vector store.
        Handles exercises, recipes, rehab protocols, etc.
        """
        import json

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Fix potential JSON truncation
            if content.startswith('[') and not content.endswith(']'):
                last_brace = content.rfind('}')
                content = content[:last_brace+1] + ']'
            data = json.loads(content)

        # Handle both array and object formats
        if isinstance(data, dict):
            data = [data]

        if doc_type == "exercise":
            return self._process_exercises(data, filepath)
        elif doc_type == "recipe":
            return self._process_recipes(data, filepath)
        elif doc_type == "rehab":
            return self._process_rehab_protocols(data, filepath)
        else:
            return self._process_generic_json(data, filepath)

    def _process_recipes(self, recipes: list, filepath: str):
        """Process fitness recipes into searchable documents."""
        documents = []
        ids = []
        metadatas = []

        for i, recipe in enumerate(recipes):
            doc_parts = [
                f"# {recipe.get('name', 'Ricetta')}",
                f"Categoria: {recipe.get('category', 'N/A')}",
                f"Descrizione: {recipe.get('description', '')}",
                f"Tempo preparazione: {recipe.get('prep_time_min', 0)} min",
                f"Tempo cottura: {recipe.get('cook_time_min', 0)} min",
                f"Porzioni: {recipe.get('servings', 1)}",
                f"Difficoltà: {recipe.get('difficulty', 'N/A')}",
            ]

            # Ingredienti
            if recipe.get('ingredients'):
                doc_parts.append("\nIngredienti:")
                for ing in recipe.get('ingredients', []):
                    doc_parts.append(f"  - {ing.get('quantity', '')} {ing.get('unit', '')} {ing.get('name', '')}")

            # Valori nutrizionali
            nutrition = recipe.get('nutrition_per_serving', {})
            if nutrition:
                doc_parts.append(f"\nValori per porzione:")
                doc_parts.append(f"  Calorie: {nutrition.get('calories', 0)} kcal")
                doc_parts.append(f"  Proteine: {nutrition.get('protein_g', 0)}g")
                doc_parts.append(f"  Carboidrati: {nutrition.get('carbs_g', 0)}g")
                doc_parts.append(f"  Grassi: {nutrition.get('fat_g', 0)}g")

            # Istruzioni (NUOVO - per ricette dettagliate)
            if recipe.get('instructions'):
                doc_parts.append("\nIstruzioni:")
                for instr in recipe.get('instructions', []):
                    doc_parts.append(f"  {instr}")

            # Tags e obiettivi
            if recipe.get('tags'):
                doc_parts.append(f"\nTags: {', '.join(recipe.get('tags', []))}")
            if recipe.get('suitable_for'):
                doc_parts.append(f"Adatto per: {', '.join(recipe.get('suitable_for', []))}")
            if recipe.get('meal_timing'):
                doc_parts.append(f"Timing: {', '.join(recipe.get('meal_timing', []))}")
            if recipe.get('sport_specific'):
                doc_parts.append(f"Sport: {', '.join(recipe.get('sport_specific', []))}")
            if recipe.get('recovery_benefits'):
                doc_parts.append(f"Benefici recupero: {recipe.get('recovery_benefits')}")
            if recipe.get('energy_benefits'):
                doc_parts.append(f"Benefici energia: {recipe.get('energy_benefits')}")

            documents.append("\n".join(doc_parts))
            # Use index-based unique ID to avoid duplicates
            ids.append(f"recipe_{i}_{recipe.get('category', 'unknown')}")
            metadatas.append({
                "source": "fitness_recipes",
                "type": "recipe",
                "category": "nutrition",
                "recipe_name": recipe.get('name', ''),
                "recipe_category": recipe.get('category', '')
            })

        # Add in batches
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = self.embedding_fn(batch_docs)
            
            self.collection.add(
                documents=batch_docs,
                embeddings=batch_embeddings,
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

        logger.info(f"Ingested {len(documents)} recipes")
        return len(documents)

    def _process_rehab_protocols(self, protocols: list, filepath: str):
        """Process rehab protocols into searchable documents."""
        documents = []
        ids = []
        metadatas = []

        for i, protocol in enumerate(protocols):
            doc_parts = [
                f"# Protocollo Riabilitazione: {protocol.get('injury_name', 'N/A')}",
                f"ID Infortunio: {protocol.get('injury_id', 'N/A')}",
                f"Descrizione: {protocol.get('description', '')}",
                f"Tempo recupero: {protocol.get('recovery_time_weeks', 'N/A')} settimane",
            ]

            # Cause comuni
            if protocol.get('common_causes'):
                doc_parts.append(f"\nCause comuni: {', '.join(protocol.get('common_causes', []))}")

            # Sintomi
            if protocol.get('symptoms'):
                doc_parts.append(f"Sintomi: {', '.join(protocol.get('symptoms', []))}")

            # Red flags
            if protocol.get('red_flags'):
                doc_parts.append(f"\n⚠️ Red Flags (consultare medico): {', '.join(protocol.get('red_flags', []))}")

            # Fasi riabilitazione
            for phase in protocol.get('phases', []):
                doc_parts.append(f"\n## Fase {phase.get('phase', '')}: {phase.get('name', '')}")
                doc_parts.append(f"Durata: {phase.get('duration', 'N/A')}")
                if phase.get('goals'):
                    doc_parts.append(f"Obiettivi: {', '.join(phase.get('goals', []))}")
                if phase.get('exercises'):
                    doc_parts.append("Esercizi:")
                    for ex in phase.get('exercises', [])[:5]:  # Limit to 5
                        doc_parts.append(f"  - {ex.get('name', '')}: {ex.get('sets', '')}x{ex.get('reps', '')}")
                if phase.get('avoid'):
                    doc_parts.append(f"Evitare: {', '.join(phase.get('avoid', []))}")

            # Prevenzione
            if protocol.get('prevention_tips'):
                doc_parts.append(f"\nPrevenzione: {', '.join(protocol.get('prevention_tips', []))}")

            documents.append("\n".join(doc_parts))
            ids.append(f"rehab_{protocol.get('injury_id', i)}")
            metadatas.append({
                "source": "rehab_protocols",
                "type": "rehab_protocol",
                "category": "medical",
                "injury_id": protocol.get('injury_id', ''),
                "injury_name": protocol.get('injury_name', '')
            })

        # Generate embeddings
        embeddings = self.embedding_fn(documents)

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        logger.info(f"Ingested {len(documents)} rehab protocols")
        return len(documents)

    def _process_generic_json(self, data: list, filepath: str):
        """Process generic JSON data."""
        documents = []
        ids = []
        metadatas = []

        for i, item in enumerate(data):
            doc = json.dumps(item, ensure_ascii=False, indent=2)
            documents.append(doc)
            ids.append(f"json_{Path(filepath).stem}_{i}")
            metadatas.append({"source": str(filepath), "type": "json"})

        embeddings = self.embedding_fn(documents)
        self.collection.add(documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas)
        return len(documents)

    def _process_exercises(self, exercises: list, filepath: str):
        """Process exercises into searchable documents."""
        documents = []
        ids = []
        metadatas = []

        for ex in exercises:
            # Build rich text document for each exercise
            doc_parts = [
                f"# {ex.get('name', 'Unknown Exercise')}",
                f"Category: {ex.get('category', 'N/A')}",
                f"Difficulty: {ex.get('difficulty', 'N/A')}",
                f"Equipment: {', '.join(ex.get('equipment', []))}",
                f"Target muscles: {', '.join(ex.get('target_muscles', []))}",
                f"Secondary muscles: {', '.join(ex.get('secondary_muscles', []))}",
                f"Movement pattern: {ex.get('movement_pattern', 'N/A')}",
            ]

            # Add instructions
            if ex.get('instructions'):
                doc_parts.append("\nInstructions:")
                for instr in ex.get('instructions', []):
                    doc_parts.append(f"  {instr}")

            # Add injury-specific information (CRITICAL for medical agent)
            injury_data = ex.get('injury_specific', {})
            if injury_data:
                doc_parts.append("\nInjury Adaptations:")
                for injury_type, info in injury_data.items():
                    if info.get('therapeutic_value') != 'low' or info.get('contraindications'):
                        doc_parts.append(f"  {injury_type.upper()}:")
                        doc_parts.append(f"    Therapeutic value: {info.get('therapeutic_value', 'N/A')}")
                        if info.get('contraindications'):
                            doc_parts.append(f"    Contraindications: {', '.join(info['contraindications'])}")
                        if info.get('modifications'):
                            doc_parts.append(f"    Modifications: {info['modifications']}")
                        if info.get('notes'):
                            doc_parts.append(f"    Notes: {info['notes']}")

            # Add phases
            if ex.get('phases'):
                doc_parts.append(f"\nRecovery phases: {', '.join(ex.get('phases', []))}")

            document = "\n".join(doc_parts)

            documents.append(document)
            ids.append(f"exercise_{ex.get('id', len(ids))}")
            metadatas.append({
                "source": "exercises_db",
                "type": "exercise",
                "category": "training",
                "exercise_name": ex.get('name', ''),
                "exercise_category": ex.get('category', ''),
                "equipment": ','.join(ex.get('equipment', [])),
                "target_muscles": ','.join(ex.get('target_muscles', []))
            })

        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]

            batch_embeddings = self.embedding_fn(batch_docs)

            self.collection.add(
                documents=batch_docs,
                embeddings=batch_embeddings,
                ids=batch_ids,
                metadatas=batch_metas
            )

        logger.info(f"Ingested {len(documents)} exercises from database")
        return len(documents)

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks."""
        chunks = []

        # Split by headers first
        sections = text.split("\n## ")

        for i, section in enumerate(sections):
            if i > 0:
                section = "## " + section

            # If section is small enough, add as is
            if len(section) <= chunk_size:
                if section.strip():
                    chunks.append(section.strip())
            else:
                # Split large sections
                words = section.split()
                current_chunk = []
                current_len = 0

                for word in words:
                    if current_len + len(word) + 1 > chunk_size and current_chunk:
                        chunks.append(" ".join(current_chunk))
                        # Keep overlap
                        overlap_words = current_chunk[-20:] if len(current_chunk) > 20 else current_chunk
                        current_chunk = overlap_words.copy()
                        current_len = sum(len(w) + 1 for w in current_chunk)

                    current_chunk.append(word)
                    current_len += len(word) + 1

                if current_chunk:
                    chunks.append(" ".join(current_chunk))

        return chunks

    def retrieve_context(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context for a query.

        Args:
            query: The search query
            k: Number of results to retrieve
            filter_metadata: Optional metadata filters

        Returns:
            List of relevant document chunks with scores
        """
        # Query ChromaDB collection with explicit embeddings
        query_embeddings = self.embedding_fn([query])
        
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=k,
            where=filter_metadata if filter_metadata else None
        )

        # Format results
        context_chunks = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0

                context_chunks.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": 1 - distance  # Convert distance to similarity
                })

        return context_chunks

    def get_exercise_recommendations(
        self,
        pain_level: int,
        recovery_phase: str,
        focus_areas: List[str]
    ) -> str:
        """
        Get exercise recommendations based on current state.

        Args:
            pain_level: Current pain level (0-10)
            recovery_phase: Current recovery phase (1-4)
            focus_areas: List of focus areas (e.g., ["squat", "pull"])

        Returns:
            Formatted context string for LLM
        """
        # Build query from current state
        query_parts = [
            f"Recovery Phase {recovery_phase}",
            f"Pain level {pain_level}",
            "Safe exercises for"
        ]
        query_parts.extend(focus_areas)
        query = " ".join(query_parts)

        # Retrieve relevant context
        results = self.retrieve_context(query, k=8)

        # Format for LLM
        context = "=== KNOWLEDGE BASE CONTEXT ===\n\n"
        for i, chunk in enumerate(results, 1):
            context += f"[Context {i}] (Relevance: {chunk['relevance_score']:.3f})\n"
            context += f"{chunk['content']}\n\n"

        return context

    def get_injury_guidelines(self, exercise_name: str, injury_type: str) -> Optional[str]:
        """
        Get injury-specific guidelines for an exercise.

        Args:
            exercise_name: Name of the exercise
            injury_type: Type of injury (e.g., 'sciatica', 'pubalgia', 'shoulder_impingement')

        Returns:
            Guidelines text or None if not found
        """
        query = f"{exercise_name} {injury_type} risk adaptation modifications"
        results = self.retrieve_context(query, k=3)

        if not results:
            return None

        # Return most relevant result
        return results[0]["content"]

    def get_exercise_contraindications(self, exercise_name: str, injury_types: List[str]) -> Dict[str, Any]:
        """
        Get contraindications for an exercise across multiple injury types.

        Args:
            exercise_name: Name of the exercise
            injury_types: List of injury types to check

        Returns:
            Dict with contraindications per injury type
        """
        contraindications = {}

        for injury_type in injury_types:
            guidelines = self.get_injury_guidelines(exercise_name, injury_type)
            if guidelines:
                contraindications[injury_type] = guidelines

        return contraindications

    def get_recipe_recommendations(
        self,
        goal: str,
        dietary_restrictions: List[str],
        ingredients: List[str] = []
    ) -> str:
        """
        Get recipe recommendations based on goal and preferences.

        Args:
            goal: User's nutritional goal (e.g., "muscle gain", "weight loss")
            dietary_restrictions: List of restrictions (e.g., "vegan", "gluten-free")
            ingredients: List of available ingredients

        Returns:
            Formatted context string for LLM
        """
        # Build query
        query_parts = [
            f"Recipe for {goal}",
        ]

        if dietary_restrictions:
            query_parts.append(f"compatible with {', '.join(dietary_restrictions)}")

        if ingredients:
            query_parts.append(f"using {', '.join(ingredients)}")

        query = " ".join(query_parts)

        # Retrieve relevant context
        results = self.retrieve_context(
            query,
            k=5,
            filter_metadata={"category": "nutrition"}
        )

        if not results:
            return ""

        # Format for LLM
        context = "=== RECIPE KNOWLEDGE BASE ===\n\n"
        for i, chunk in enumerate(results, 1):
            context += f"[Recipe {i}] (Relevance: {chunk['relevance_score']:.3f})\n"
            context += f"{chunk['content']}\n\n"

        return context

    def initialize_knowledge_base(self, data_dir: str = "./data"):
        """
        Initialize the knowledge base by ingesting all documents.

        Args:
            data_dir: Directory containing knowledge base files
        """
        data_path = Path(data_dir)

        # Check if already initialized
        try:
            collection = self.collection.get()
            if collection and collection.get('ids') and len(collection['ids']) > 0:
                logger.info(f"Knowledge base already initialized with {len(collection['ids'])} documents")
                return
        except KeyError as e:
            # ChromaDB version mismatch - collection may need reinitialization
            logger.warning(f"ChromaDB collection format issue ({e}), will reinitialize if needed")
        except Exception as e:
            logger.warning(f"Error checking knowledge base status: {e}")

        logger.info("Initializing knowledge base...")

        rag_path = data_path / "rag"

        total_docs = 0

        # === TRAINING DOCUMENTS ===
        training_path = rag_path / "training"
        if training_path.exists():
            for md_file in training_path.glob("*.md"):
                count = self.ingest_document(
                    str(md_file),
                    metadata={"source": md_file.stem, "type": "training", "category": "training"}
                )
                total_docs += count
                logger.info(f"Loaded {md_file.name}: {count} chunks")

        # === MEDICAL DOCUMENTS ===
        medical_path = rag_path / "medical"
        if medical_path.exists():
            # Markdown files
            for md_file in medical_path.glob("*.md"):
                count = self.ingest_document(
                    str(md_file),
                    metadata={"source": md_file.stem, "type": "medical", "category": "medical"}
                )
                total_docs += count
                logger.info(f"Loaded {md_file.name}: {count} chunks")

            # Rehab protocols JSON
            rehab_json = medical_path / "rehab_protocols.json"
            if rehab_json.exists():
                count = self._ingest_json_file(str(rehab_json), doc_type="rehab")
                total_docs += count

        # === NUTRITION DOCUMENTS (DISABLED - FATSECRET ONLY MANDATE) ===
        # nutrition_path = rag_path / "nutrition"
        # if nutrition_path.exists():
        #     # Markdown files
        #     for md_file in nutrition_path.glob("*.md"):
        #         count = self.ingest_document(
        #             str(md_file),
        #             metadata={"source": md_file.stem, "type": "nutrition", "category": "nutrition"}
        #         )
        #         total_docs += count
        #         logger.info(f"Loaded {md_file.name}: {count} chunks")
        #
        #     # Fitness recipes JSON (base + enhanced)
        #     for recipe_file in ["fitness_recipes.json", "fit_recipes_enhanced.json"]:
        #         recipes_json = nutrition_path / recipe_file
        #         if recipes_json.exists():
        #             count = self._ingest_json_file(str(recipes_json), doc_type="recipe")
        #             total_docs += count
        #             logger.info(f"Loaded {recipe_file}: {count} recipes")

        # === EXERCISES DATABASE ===
        exercises_path = rag_path / "exercises"
        if exercises_path.exists():
            exercises_json = exercises_path / "exercises_complete.json"
            if exercises_json.exists():
                count = self._ingest_json_file(str(exercises_json), doc_type="exercise")
                total_docs += count

        logger.info(f"Knowledge base initialization complete! Total: {total_docs} documents")

    def reinitialize_knowledge_base(self, data_dir: str = "./data"):
        """
        Force reinitialize the knowledge base by clearing and reloading all documents.

        Args:
            data_dir: Directory containing knowledge base files
        """
        logger.info("Reinitializing knowledge base (clearing existing data)...")

        # Delete existing collection
        try:
            self.chroma_client.delete_collection("ironrep_knowledge_v2")
            logger.info("Deleted existing collection")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")

        # Recreate collection WITHOUT embedding function
        self.collection = self.chroma_client.get_or_create_collection(
            name="ironrep_knowledge_v2",
            embedding_function=None
        )

        # Use the same initialization logic
        rag_path = Path(data_dir) / "rag"
        total_docs = 0

        # === TRAINING DOCUMENTS ===
        training_path = rag_path / "training"
        if training_path.exists():
            for md_file in training_path.glob("*.md"):
                count = self.ingest_document(
                    str(md_file),
                    metadata={"source": md_file.stem, "type": "training", "category": "training"}
                )
                total_docs += count
                logger.info(f"Loaded {md_file.name}: {count} chunks")

        # === MEDICAL DOCUMENTS ===
        medical_path = rag_path / "medical"
        if medical_path.exists():
            for md_file in medical_path.glob("*.md"):
                count = self.ingest_document(
                    str(md_file),
                    metadata={"source": md_file.stem, "type": "medical", "category": "medical"}
                )
                total_docs += count
                logger.info(f"Loaded {md_file.name}: {count} chunks")

            rehab_json = medical_path / "rehab_protocols.json"
            if rehab_json.exists():
                count = self._ingest_json_file(str(rehab_json), doc_type="rehab")
                total_docs += count

        # === NUTRITION DOCUMENTS (DISABLED - FATSECRET ONLY MANDATE) ===
        # nutrition_path = rag_path / "nutrition"
        # if nutrition_path.exists():
        #     for md_file in nutrition_path.glob("*.md"):
        #         count = self.ingest_document(
        #             str(md_file),
        #             metadata={"source": md_file.stem, "type": "nutrition", "category": "nutrition"}
        #         )
        #         total_docs += count
        #         logger.info(f"Loaded {md_file.name}: {count} chunks")
        #
        #     # Fitness recipes JSON (base + enhanced)
        #     for recipe_file in ["fitness_recipes.json", "fit_recipes_enhanced.json"]:
        #         recipes_json = nutrition_path / recipe_file
        #         if recipes_json.exists():
        #             count = self._ingest_json_file(str(recipes_json), doc_type="recipe")
        #             total_docs += count
        #             logger.info(f"Loaded {recipe_file}: {count} recipes")

        # === EXERCISES DATABASE ===
        exercises_path = rag_path / "exercises"
        if exercises_path.exists():
            exercises_json = exercises_path / "exercises_complete.json"
            if exercises_json.exists():
                count = self._ingest_json_file(str(exercises_json), doc_type="exercise")
                total_docs += count

        logger.info(f"Knowledge base reinitialized! Total: {total_docs} documents")
        return total_docs


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
