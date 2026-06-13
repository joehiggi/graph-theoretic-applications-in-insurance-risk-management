# Graph-Theoretic Applications in Insurance Risk Management

Building **disclosure-derived exposure networks** from SEC 10-K filings.

## Project summary

This research project investigates graph-theoretic approaches to insurance
and investment risk. It mines the narrative risk disclosures in SEC 10-K
annual reports — distributed as the [`PleIAs/SEC`](https://huggingface.co/datasets/PleIAs/SEC)
dataset on the Hugging Face Hub — and turns them into **exposure networks**:

* a **bipartite firm-exposure graph**, linking each company to the risk
  themes (interest-rate risk, cybersecurity, supply chain, climate, ...) it
  discloses in *Item 1A. Risk Factors*; and
* a **firm-firm projection**, where companies are connected by the number of
  exposures they share.

The goal is to test (1) whether an aggregate, network-derived metric can
describe a firm's exposure to risk, and (2) whether there are network effects
of shared exposure across firms. Graphs are built with
[NetworkX](https://networkx.org/) and rendered with
[Graphviz](https://graphviz.org/).

## Repository layout

```
src/edgar_exposure/      # the pipeline, as importable modules
  loader.py              #   stream filings from PleIAs/SEC
  sections.py            #   split 10-K text into Item sections
  graph.py               #   detect exposures and build graphs
  metrics.py             #   centrality and exposure statistics
  viz.py                 #   Graphviz rendering
notebooks/               # Colab-compatible notebook mirroring the pipeline
tests/                   # offline pytest (tiny fixture, no downloads)
data/                    # local dataset cache (gitignored)
outputs/                 # generated graphs/figures (gitignored)
```

## Dataset & citation

Data: **`PleIAs/SEC`** — <https://huggingface.co/datasets/PleIAs/SEC>

The underlying 10-K corpus derives from **EDGAR-CORPUS**. Please cite:

> Lefteris Loukas, Manos Fergadiotis, Ion Androutsopoulos, and Prodromos
> Malakasiotis. *EDGAR-CORPUS: Billions of Tokens Make The World Go Round.*
> Proceedings of the Third Workshop on Economics and Natural Language
> Processing (ECONLP), EMNLP 2021. arXiv:[2109.14394](https://arxiv.org/abs/2109.14394).

```bibtex
@inproceedings{loukas-etal-2021-edgar,
    title = "{EDGAR}-{CORPUS}: Billions of Tokens Make The World Go Round",
    author = "Loukas, Lefteris and Fergadiotis, Manos and
              Androutsopoulos, Ion and Malakasiotis, Prodromos",
    booktitle = "Proceedings of the Third Workshop on Economics and
                 Natural Language Processing",
    year = "2021",
    publisher = "Association for Computational Linguistics",
    note = "arXiv:2109.14394",
}
```

Source filings are public-domain disclosures from the U.S. SEC EDGAR system.
See [`NOTICE`](NOTICE) for full attribution.

## Setup

### Local

Graphviz is a **system dependency** required by `pygraphviz`. Install it
*before* the Python packages:

```bash
# Debian/Ubuntu
sudo apt-get install -y graphviz graphviz-dev
# macOS
brew install graphviz

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .            # makes `edgar_exposure` importable
```

### Google Colab

```python
# 1. System Graphviz (needed by pygraphviz)
!apt-get -qq install -y graphviz graphviz-dev

# 2. Python packages
!pip install -q datasets networkx pygraphviz pandas

# 3. (optional) clone this repo to import the package
!git clone https://github.com/joehiggi/graph-theoretic-applications-in-insurance-risk-management.git
%cd graph-theoretic-applications-in-insurance-risk-management
!pip install -q -e .
```

Open [`notebooks/edgar_exposure_pipeline.ipynb`](notebooks/edgar_exposure_pipeline.ipynb)
for an end-to-end walkthrough.

## Usage

```python
from edgar_exposure.loader import load_filings_list
from edgar_exposure.graph import build_exposure_graph, project_firm_network
from edgar_exposure.metrics import firm_centrality, exposure_frequency
from edgar_exposure.viz import draw_graph

# Pull a small, bounded sample (streams; never downloads the full corpus).
filings = load_filings_list(limit=200)

# Build the bipartite firm-exposure graph and its firm-firm projection.
bipartite = build_exposure_graph(filings)
firms = project_firm_network(bipartite)

# Analyse.
print(firm_centrality(firms).head())
print(exposure_frequency(bipartite).head())

# Render with Graphviz.
draw_graph(bipartite, "outputs/exposure_network.png")
```

## Tests

The test suite is fully offline — it runs the section splitter and graph
builder on a tiny hardcoded fixture and never touches the network:

```bash
pip install pytest
pytest
```

## License

Code: [MIT](LICENSE). Data attribution: [`NOTICE`](NOTICE).
