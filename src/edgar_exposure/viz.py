"""Render exposure networks with Graphviz.

Rendering uses ``pygraphviz`` (via NetworkX's ``nx_agraph`` bridge), which
in turn requires the system Graphviz binaries. Firm and exposure nodes are
styled differently so the bipartite structure is visible at a glance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import networkx as nx

from .graph import EXPOSURE_KIND, FIRM_KIND

PathLike = Union[str, Path]

# Visual styling for each node partition.
_FIRM_STYLE = {"shape": "box", "style": "filled", "fillcolor": "#cfe8ff"}
_EXPOSURE_STYLE = {"shape": "ellipse", "style": "filled", "fillcolor": "#ffe0b3"}


def to_agraph(graph: nx.Graph, *, layout: str = "dot"):
    """Convert a NetworkX exposure graph to a styled PyGraphviz ``AGraph``.

    Parameters
    ----------
    graph:
        A bipartite firm-exposure graph or a firm-firm projection.
    layout:
        Graphviz layout engine (``dot``, ``neato``, ``fdp``, ...).

    Returns
    -------
    pygraphviz.AGraph
        The laid-out graph, ready to ``draw``.

    Raises
    ------
    ImportError
        If ``pygraphviz`` (and the Graphviz system package) is unavailable.
    """
    agraph = nx.nx_agraph.to_agraph(graph)
    for node in agraph.nodes():
        kind = node.attr.get("kind")
        style = _FIRM_STYLE if kind == FIRM_KIND else _EXPOSURE_STYLE
        if kind not in (FIRM_KIND, EXPOSURE_KIND):
            style = _FIRM_STYLE
        node.attr.update(style)
    agraph.layout(prog=layout)
    return agraph


def draw_graph(
    graph: nx.Graph,
    path: PathLike,
    *,
    layout: str = "dot",
) -> Path:
    """Render an exposure graph to an image file with Graphviz.

    Parameters
    ----------
    graph:
        The graph to render.
    path:
        Output path; the file extension (``.png``, ``.svg``, ``.pdf``)
        selects the output format.
    layout:
        Graphviz layout engine.

    Returns
    -------
    pathlib.Path
        The path the image was written to.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    agraph = to_agraph(graph, layout=layout)
    agraph.draw(str(out))
    return out
