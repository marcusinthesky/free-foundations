# Expanded financial-topology experiment

[Results](RESULTS.md) · [Matrix inventory](distance-inventory.csv) · [Matrix audit](distance-audit.json)

Run `just python-expanded` from the repository root after the original
[pilot](../pilot/README.md). It reuses that pilot's cached SEC disclosures,
Yahoo prices, Fama–French factors and issuer cohort. Model weights are pinned to
immutable revisions and downloaded only if missing. SEC identity is needed only
when fetching the current SIC control; set `EDGAR_IDENTITY` in your environment.

## Inputs and timing

Each evaluation year 2016–2025 uses disclosures publicly filed by the preceding
December 31. The original pilot's eligible annual cohort is preserved: 80–95
firms from the 100-issuer universe. A matrix labeled **2016** therefore measures
proximity at **2015-12-31**, for evaluation on 2016 residual returns.

Three predetermined views are compared:

| View | Inputs before missingness indicators |
| --- | --- |
| `core19` | Log assets and the original 18 accounting ratios |
| `broad` | Up to 200 reported US-GAAP concept/unit/period combinations, signed-log transformed |
| `metrics` | First 100 broad concepts normalized by assets where in USD, plus annual differences and log assets |

The broad panel contains 5,010 candidate columns from entity-wide standard
US-GAAP facts. It is **not complete raw XBRL**: custom tags, segment contexts,
quarterly flows and non-USD monetary units are excluded. Instantaneous stocks
and 300–380-day annual flows remain separate. Concepts are selected by coverage
of at least 20% in the two support periods, with a 200-column cap and deterministic
tie-breaking. Future observations do not determine earlier vocabularies.

The metrics view retains per-share and dimensionless values, log-transforms
share counts, and divides USD concepts by the snapshot's assets. Differences are
one-year snapshot differences, not growth rates. Concepts are independently
selected from the latest available facts; this pilot does not guarantee that all
numerators and denominators refer to identical fiscal periods.

Support features come from snapshots `t-3` and `t-2`; support labels are the
following snapshot's net income/assets or operating cash/assets. Both contexts
use the same rows with both labels observed. Query features come from `t-1`.
Median imputation, missingness indicators and standardization are fitted only on
support rows, followed by clipping to [-8, 8]. No return labels enter these model
contexts. The query cohort remains fixed across models within a year.
Models receive numerical tables; concept names identify columns for provenance
and are not supplied as text embeddings.
The original pilot and its retained conventional benchmarks use mean imputation;
the expanded model/compression views explicitly use median imputation. The original
pilot documentation has been corrected to describe its actual mean imputation,
without changing its numerical results.

## Readouts

| Model | Readout | Dimensions |
| --- | --- | --- |
| TabPFN 3.5 Fast | Native query embeddings, one ensemble member | 1,024 |
| TabPFN 3.5 full | Native query embeddings, one ensemble member | 1,024 |
| Google TabFM 1.1 | Pre-ICL row tokens, concatenated | 1,024 |
| Google TabFM 1.1 | Pre-ICL row tokens, mean pooled | 128 |
| Google TabFM 1.1 | Post-ICL normalized query state | 1,024 |
| EXAONE Tabular | Query label token entering the quantile decoder | 192 |

All models use frozen pretrained weights on CPU. TabFM uses its checkpoint's
actual configuration with strict weight loading and bfloat16 computation.
Its early readouts are still conditioned on the support table and labels;
“pre-ICL” does not mean context-independent. Later panel and ladder runs add a TabFM null-label pass and EXAONE first- and last-layer item summaries; see [`research/panel`](../panel/README.md). EXAONE uses one member, uniform
weighting and no SVD feature augmentation. These are internal representations,
not prediction vectors. This compares selected readouts under a common input
recipe, rather than each vendor's tuned predictive pipeline. The experiment's
reviewed custom extractors pass through
the shared `TabularEncoder` contract; `from_fitted` remains limited to TabPFN's
native API.

PCA with 16 components, a small denoising autoencoder and that autoencoder's
untrained encoder provide compression controls. The autoencoder is fitted only
on support rows with a fixed seed and fixed training schedule. It is not an
architecture-matched random transformer control.

## Distances and spatial weights

Primary distances are Euclidean distances between unit-normalized row vectors:

```text
u_i = z_i / ||z_i||
d_ij = ||u_i - u_j|| = sqrt(2 * (1 - cosine(z_i, z_j)))
```

This is a metric on normalized vectors and a pseudometric on raw vectors:
positive rescalings of a vector become indistinguishable. Zero vectors are
rejected. It preserves angles, avoids embedding magnitude dominating proximity,
and is invariant to orthogonal rotations. It is not invariant to arbitrary
invertible transformations and does not establish economic identification.
Ordinary Euclidean distance is saved as a predetermined sensitivity check;
embedding coordinates are not separately standardized or whitened.

For each configuration, spatial weights are `exp(-d_ij² / h)`, with `h` the
median positive squared pairwise distance, zero diagonal and row normalization.
No returns select the metric or bandwidth. Distance matrices are symmetric;
row-normalized weights need not be. Distances across models or years do not
have a common calibrated economic scale. Annual changes also reflect rolling
support contexts, preprocessing and selected vocabularies. This run therefore
does not identify changes in firm fundamentals as the sole source of changing
network topology; that would require a fixed-reference measurement check.

Matrices are ticker-labeled Parquet tables, for example:

```python
from pathlib import Path

import pandas as pd

root = Path("research/expanded")
path = root / "distances/2016/core19__income__tabpfn_full__late__chord.parquet"
distance = pd.read_parquet(path)
assert distance.index.tolist() == distance.columns.tolist()
```

There are 72 foundation-model distance matrices per year: three input views,
two label contexts, six readouts and two metrics. Additional baseline matrices
are also retained. `distance-inventory.csv` records paths, information cutoffs, cohort size,
dimensionality, bandwidth and distance dispersion. `schemas/` records feature
names, ordered query tickers and context digests. Cached embedding files retain
checkpoint and support-row provenance. `manifest.json` records source, lockfile
and original pilot artifact hashes; checkpoint revisions and weight hashes are
recorded in `checkpoints.json` and the manifest. Raw data and weights stay in ignored
`cache/` directories; labeled distances and compact result tables are reviewable.

## Evaluation and interpretation

The original pilot's three-year factor regression and spatial-error estimator
are reused. The six factors are FF5 plus momentum. Realized evaluation-period
factors are used to measure residual dependence, not to forecast total returns.
Gaussian covariance loss and residual minimum-variance portfolio risk are
compared against diagonal and Ledoit–Wolf covariance controls.

Controls include current two-digit SIC, size, missingness and the age of each
fact's **period end**. The name `disclosure_age` in artifacts refers to period-end
age, not time since filing. Current SIC is explicitly not point-in-time.
Late-readout chord networks also receive unrestricted, within-industry and
within-size-quartile permutations. These are diagnostics, not causal controls.

The universe ignores survivorship as requested. Historical evaluation results
were already examined in the original pilot, so this expanded grid is a
**development study**, not a fresh holdout or confirmatory model-selection test.
Model versions are selected retrospectively; the TabPFN 3.5 checkpoints date
from 2026, after the evaluation window. This is not a historically deployable
strategy backtest. Pretraining exposure to historical data is not audited, and
filing-date discipline does not resolve that issue. Context, metric and
pooling sensitivity must be reported; selecting the best configuration after
seeing these results would require a new evaluation period.

The subsequent representative-model experiment is documented in
[the four-model protocol](../panel/three-foundations/README.md). It adds pinned
Kumo-Tabular Large and LimiX-2 prediction-head readouts to TabPFN and TabFM.
The [model landscape](../panel/three-foundations/model-landscape.md) records all
ten candidates and distinguishes empirical inclusion from catalogue coverage.
Nori now has a dedicated public runtime, and Xiaomi TabLDM provides inference
code; the earlier installation notes are historical, not current availability
claims. SAP checkpoint access remains gated. Existing EXAONE results retain
their original cohorts and specifications.
