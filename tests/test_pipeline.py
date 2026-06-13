"""Offline tests for the section splitter and graph builder.

These tests run entirely on a tiny hardcoded fixture; they never touch the
network or download the ``PleIAs/SEC`` dataset.
"""

from __future__ import annotations

import networkx as nx
import pytest

from edgar_exposure.graph import (
    EXPOSURE_KIND,
    FIRM_KIND,
    build_exposure_graph,
    find_exposures,
    project_firm_network,
)
from edgar_exposure.metrics import exposure_frequency, firm_centrality, summary
from edgar_exposure.sections import get_section, split_sections

# Two minimal, fictional 10-K excerpts. ACME and Globex both disclose a
# cybersecurity exposure (their shared edge in the firm projection), while
# only ACME mentions interest-rate risk and only Globex mentions supply chain.
ACME_10K = """
Item 1. Business
ACME Corp manufactures widgets.

Item 1A. Risk Factors
Our results are sensitive to interest rate movements on our debt.
We also face cybersecurity threats, including the risk of a data breach.

Item 7. Management's Discussion and Analysis
Revenue grew 4% year over year.
"""

GLOBEX_10K = """
Item 1. Business
Globex Inc provides logistics services.

Item 1A. Risk Factors
A disruption in our supply chain could harm operations.
We remain exposed to cybersecurity incidents such as ransomware.

Item 8. Financial Statements and Supplementary Data
See accompanying notes.
"""

FILINGS = [
    {"company": "ACME", "text": ACME_10K},
    {"company": "Globex", "text": GLOBEX_10K},
]


def test_split_sections_finds_items() -> None:
    sections = split_sections(ACME_10K)
    assert set(sections) == {"Item 1", "Item 1A", "Item 7"}
    assert "interest rate" in sections["Item 1A"].lower()
    # Item 1A text must not bleed into the following MD&A section.
    assert "Revenue grew" not in sections["Item 1A"]


def test_get_section_missing_returns_empty() -> None:
    assert get_section(ACME_10K, "Item 9A") == ""


def test_find_exposures_in_risk_factors() -> None:
    risk_text = get_section(ACME_10K, "Item 1A")
    exposures = find_exposures(risk_text)
    assert "Interest Rate Risk" in exposures
    assert "Cybersecurity" in exposures
    assert "Supply Chain" not in exposures


def test_build_exposure_graph_is_bipartite() -> None:
    graph = build_exposure_graph(FILINGS)

    firms = {n for n, d in graph.nodes(data=True) if d["kind"] == FIRM_KIND}
    exposures = {n for n, d in graph.nodes(data=True) if d["kind"] == EXPOSURE_KIND}

    assert firms == {"ACME", "Globex"}
    assert {"Interest Rate Risk", "Cybersecurity", "Supply Chain"} <= exposures
    assert nx.is_bipartite(graph)
    assert graph.has_edge("ACME", "Cybersecurity")
    assert graph.has_edge("Globex", "Supply Chain")
    assert not graph.has_edge("Globex", "Interest Rate Risk")


def test_firm_projection_weights_shared_exposures() -> None:
    graph = build_exposure_graph(FILINGS)
    projection = project_firm_network(graph)

    # ACME and Globex share exactly one exposure: Cybersecurity.
    assert projection.has_edge("ACME", "Globex")
    assert projection["ACME"]["Globex"]["weight"] == 1


def test_metrics_run_on_fixture() -> None:
    graph = build_exposure_graph(FILINGS)
    projection = project_firm_network(graph)

    stats = summary(graph)
    assert stats["n_firms"] == 2
    assert stats["n_edges"] == graph.number_of_edges()

    centrality = firm_centrality(projection)
    assert set(centrality.index) == {"ACME", "Globex"}

    frequency = exposure_frequency(graph)
    assert frequency.loc["Cybersecurity", "firm_count"] == 2


def test_empty_input_is_handled() -> None:
    assert split_sections("") == {}
    assert find_exposures("") == set()
    empty_graph = build_exposure_graph([])
    assert empty_graph.number_of_nodes() == 0
    assert summary(empty_graph)["n_firms"] == 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
