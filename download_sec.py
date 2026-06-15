#!/usr/bin/env python3
"""Download the PleIAs/SEC dataset from the Hugging Face Hub.

Usage
-----
    # Quick sample (streams, no full download) -> data/sec_sample.parquet
    python download_sec.py --limit 1000

    # Full dataset saved to disk -> data/sec/
    python download_sec.py

Requires:  pip install datasets
"""

from __future__ import annotations

import argparse
from pathlib import Path

DATASET_ID = "PleIAs/SEC"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split", default="train", help="dataset split to download (default: train)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="only fetch the first N records (streams a sample to parquet)",
    )
    parser.add_argument(
        "--out",
        default="data",
        help="output directory (default: data)",
    )
    args = parser.parse_args()

    from datasets import load_dataset  # imported here so --help works without it

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.limit is not None:
        # Stream just a sample so we never pull the whole corpus.
        stream = load_dataset(DATASET_ID, split=args.split, streaming=True)
        rows = list(stream.take(args.limit))
        from datasets import Dataset

        sample = Dataset.from_list(rows)
        out_file = out_dir / f"sec_{args.split}_sample.parquet"
        sample.to_parquet(str(out_file))
        print(f"Saved {len(sample)} records to {out_file}")
    else:
        # Full download, materialised to disk.
        dataset = load_dataset(DATASET_ID, split=args.split)
        out_path = out_dir / "sec"
        dataset.save_to_disk(str(out_path))
        print(f"Saved {len(dataset)} records to {out_path}/")


if __name__ == "__main__":
    main()
