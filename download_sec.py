#!/usr/bin/env python3
"""Download the PleIAs/SEC dataset from the Hugging Face Hub.

This pulls the dataset's raw data files (parquet) DIRECTLY with
``huggingface_hub`` and never executes a dataset loading script. That
avoids the modern ``datasets`` error:

    RuntimeError: Dataset scripts are no longer supported

which is raised whenever a dataset ships a ``.py`` loader (e.g.
``eloukas/edgar-corpus``). Downloading the files themselves sidesteps the
whole problem.

Usage
-----
    # Download the full dataset's parquet files -> data/sec/
    python download_sec.py

    # Quick sample: just the first parquet shard
    python download_sec.py --first-shard

    # A different repo (e.g. the script-based EDGAR-CORPUS) still works,
    # because we only download files, never run a loader:
    python download_sec.py --repo eloukas/edgar-corpus

Requires:  pip install huggingface_hub
Load it afterwards with:  pandas.read_parquet(...) or
datasets.load_dataset("parquet", data_files="data/sec/**/*.parquet")
"""

from __future__ import annotations

import argparse
from pathlib import Path

DATASET_ID = "PleIAs/SEC"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo", default=DATASET_ID, help=f"HF dataset id (default: {DATASET_ID})"
    )
    parser.add_argument(
        "--out", default="data/sec", help="output directory (default: data/sec)"
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=["*.parquet"],
        help="file glob patterns to fetch (default: *.parquet)",
    )
    parser.add_argument(
        "--first-shard",
        action="store_true",
        help="download only the first matching parquet file (a quick sample)",
    )
    args = parser.parse_args()

    # Imported here so --help works without the dependency installed.
    from huggingface_hub import hf_hub_download, list_repo_files, snapshot_download

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.first_shard:
        files = [
            f
            for f in list_repo_files(args.repo, repo_type="dataset")
            if f.endswith(".parquet")
        ]
        if not files:
            raise SystemExit(f"No .parquet files found in dataset repo '{args.repo}'.")
        target = sorted(files)[0]
        path = hf_hub_download(
            args.repo, target, repo_type="dataset", local_dir=str(out_dir)
        )
        print(f"Downloaded first shard to {path}")
        return

    # Download every matching data file directly (no script execution).
    path = snapshot_download(
        args.repo,
        repo_type="dataset",
        allow_patterns=args.patterns,
        local_dir=str(out_dir),
    )
    print(f"Downloaded data files to {Path(path).resolve()}/")


if __name__ == "__main__":
    main()
