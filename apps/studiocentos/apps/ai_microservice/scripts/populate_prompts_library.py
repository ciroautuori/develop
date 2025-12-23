#!/usr/bin/env python3
"""
Prompts Library RAG Population Script.

Loads all prompt templates, brand guidelines, and campaign kits from
`prompts_library/` into ChromaDB for RAG-powered agent context injection.

Usage:
    python scripts/populate_prompts_library.py [--dry-run]

This enables agents to:
- Retrieve Brand DNA (Gold #D4AF37, Inter font) before generating content
- Access Campaign Kits for structured content generation
- Maintain consistent brand voice across all AI outputs
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.rag.service import rag_service


# Mapping of directory names to document types for metadata
DIRECTORY_TYPE_MAP = {
    "00_brand_identity": "brand_dna",
    "01_instagram": "prompt_template",
    "02_google_whisk": "prompt_template",
    "03_launch_campaign_v2": "campaign_kit",
}


async def load_prompts_library(dry_run: bool = False):
    """Load all prompt library files into RAG."""

    # prompts_library is at repo root
    prompts_dir = Path(__file__).parent.parent.parent / "prompts_library"

    if not prompts_dir.exists():
        print(f"❌ Directory not found: {prompts_dir}")
        return

    print("=" * 60)
    print("🚀 StudioCentOS Prompts Library RAG Population")
    print("=" * 60)
    print(f"\n📂 Source: {prompts_dir}")
    print(f"🔧 Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

    # Find all markdown files
    md_files = list(prompts_dir.rglob("*.md"))
    print(f"📄 Found {len(md_files)} prompt files:\n")

    uploaded = 0
    failed = 0

    for md_file in md_files:
        # Get the category folder name (e.g., "00_brand_identity")
        relative_path = md_file.relative_to(prompts_dir)
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"
        filename = md_file.name

        # Determine document type from category
        doc_type = DIRECTORY_TYPE_MAP.get(category, "prompt_template")

        print(f"  [{category}] {filename}...", end=" ")

        if dry_run:
            print(f"✅ (dry run, type={doc_type})")
            uploaded += 1
            continue

        try:
            content = md_file.read_text(encoding="utf-8")

            # Build metadata for RAG filtering
            metadata = {
                "type": doc_type,
                "category": category,
                "source": "prompts_library",
                "format": "markdown",
                "filename": filename,
            }

            # Extract special tags based on content
            if "GOLD_PRIMARY" in content or "#D4AF37" in content:
                metadata["has_brand_colors"] = True
            if "Inter" in content:
                metadata["has_typography"] = True
            if "Veo" in content or "veo" in content:
                metadata["model_target"] = "veo_vertex"
            if "Nano Banana" in content or "Imagen" in content:
                metadata["model_target"] = "nano_banana_pro"

            # Upload to RAG
            result = await rag_service.upload_document(
                filename=f"prompt_{category}_{filename}",
                content=content,
                metadata=metadata,
                user_id=1,  # System user
            )

            chunk_count = result.get("chunk_count", result.get("chunks_count", 0))
            print(f"✅ ({chunk_count} chunks, type={doc_type})")
            uploaded += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Uploaded: {uploaded}")
    print(f"❌ Failed: {failed}")
    print(f"📄 Total: {len(md_files)}")

    if not dry_run and uploaded > 0:
        print("\n🔍 Testing search capabilities...")

        # Test searches for important concepts
        test_queries = [
            ("Brand Identity", "brand gold color palette"),
            ("Visual Guidelines", "Nano Banana image generation"),
            ("Campaign Content", "announcement siamo tornati"),
            ("Video Prompts", "Veo Vertex video"),
        ]

        for name, query in test_queries:
            results = await rag_service.search(query=query, top_k=2, min_score=0.3)
            print(f"\n  🔎 {name}: '{query}'")
            if results:
                for r in results:
                    src = r.document.metadata.get("filename", "unknown")
                    doc_type = r.document.metadata.get("type", "unknown")
                    print(f"    → {src} (score: {r.score:.2f}, type: {doc_type})")
            else:
                print("    → No results found")

    print("\n✅ Done! Prompts Library is now in RAG.")
    print("   Agents can now call: rag_service.get_context('brand identity')")


async def main():
    parser = argparse.ArgumentParser(description="Populate RAG with Prompts Library")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading"
    )
    args = parser.parse_args()

    await load_prompts_library(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
