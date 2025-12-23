#!/usr/bin/env python3
"""
HuggingFace Dataset Upload Script.

Uploads StudioCentOS content training dataset to private HuggingFace repo.

Usage:
    python scripts/upload_to_huggingface.py [--repo-id REPO] [--dry-run]

Environment:
    HF_TOKEN: HuggingFace write token (or use hardcoded token below)
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Try importing huggingface_hub
try:
    from huggingface_hub import HfApi, login, create_repo
    from datasets import Dataset, DatasetDict
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install huggingface_hub datasets")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

# HuggingFace Write Token (PRIVATE - do not share!)
HF_TOKEN = os.getenv("HF_TOKEN", "your_token_here")

# Default repo (PRIVATE)
DEFAULT_REPO_ID = "autuoriciro/studiocentos-content-training"

# Dataset paths
DATASET_PATH = Path(__file__).parent.parent / "data" / "studiocentos_vertical_dataset.jsonl"


def load_jsonl_dataset(path: Path) -> list:
    """Load JSONL file into list of dicts."""
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def prepare_dataset(data: list) -> Dataset:
    """Convert raw data to HuggingFace Dataset."""
    # Flatten messages for training
    processed = []
    for item in data:
        messages = item.get("messages", [])

        # Extract system, user, assistant
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), "")

        # Create training format (Alpaca-style)
        text = f"""### System:
{system_msg}

### User:
{user_msg}

### Assistant:
{assistant_msg}"""

        processed.append({
            "text": text,
            "system": system_msg,
            "instruction": user_msg,
            "output": assistant_msg,
            "post_type": item.get("post_type", "unknown"),
            "platform": item.get("platform", "unknown"),
            "sector": item.get("sector", "general"),
            "engagement_score": item.get("engagement_score", 0),
        })

    return Dataset.from_list(processed)


def main():
    parser = argparse.ArgumentParser(description="Upload dataset to HuggingFace")
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="HuggingFace repo ID")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded")
    parser.add_argument("--public", action="store_true", help="Make repo public (default: private)")
    args = parser.parse_args()

    print("=" * 60)
    print("🤗 StudioCentOS Dataset Upload to HuggingFace")
    print("=" * 60)
    print(f"\n📂 Source: {DATASET_PATH}")
    print(f"☁️  Target: {args.repo_id}")
    print(f"🔒 Visibility: {'PUBLIC' if args.public else 'PRIVATE'}")
    print(f"🔧 Mode: {'DRY RUN' if args.dry_run else 'LIVE'}\n")

    # Check dataset exists
    if not DATASET_PATH.exists():
        print(f"❌ Dataset not found: {DATASET_PATH}")
        sys.exit(1)

    # Load data
    print("📄 Loading dataset...")
    raw_data = load_jsonl_dataset(DATASET_PATH)
    print(f"   Found {len(raw_data)} examples")

    # Prepare dataset
    print("\n🔧 Preparing dataset...")
    dataset = prepare_dataset(raw_data)

    # Show stats
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total examples: {len(dataset)}")

    # Post type distribution
    post_types = {}
    for item in dataset:
        pt = item["post_type"]
        post_types[pt] = post_types.get(pt, 0) + 1
    print(f"\n   Post Types:")
    for pt, count in sorted(post_types.items()):
        print(f"      {pt}: {count}")

    # Platform distribution
    platforms = {}
    for item in dataset:
        p = item["platform"]
        platforms[p] = platforms.get(p, 0) + 1
    print(f"\n   Platforms:")
    for p, count in sorted(platforms.items()):
        print(f"      {p}: {count}")

    # Avg engagement
    avg_eng = sum(item["engagement_score"] for item in dataset) / len(dataset)
    print(f"\n   Avg Engagement Score: {avg_eng:.1f}")

    # Show sample
    print(f"\n📝 Sample (first example):")
    print(f"   Post Type: {dataset[0]['post_type']}")
    print(f"   Platform: {dataset[0]['platform']}")
    print(f"   Instruction: {dataset[0]['instruction'][:80]}...")

    if args.dry_run:
        print("\n🔧 DRY RUN - Not uploading")
        print("   Run without --dry-run to upload")
        return

    # Login to HuggingFace
    print(f"\n🔐 Logging in to HuggingFace...")
    login(token=HF_TOKEN)

    # Create repo if doesn't exist
    print(f"\n📦 Creating/checking repo: {args.repo_id}...")
    api = HfApi()
    try:
        create_repo(
            repo_id=args.repo_id,
            repo_type="dataset",
            private=not args.public,
            token=HF_TOKEN,
            exist_ok=True,
        )
        print(f"   ✅ Repo ready")
    except Exception as e:
        print(f"   ⚠️  {e}")

    # Split into train/validation
    print(f"\n📊 Splitting dataset (90/10)...")
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)

    # Create DatasetDict
    dataset_dict = DatasetDict({
        "train": split_dataset["train"],
        "validation": split_dataset["test"],
    })

    print(f"   Train: {len(dataset_dict['train'])} examples")
    print(f"   Validation: {len(dataset_dict['validation'])} examples")

    # Push to hub
    print(f"\n⬆️  Pushing to HuggingFace Hub...")
    dataset_dict.push_to_hub(
        args.repo_id,
        token=HF_TOKEN,
        private=not args.public,
    )

    print("\n" + "=" * 60)
    print("✅ UPLOAD COMPLETE!")
    print("=" * 60)
    print(f"\n🔗 Dataset URL: https://huggingface.co/datasets/{args.repo_id}")
    print(f"📊 Total examples: {len(dataset)}")
    print(f"🔒 Visibility: {'PUBLIC' if args.public else 'PRIVATE'}")

    print("\n💡 To use this dataset:")
    print(f'   from datasets import load_dataset')
    print(f'   dataset = load_dataset("{args.repo_id}")')


if __name__ == "__main__":
    main()
