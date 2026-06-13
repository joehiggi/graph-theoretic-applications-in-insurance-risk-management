"""Stream SEC 10-K filings from the ``PleIAs/SEC`` Hugging Face dataset.

The ``datasets`` import is performed lazily inside each function so that the
rest of the package (and the test suite) can be used without that heavy
dependency, and so that no network access occurs at import time.

Notes
-----
The exact field names exposed by ``PleIAs/SEC`` may evolve. The helpers
below normalise records into a small, stable schema (``company`` and
``text``) and accept overrides for the source field names.
"""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

DATASET_ID = "PleIAs/SEC"


def load_filings(
    *,
    split: str = "train",
    limit: Optional[int] = None,
    streaming: bool = True,
    text_field: str = "text",
    firm_field: str = "company",
):
    """Load the raw ``PleIAs/SEC`` dataset via :mod:`datasets`.

    Parameters
    ----------
    split:
        Dataset split to read (e.g. ``"train"``).
    limit:
        Maximum number of records to materialise; ``None`` reads all.
    streaming:
        When ``True`` (recommended), records are streamed rather than
        downloaded in full.
    text_field, firm_field:
        Reserved for callers that need to know the source field names;
        accepted for API symmetry with :func:`iter_filings`.

    Returns
    -------
    datasets.Dataset or datasets.IterableDataset
        The loaded dataset, optionally truncated to ``limit`` records.

    Raises
    ------
    ImportError
        If the optional :mod:`datasets` dependency is not installed.
    """
    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - exercised only without dep
        raise ImportError(
            "The 'datasets' package is required to load PleIAs/SEC. "
            "Install it with `pip install datasets`."
        ) from exc

    dataset = load_dataset(DATASET_ID, split=split, streaming=streaming)
    if limit is not None:
        dataset = dataset.take(limit) if streaming else dataset.select(range(limit))
    return dataset


def iter_filings(
    *,
    split: str = "train",
    limit: Optional[int] = None,
    streaming: bool = True,
    text_field: str = "text",
    firm_field: str = "company",
) -> Iterator[Dict[str, str]]:
    """Yield normalised filing records with ``company`` and ``text`` keys.

    Each yielded mapping has the stable shape consumed by
    :func:`edgar_exposure.graph.build_exposure_graph`. Records missing the
    text field are skipped; a missing firm field falls back to a synthetic
    ``filing-{i}`` identifier.

    Parameters
    ----------
    split, limit, streaming:
        Forwarded to :func:`load_filings`.
    text_field:
        Source field holding the raw 10-K text.
    firm_field:
        Source field holding the company identifier.

    Yields
    ------
    dict
        ``{"company": ..., "text": ...}`` records.
    """
    dataset = load_filings(split=split, limit=limit, streaming=streaming)
    for index, record in enumerate(dataset):
        text = record.get(text_field)
        if not text:
            continue
        firm = record.get(firm_field) or f"filing-{index}"
        yield {"company": str(firm), "text": str(text)}


def load_filings_list(
    *,
    split: str = "train",
    limit: int = 100,
    text_field: str = "text",
    firm_field: str = "company",
) -> List[Dict[str, str]]:
    """Materialise a bounded list of normalised filing records.

    A convenience wrapper around :func:`iter_filings` for notebooks and
    quick experiments. ``limit`` is required to avoid accidentally pulling
    the full corpus.

    Parameters
    ----------
    split:
        Dataset split to read.
    limit:
        Number of records to collect.
    text_field, firm_field:
        Source field names forwarded to :func:`iter_filings`.

    Returns
    -------
    list of dict
        Up to ``limit`` normalised filing records.
    """
    return list(
        iter_filings(
            split=split,
            limit=limit,
            streaming=True,
            text_field=text_field,
            firm_field=firm_field,
        )
    )
