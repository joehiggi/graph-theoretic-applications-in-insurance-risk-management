"""Disclosure-derived exposure networks from SEC 10-K filings.

This package turns the narrative risk disclosures in SEC 10-K filings
(distributed as the ``PleIAs/SEC`` dataset on the Hugging Face Hub) into
*exposure networks*: bipartite firm-to-risk graphs, and firm-to-firm
projections that connect companies sharing common disclosed exposures.

Modules
-------
loader
    Stream filings from the ``PleIAs/SEC`` dataset.
sections
    Split raw 10-K text into its canonical ``Item`` sections.
graph
    Detect disclosed exposures and build NetworkX graphs.
metrics
    Compute graph-theoretic centrality and exposure statistics.
viz
    Render graphs with Graphviz.
"""

from __future__ import annotations

from . import graph, loader, metrics, sections, viz

__all__ = ["loader", "sections", "graph", "metrics", "viz"]

__version__ = "0.1.0"
