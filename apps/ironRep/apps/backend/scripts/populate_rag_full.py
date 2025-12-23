#!/usr/bin/env python3
"""
Populate RAG Full - Complete Knowledge Base Population Script.

This script populates ChromaDB with ALL knowledge bases:
- Markdown knowledge files
- Exercise database (2236+ exercises)
- Medical knowledge
- Recipes and nutrition

Usage:
    cd apps/backend
    python scripts/populate_rag_full.py
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
DATA_DIR = Path(__file__).parent.parent / "data"
BATCH_SIZE = 100  # ChromaDB batch size for exercises


def get_chroma_client():
    """Initialize ChromaDB client."""
    print(f"🔗 Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings(anonymized_telemetry=False)
    )
    print("✅ Connected to ChromaDB")
    return client


def get_embedding_function():
    """Get default embedding function."""
    return embedding_functions.DefaultEmbeddingFunction()


def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    sections = text.split("\n## ")

    for i, section in enumerate(sections):
        if i > 0:
            section = "## " + section

        if len(section) <= chunk_size:
            if section.strip():
                chunks.append(section.strip())
        else:
            words = section.split()
            current_chunk = []
            current_len = 0

            for word in words:
                if current_len + len(word) + 1 > chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    overlap_words = current_chunk[-20:] if len(current_chunk) > 20 else current_chunk
                    current_chunk = overlap_words.copy()
                    current_len = sum(len(w) + 1 for w in current_chunk)

                current_chunk.append(word)
                current_len += len(word) + 1

            if current_chunk:
                chunks.append(" ".join(current_chunk))

    return chunks


def generate_id(text: str, prefix: str = "") -> str:
    """Generate unique ID from text."""
    hash_val = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_val}" if prefix else hash_val


def populate_markdown_files(collection, embedding_fn):
    """Populate collection with markdown knowledge base files."""
    print("\n📚 POPULATING MARKDOWN KNOWLEDGE BASES")
    print("=" * 50)

    markdown_files = [
        # Root data files
        (DATA_DIR / "crossfit_knowledge_base.md", {
            "category": "crossfit",
            "type": "knowledge_base",
            "topic": "crossfit_training"
        }),
        (DATA_DIR / "sports_medicine_knowledge_base.md", {
            "category": "medical",
            "type": "knowledge_base",
            "topic": "sports_medicine"
        }),
        # Knowledge base folder
        (DATA_DIR / "knowledge_base" / "crossfit_movement_standards.md", {
            "category": "crossfit",
            "type": "movement_standards",
            "topic": "exercise_technique"
        }),
        (DATA_DIR / "knowledge_base" / "fit_recipes.md", {
            "category": "nutrition",
            "type": "recipes",
            "topic": "meal_planning"
        }),
        (DATA_DIR / "knowledge_base" / "sciatica_medical_knowledge.md", {
            "category": "medical",
            "type": "injury_knowledge",
            "topic": "sciatica"
        }),
    ]

    total_chunks = 0

    for filepath, metadata in markdown_files:
        if not filepath.exists():
            print(f"  ⚠️  Not found: {filepath.name}")
            continue

        print(f"\n  📄 Processing: {filepath.name}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = split_text(content)
        if not chunks:
            print(f"    ⚠️  No chunks generated")
            continue

        # Prepare data
        ids = [generate_id(chunk, filepath.stem) for chunk in chunks]
        metadatas = []
        for i, chunk in enumerate(chunks):
            meta = metadata.copy()
            meta["source"] = str(filepath)
            meta["chunk_index"] = i
            meta["ingested_at"] = datetime.now().isoformat()
            metadatas.append(meta)

        # Add to collection
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

        print(f"    ✅ Added {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\n📊 Total markdown chunks: {total_chunks}")
    return total_chunks


def populate_exercises(collection, embedding_fn):
    """Populate collection with exercise database."""
    print("\n🏋️ POPULATING EXERCISE DATABASE")
    print("=" * 50)

    exercises_file = DATA_DIR / "final" / "exercises_complete.json"

    if not exercises_file.exists():
        print(f"  ⚠️  Exercises file not found: {exercises_file}")
        return 0

    print(f"  📄 Loading: {exercises_file.name}")

    with open(exercises_file, 'r', encoding='utf-8') as f:
        exercises = json.load(f)

    print(f"  📊 Total exercises: {len(exercises)}")

    total_added = 0
    batch_docs = []
    batch_ids = []
    batch_metas = []

    for i, exercise in enumerate(exercises):
        # Create searchable document from exercise
        doc_parts = [
            f"Exercise: {exercise.get('name', 'Unknown')}",
            f"Category: {exercise.get('category', 'N/A')}",
            f"Difficulty: {exercise.get('difficulty', 'N/A')}",
            f"Equipment: {', '.join(exercise.get('equipment', []))}",
            f"Target Muscles: {', '.join(exercise.get('target_muscles', []))}",
            f"Secondary Muscles: {', '.join(exercise.get('secondary_muscles', []))}",
            f"Phases: {', '.join(exercise.get('phases', []))}",
        ]

        # Add instructions
        instructions = exercise.get('instructions', [])
        if instructions:
            doc_parts.append("Instructions: " + " ".join(instructions))

        # Add injury-specific info
        injury_info = exercise.get('injury_specific', {})
        for injury_type, info in injury_info.items():
            if info.get('therapeutic_value') in ['high', 'medium']:
                doc_parts.append(f"{injury_type}: therapeutic_value={info.get('therapeutic_value')}")
                if info.get('modifications'):
                    doc_parts.append(f"Modifications: {json.dumps(info.get('modifications'))}")

        document = "\n".join(doc_parts)

        # Metadata
        metadata = {
            "category": "exercise",
            "type": "exercise_db",
            "exercise_id": exercise.get('id', ''),
            "exercise_name": exercise.get('name', ''),
            "exercise_category": exercise.get('category', ''),
            "difficulty": exercise.get('difficulty', ''),
            "equipment": ",".join(exercise.get('equipment', [])),
            "target_muscles": ",".join(exercise.get('target_muscles', [])),
            "phases": ",".join(exercise.get('phases', [])),
            "source": "exercises_complete.json",
            "ingested_at": datetime.now().isoformat()
        }

        # Add to batch
        batch_docs.append(document)
        batch_ids.append(f"exercise_{exercise.get('id', i)}")
        batch_metas.append(metadata)

        # Insert batch when full
        if len(batch_docs) >= BATCH_SIZE:
            try:
                collection.add(
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metas
                )
                total_added += len(batch_docs)
                print(f"    ✅ Added batch: {total_added}/{len(exercises)} exercises")
            except Exception as e:
                print(f"    ❌ Error adding batch: {e}")

            batch_docs = []
            batch_ids = []
            batch_metas = []

    # Add remaining
    if batch_docs:
        try:
            collection.add(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metas
            )
            total_added += len(batch_docs)
        except Exception as e:
            print(f"    ❌ Error adding final batch: {e}")

    print(f"\n📊 Total exercises added: {total_added}")
    return total_added


def clear_collection(collection):
    """Clear all documents from collection."""
    try:
        # Get all IDs
        results = collection.get()
        if results and results['ids']:
            collection.delete(ids=results['ids'])
            print(f"  🗑️  Deleted {len(results['ids'])} existing documents")
    except Exception as e:
        print(f"  ⚠️  Could not clear collection: {e}")


def main():
    """Main function to populate RAG."""
    print("=" * 60)
    print("🚀 IRONREP RAG POPULATION SCRIPT")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().isoformat()}")
    print(f"📁 Data directory: {DATA_DIR}")

    # Connect to ChromaDB
    client = get_chroma_client()
    embedding_fn = get_embedding_function()

    # Get or create collection
    print("\n📦 Setting up collection: ironrep_knowledge")
    collection = client.get_or_create_collection(
        name="ironrep_knowledge",
        embedding_function=embedding_fn
    )

    # Ask to clear existing data
    existing = collection.count()
    print(f"  📊 Existing documents: {existing}")

    if existing > 0:
        clear = input("  ❓ Clear existing data? (y/N): ").strip().lower()
        if clear == 'y':
            clear_collection(collection)

    # Populate knowledge bases
    markdown_chunks = populate_markdown_files(collection, embedding_fn)

    # Populate exercises
    exercise_count = populate_exercises(collection, embedding_fn)

    # Summary
    print("\n" + "=" * 60)
    print("✅ POPULATION COMPLETE")
    print("=" * 60)

    final_count = collection.count()
    print(f"📊 Final document count: {final_count}")
    print(f"   - Markdown chunks: {markdown_chunks}")
    print(f"   - Exercises: {exercise_count}")
    print(f"📅 Completed: {datetime.now().isoformat()}")

    # Test retrieval
    print("\n🔍 Testing retrieval...")
    test_queries = [
        "sciatica exercises phase 1",
        "high protein breakfast recipe",
        "squat technique cues",
        "shoulder impingement modifications"
    ]

    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        print(f"\n  Query: '{query}'")
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0][:2]):
                preview = doc[:100].replace('\n', ' ') + "..."
                print(f"    {i+1}. {preview}")
        else:
            print("    No results found")

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
