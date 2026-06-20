# Graph-Theoretic Applications in Insurance Risk Management

A minimal quick-start for researching **graph-theoretic structure in firm risk disclosures**.

**Research question.** Can a network-level metric summarise a firm's exposure to risk, and do *network effects* propagate exposure between firms whose SEC disclosures share risk language?

## What's here

```
src/GTAIRM_0.ipynb   the notebook: stream data -> build graph -> metrics -> figure
data/input/          reserved for local inputs (empty for now)
data/output/         generated static graphs land here (e.g. risk_factor_network_2018.png)
docs/methodology.md  how the pipeline works, end to end
```

The notebook [`src/GTAIRM_0.ipynb`](src/GTAIRM_0.ipynb)

1. **streams** SEC 10-K filings from the Hugging Face Hub (nothing is stored locally),
2. builds a firm–firm graph from **Risk Factors** (Item 1A) text similarity,
3. computes centrality as an aggregate exposure metric, and
4. saves a static network figure to [`data/output/`](data/output).

## Data

[**EDGAR-CORPUS**](https://huggingface.co/datasets/eloukas/edgar-corpus) — a peer-reviewed corpus of the full text of every SEC 10-K (1993–2020), segmented into the standard 10-K items (Item 1A Risk Factors, Item 7 MD&A, …).

> Loukas, Fergadiotis, Androutsopoulos & Malakasiotis (2021). *EDGAR-CORPUS: Billions of Tokens Make The World Go Round.* ECONLP @ EMNLP. [arXiv:2109.14394](https://arxiv.org/abs/2109.14394)

The original script-based `load_dataset("eloukas/edgar-corpus", "full")` no longer works on modern `datasets`; the notebook reads the Hub's auto-generated **parquet** mirror with `streaming=True` instead, so no full corpus download is needed.

## Run it

Open in [Colab](https://colab.research.google.com/github/joehiggi/graph-theoretic-applications-in-insurance-risk-management/blob/main/src/GTAIRM_0.ipynb) (one click, no setup), or locally:

```bash
pip install datasets huggingface_hub pyarrow scikit-learn networkx pandas matplotlib
jupyter notebook src/GTAIRM_0.ipynb
```

See [`docs/methodology.md`](docs/methodology.md) for the full approach.

## License

Code: [MIT](LICENSE). Data attribution and citation: [`NOTICE`](NOTICE).
