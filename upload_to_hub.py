#!/usr/bin/env python3
"""Upload a processed file to a PUBLIC Hugging Face dataset repo.

Companion to ``download_sec.py``. Pushes a local parquet/csv/json file to a
dataset repo so any Colab notebook can later do
``load_dataset("<your-user>/<name>")`` with zero hosting cost.

Usage
-----
    # one-time auth: create a WRITE token at
    #   https://huggingface.co/settings/tokens
    huggingface-cli login        # or set HF_TOKEN in the environment

    python upload_to_hub.py data/sec/part-0.parquet joehiggi/sec-exposure

Requires:  pip install datasets huggingface_hub
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="local data file (.parquet, .csv, or .json)")
    parser.add_argument("repo", help="target repo id, e.g. joehiggi/sec-exposure")
    parser.add_argument(
        "--split", default="train", help="split name to store under (default: train)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="create the repo as private (default: public)",
    )
    args = parser.parse_args()

    from datasets import Dataset

    src = Path(args.file)
    if not src.exists():
        raise SystemExit(f"File not found: {src}")

    suffix = src.suffix.lower()
    if suffix == ".parquet":
        dataset = Dataset.from_parquet(str(src))
    elif suffix == ".csv":
        dataset = Dataset.from_csv(str(src))
    elif suffix in (".json", ".jsonl"):
        dataset = Dataset.from_json(str(src))
    else:
        raise SystemExit(f"Unsupported file type: {suffix} (use parquet/csv/json)")

    dataset.push_to_hub(args.repo, split=args.split, private=args.private)
    visibility = "private" if args.private else "public"
    print(
        f"Pushed {len(dataset)} records to {visibility} repo "
        f"https://huggingface.co/datasets/{args.repo}"
    )


if __name__ == "__main__":
    main()
