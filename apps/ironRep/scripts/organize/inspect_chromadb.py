#!/usr/bin/env python3
"""
ChromaDB Simple Inspector - Verifica contenuti RAG
Connessione diretta a ChromaDB senza dipendenze complesse
"""

import chromadb
from chromadb.config import Settings
import json
from pathlib import Path

def inspect_chromadb():
    """Ispeziona il contenuto di ChromaDB"""

    print("🔍 ChromaDB Simple Inspector")
    print("=" * 50)

    try:
        # Connessione diretta a ChromaDB
        client = chromadb.HttpClient(
            host='localhost',
            port=8001,
            settings=Settings(anonymized_telemetry=False)
        )

        # Lista collections
        collections = client.list_collections()
        print(f"📊 Collections found: {len(collections)}")

        if not collections:
            print("❌ NESSUNA collection trovata!")
            return False

        for collection in collections:
            print(f"\n📁 Collection: {collection.name}")
            print(f"   ID: {collection.id}")

            # Count documenti
            count = collection.count()
            print(f"   Documents: {count}")

            if count > 0:
                # Get sample documents
                sample = collection.get(
                    limit=5,
                    include=['metadatas', 'documents']
                )

                print(f"   Sample documents:")
                for i, (doc_id, metadata, doc) in enumerate(zip(
                    sample['ids'][:3],
                    sample['metadatas'][:3],
                    sample['documents'][:3]
                )):
                    print(f"     {i+1}. ID: {doc_id}")
                    if metadata:
                        source = metadata.get('source', 'unknown')
                        category = metadata.get('category', 'unknown')
                        print(f"        Source: {source}")
                        print(f"        Category: {category}")
                    print(f"        Length: {len(doc)} chars")
                    print(f"        Preview: {doc[:80]}...")
                    print()

        # Analisi dettagliata della collection principale
        main_collection = client.get_collection("ironrep_knowledge")
        print(f"\n🔍 Detailed Analysis - ironrep_knowledge:")
        print("-" * 40)

        # Get tutti i metadati
        all_data = main_collection.get(include=['metadatas'])

        # Analisi per source
        sources = {}
        categories = {}

        for metadata in all_data['metadatas']:
            if metadata:
                source = metadata.get('source', 'unknown')
                category = metadata.get('category', 'unknown')

                sources[source] = sources.get(source, 0) + 1
                categories[category] = categories.get(category, 0) + 1

        print(f"📈 Sources ({len(sources)} total):")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count} chunks")

        print(f"\n📈 Categories ({len(categories)} total):")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} chunks")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Assicurati che ChromaDB sia running su localhost:8001")
        return False

def check_local_files():
    """Verifica file locali in data/"""

    print("\n📁 Local Files Analysis:")
    print("-" * 30)

    data_dir = Path("apps/backend/data")

    if not data_dir.exists():
        print("❌ Directory data/ non trovata!")
        return

    # File principali
    main_files = []
    for ext in ['*.md', '*.json', '*.txt']:
        main_files.extend(data_dir.glob(ext))

    print(f"📄 Main files ({len(main_files)}):")
    for file_path in sorted(main_files):
        size = file_path.stat().st_size
        print(f"  {file_path.name} ({size:,} bytes)")

    # Subdirectories
    subdirs = [d for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    print(f"\n📁 Subdirectories ({len(subdirs)}):")
    for subdir in sorted(subdirs):
        file_count = len(list(subdir.rglob("*")))
        print(f"  {subdir.name}/ ({file_count} items)")

def main():
    """Main inspection"""

    # Check local files
    check_local_files()

    # Check ChromaDB
    print("\n" + "=" * 50)
    success = inspect_chromadb()

    if success:
        print("\n✅ ChromaDB inspection completed!")
        print("\n💡 ChromaDB Web Interface:")
        print("   http://localhost:8001 (basic UI available)")
        print("\n🔧 If data is missing, check:")
        print("   1. ChromaDB container is running")
        print("   2. RAG population was executed")
        print("   3. Files exist in apps/backend/data/")
    else:
        print("\n❌ Cannot connect to ChromaDB!")
        print("   Check: docker ps | grep chromadb")

if __name__ == "__main__":
    main()
