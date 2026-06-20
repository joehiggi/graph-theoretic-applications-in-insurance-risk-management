# Methodology

How the quick-start turns SEC disclosures into an exposure network.

## 1. Data

Source: [**EDGAR-CORPUS**](https://huggingface.co/datasets/eloukas/edgar-corpus) (`eloukas/edgar-corpus`) — the peer-reviewed full text of every SEC 10-K from 1993–2020, segmented into the standard items. See Loukas et al. (2021), [arXiv:2109.14394](https://arxiv.org/abs/2109.14394).

We **stream** from the Hub's auto-generated parquet mirror (`refs/convert/parquet`) with `streaming=True`. Rows are fetched lazily over HTTP, so the full corpus is never downloaded and nothing is stored locally. The legacy `load_dataset("eloukas/edgar-corpus", "full")` call no longer works because Hugging Face dropped script-based datasets.

Each record exposes `cik`, `year`, `filename`, and `section_1`…`section_15` (the 10-K items). We work with `section_1A` (Risk Factors) and optionally `section_7` (MD&A).

## 2. Graph construction

- **Nodes** — one per filer, keyed by `cik`.
- **Edges** — connect two firms when the cosine similarity of their TF-IDF–vectorised Risk Factors text exceeds `SIM_THRESHOLD` (default `0.30`). Edge weight is the similarity.

Edges therefore link firms that frame their risks in similar language — a proxy for shared exposure channels.

## 3. Aggregate exposure metric

Centrality on the similarity graph summarises how central a firm's risk profile is within the disclosure network:

- **Weighted degree** — total similarity mass a firm shares with others.
- **Eigenvector centrality** — recursively weights connections to other central firms; a candidate systemic-risk score.

## 4. Outputs

The notebook renders the network and saves a static PNG to [`../data/output/`](../data/output) as `risk_factor_network_<YEAR>.png`. `data/output/` is the home for generated static graphs; `data/input/` is reserved for any local inputs. Both are git-tracked as empty folders (`.gitkeep`) and their contents are gitignored.

## Extensions

- Map `cik` → SIC codes via the SEC company-facts API to isolate insurers/financials.
- Build temporal networks across years to track centrality through crises (2008, 2020).
- Swap TF-IDF for sentence embeddings, or build edges from MD&A (`section_7`).
- Validate by correlating centrality with realised volatility or rating downgrades.
