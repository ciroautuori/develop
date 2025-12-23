#!/usr/bin/env python3
"""
RAG Population Script - Popola il sistema RAG con case study StudioCentOS.

Usage:
    python scripts/populate_rag.py [--dry-run]

Requires:
    - AI microservice running
    - RAG service initialized
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.rag.service import rag_service


async def load_case_studies(dry_run: bool = False):
    """Load all case study markdown files into RAG."""

    case_studies_dir = Path(__file__).parent.parent / "data" / "case_studies"

    if not case_studies_dir.exists():
        print(f"❌ Directory not found: {case_studies_dir}")
        return

    print("=" * 60)
    print("🚀 StudioCentOS RAG Population Script")
    print("=" * 60)
    print(f"\n📂 Source: {case_studies_dir}")
    print(f"🔧 Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

    # Find all markdown files
    md_files = list(case_studies_dir.rglob("*.md"))
    print(f"📄 Found {len(md_files)} case study files:\n")

    uploaded = 0
    failed = 0

    for md_file in md_files:
        sector = md_file.parent.name
        filename = md_file.name

        print(f"  [{sector}] {filename}...", end=" ")

        if dry_run:
            print("✅ (dry run)")
            uploaded += 1
            continue

        try:
            content = md_file.read_text(encoding="utf-8")

            # Extract metadata from content
            metadata = {
                "type": "case_study",
                "sector": sector,
                "source": "studiocentos",
                "format": "markdown",
            }

            # Extract tags if present
            if "## Tags" in content:
                tags_section = content.split("## Tags")[-1].strip()
                tags = [t.strip().replace("`", "") for t in tags_section.split("`") if t.strip()]
                metadata["tags"] = tags[:10]  # Max 10 tags

            # Upload to RAG
            result = await rag_service.upload_document(
                filename=f"case_study_{sector}_{filename}",
                content=content,
                metadata=metadata,
                user_id=1,  # System user
            )

            print(f"✅ ({result.get('chunk_count', 0)} chunks)")
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
        print("\n🔍 Testing search...")
        # Test search
        for query in ["ristorazione sprechi", "hotel prenotazioni", "commercialista fatture"]:
            results = await rag_service.search(query=query, top_k=2)
            print(f"\n  Query: '{query}'")
            for r in results:
                print(f"    → {r.document.metadata.get('filename', 'unknown')} (score: {r.score:.2f})")

    print("\n✅ Done!")


async def main():
    parser = argparse.ArgumentParser(description="Populate RAG with case studies")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without actually uploading")
    args = parser.parse_args()

    await load_case_studies(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
