"""Detect disclosed exposures and build NetworkX exposure networks.

The pipeline models a filing as a set of *exposures* (risk themes) that
the company discloses in narrative text. Two graphs are produced:

* a **bipartite firm-exposure graph**, where an edge links a company to
  each risk theme it discloses; and
* a **firm-firm projection**, where two companies are connected with a
  weight equal to the number of exposures they share.

Exposure detection is deliberately simple and transparent: a curated
vocabulary maps a canonical risk label to a list of keyword patterns, and
a label is assigned to a filing whenever any of its keywords appears in
the target section. This keeps the network reproducible and easy to audit,
and the vocabulary can be swapped for a domain-specific one.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Mapping, Sequence, Set

import networkx as nx

from .sections import get_section

# Canonical exposure label -> keyword patterns (matched case-insensitively).
DEFAULT_EXPOSURES: Dict[str, Sequence[str]] = {
    "Interest Rate Risk": ["interest rate"],
    "Foreign Currency": ["foreign currency", "foreign exchange", "exchange rate"],
    "Credit Risk": ["credit risk", "counterparty", "creditworthiness"],
    "Commodity Prices": ["commodity", "raw material", "oil price", "fuel cost"],
    "Cybersecurity": ["cyber", "data breach", "information security", "ransomware"],
    "Supply Chain": ["supply chain", "supplier", "third-party manufacturer"],
    "Pandemic": ["pandemic", "covid", "epidemic"],
    "Climate": ["climate", "greenhouse", "extreme weather", "natural disaster"],
    "Litigation": ["litigation", "lawsuit", "legal proceeding"],
    "Regulatory": ["regulation", "regulatory", "noncompliance", "compliance"],
    "Competition": ["competition", "competitor", "competitive pressure"],
    "Liquidity": ["liquidity", "refinanc", "indebtedness"],
}

# Node attribute values distinguishing the two bipartite partitions.
FIRM_KIND = "firm"
EXPOSURE_KIND = "exposure"


def find_exposures(
    text: str,
    vocabulary: Mapping[str, Sequence[str]] = DEFAULT_EXPOSURES,
) -> Set[str]:
    """Return the set of exposure labels disclosed in ``text``.

    Parameters
    ----------
    text:
        Section (or full filing) text to scan.
    vocabulary:
        Mapping of exposure label to keyword patterns. A label is included
        when any of its keywords occurs in ``text`` (case-insensitive,
        substring match).

    Returns
    -------
    set of str
        The exposure labels detected in ``text``.
    """
    if not text:
        return set()
    lowered = text.lower()
    found: Set[str] = set()
    for label, keywords in vocabulary.items():
        if any(re.search(re.escape(kw.lower()), lowered) for kw in keywords):
            found.add(label)
    return found


def build_exposure_graph(
    filings: Iterable[Mapping[str, object]],
    *,
    vocabulary: Mapping[str, Sequence[str]] = DEFAULT_EXPOSURES,
    section: str = "Item 1A",
    firm_key: str = "company",
    text_key: str = "text",
) -> nx.Graph:
    """Build a bipartite firm-exposure graph from a collection of filings.

    For each filing the target ``section`` (by default ``Item 1A. Risk
    Factors``) is extracted; if that item is absent the full filing text is
    used as a fallback. Detected exposures become edges from the firm node
    to each exposure node.

    Parameters
    ----------
    filings:
        Iterable of mappings, each with at least a firm identifier under
        ``firm_key`` and raw filing text under ``text_key``.
    vocabulary:
        Exposure vocabulary passed to :func:`find_exposures`.
    section:
        Canonical item id whose text is scanned for exposures.
    firm_key:
        Mapping key holding the company identifier.
    text_key:
        Mapping key holding the raw 10-K text.

    Returns
    -------
    networkx.Graph
        Bipartite graph. Firm nodes carry ``kind="firm"`` and
        ``bipartite=0``; exposure nodes carry ``kind="exposure"`` and
        ``bipartite=1``.
    """
    graph = nx.Graph()
    for filing in filings:
        firm = filing[firm_key]
        text = str(filing.get(text_key, ""))
        target = get_section(text, section) or text
        graph.add_node(firm, kind=FIRM_KIND, bipartite=0)
        for exposure in find_exposures(target, vocabulary):
            graph.add_node(exposure, kind=EXPOSURE_KIND, bipartite=1)
            graph.add_edge(firm, exposure)
    return graph


def firm_nodes(graph: nx.Graph) -> List[object]:
    """Return the firm-partition nodes of an exposure graph."""
    return [n for n, d in graph.nodes(data=True) if d.get("kind") == FIRM_KIND]


def exposure_nodes(graph: nx.Graph) -> List[object]:
    """Return the exposure-partition nodes of an exposure graph."""
    return [n for n, d in graph.nodes(data=True) if d.get("kind") == EXPOSURE_KIND]


def project_firm_network(graph: nx.Graph) -> nx.Graph:
    """Project a bipartite firm-exposure graph onto its firm nodes.

    Two firms are connected with an integer ``weight`` equal to the number
    of exposures they jointly disclose. This firm-firm network is the basis
    for studying network effects of shared exposure.

    Parameters
    ----------
    graph:
        Bipartite graph produced by :func:`build_exposure_graph`.

    Returns
    -------
    networkx.Graph
        Weighted firm-firm projection.
    """
    return nx.bipartite.weighted_projected_graph(graph, firm_nodes(graph))
