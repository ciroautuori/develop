#!/usr/bin/env python3
"""
ChromaDB Inspector - Visualizza contenuti RAG come pgadmin
Verifica quali file sono stati caricati in ChromaDB
"""

import sys
import os
sys.path.append('apps/backend')

from src.infrastructure.ai.rag_service import RAGService
from src.infrastructure.config.settings import settings
import json
from pathlib import Path

def inspect_chromadb():
    """Ispeziona il contenuto di ChromaDB"""

    print("🔍 ChromaDB Inspector - IronRep RAG Analysis")
    print("=" * 60)

    try:
        # Inizializza RAG service
        rag = RAGService()

        # Ottieni collection info
        collection = rag.collection

        # Count totale documenti
        total_docs = collection.count()
        print(f"📊 Total Documents in ChromaDB: {total_docs}")
        print()

        if total_docs == 0:
            print("❌ NESSUN documento trovato in ChromaDB!")
            return

        # Get tutti i documenti con metadata
        all_docs = collection.get(include=['metadatas', 'documents'])

        print("📋 Document Analysis:")
        print("-" * 40)

        # Analizza per source/type
        sources = {}
        categories = {}
        file_types = {}

        for i, (metadata, doc) in enumerate(zip(all_docs['metadatas'], all_docs['documents'])):
            if metadata:
                source = metadata.get('source', 'unknown')
                category = metadata.get('category', 'unknown')

                # Count by source
                sources[source] = sources.get(source, 0) + 1

                # Count by category
                categories[category] = categories.get(category, 0) + 1

                # Extract file type from source
                if '.' in source:
                    file_ext = source.split('.')[-1]
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1

                # Show first few documents
                if i < 5:
                    print(f"📄 {source}")
                    print(f"   Category: {category}")
                    print(f"   Length: {len(doc)} chars")
                    print(f"   Preview: {doc[:100]}...")
                    print()

        print("📈 Summary by Source:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count} documents")

        print("\n📈 Summary by Category:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} documents")

        print("\n📈 Summary by File Type:")
        for ext, count in sorted(file_types.items()):
            print(f"  .{ext}: {count} documents")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        print(f"   ChromaDB Host: {settings.chroma_host}:{settings.chroma_port}")
        return False

    return True

def check_local_files():
    """Verifica quali file esistono localmente in data/"""

    print("\n📁 Local Files in apps/backend/data:")
    print("-" * 40)

    data_dir = Path("apps/backend/data")

    if not data_dir.exists():
        print("❌ Directory data/ non trovata!")
        return

    # File principali
    main_files = list(data_dir.glob("*.md")) + list(data_dir.glob("*.json"))

    for file_path in sorted(main_files):
        size = file_path.stat().st_size
        print(f"📄 {file_path.name} ({size:,} bytes)")

    # Subdirectories
    for subdir in sorted(data_dir.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith('.'):
            file_count = len(list(subdir.rglob("*")))
            print(f"📁 {subdir.name}/ ({file_count} items)")

    print()

def main():
    """Main inspection"""

    # Check local files
    check_local_files()

    # Check ChromaDB
    success = inspect_chromadb()

    if success:
        print("✅ ChromaDB inspection completed!")
        print("\n💡 To access ChromaDB web interface:")
        print(f"   URL: http://{settings.chroma_host}:{settings.chroma_port}")
        print("   (Note: ChromaDB has basic web UI, not full pgadmin-like interface)")
    else:
        print("❌ ChromaDB inspection failed!")

    print("\n🔧 To repopulate RAG if needed:")
    print("   cd apps/backend && python scripts/populate_rag_full.py")

if __name__ == "__main__":
    main()
