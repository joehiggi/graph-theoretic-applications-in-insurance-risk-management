"""Graph-theoretic metrics over exposure networks.

These helpers summarise the structural importance of firms and the
prevalence of exposures, supporting the research question of whether an
aggregate, network-derived metric can describe a firm's risk exposure.
"""

from __future__ import annotations

from typing import Dict

import networkx as nx
import pandas as pd

from .graph import exposure_nodes, firm_nodes


def firm_centrality(graph: nx.Graph) -> pd.DataFrame:
    """Compute centrality metrics for the firm projection.

    Parameters
    ----------
    graph:
        A firm-firm network, typically from
        :func:`edgar_exposure.graph.project_firm_network`.

    Returns
    -------
    pandas.DataFrame
        One row per firm with ``degree``, ``weighted_degree``,
        ``betweenness``, ``eigenvector`` and ``clustering`` columns, sorted
        by descending weighted degree.
    """
    if graph.number_of_nodes() == 0:
        return pd.DataFrame(
            columns=[
                "firm",
                "degree",
                "weighted_degree",
                "betweenness",
                "eigenvector",
                "clustering",
            ]
        ).set_index("firm")

    degree = dict(graph.degree())
    weighted_degree = dict(graph.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(graph, weight="weight")
    clustering = nx.clustering(graph, weight="weight")
    try:
        eigenvector = nx.eigenvector_centrality_numpy(graph, weight="weight")
    except (nx.NetworkXException, ImportError):
        # Falls back gracefully for tiny or disconnected graphs.
        eigenvector = {node: float("nan") for node in graph.nodes()}

    frame = pd.DataFrame(
        {
            "degree": degree,
            "weighted_degree": weighted_degree,
            "betweenness": betweenness,
            "eigenvector": eigenvector,
            "clustering": clustering,
        }
    )
    frame.index.name = "firm"
    return frame.sort_values("weighted_degree", ascending=False)


def exposure_frequency(graph: nx.Graph) -> pd.DataFrame:
    """Count how many firms disclose each exposure.

    Parameters
    ----------
    graph:
        A bipartite firm-exposure graph from
        :func:`edgar_exposure.graph.build_exposure_graph`.

    Returns
    -------
    pandas.DataFrame
        One row per exposure with a ``firm_count`` column, sorted by
        descending frequency.
    """
    counts = {node: graph.degree(node) for node in exposure_nodes(graph)}
    frame = pd.DataFrame({"firm_count": counts})
    frame.index.name = "exposure"
    return frame.sort_values("firm_count", ascending=False)


def summary(graph: nx.Graph) -> Dict[str, float]:
    """Return high-level counts for a bipartite exposure graph.

    Parameters
    ----------
    graph:
        A bipartite firm-exposure graph.

    Returns
    -------
    dict
        Counts of firms, exposures and edges, plus graph density.
    """
    return {
        "n_firms": len(firm_nodes(graph)),
        "n_exposures": len(exposure_nodes(graph)),
        "n_edges": graph.number_of_edges(),
        "density": nx.density(graph) if graph.number_of_nodes() else 0.0,
    }
