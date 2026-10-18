# Python

A small typed interface for measuring firm proximity. The package imports NumPy,
not model runtimes, and never downloads weights on import.

## Install and check

From the repository root:

```sh
uv sync --project src/python --frozen
just python-check
just python-testmon
just python-model tabpfn
```

The default environment includes the `data` and `dev` dependency groups:
`spreg`, `libpysal`, `esda`, `yfinance`, `pandas-datareader`, `edgartools`,
`marimo`, Arrow, the scientific Python stack, and the quality tools.
`pandas-datareader` exposes the [Fama–French reader](https://pandas-datareader.readthedocs.io/en/latest/readers/famafrench.html)
for [Ken French's data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
EdgarTools requires an SEC identity before downloads; see its
[documentation](https://edgartools.readthedocs.io/en/latest/).
The [research pilot](../../research/pilot/README.md) adds cached data acquisition,
annual spatial-error comparisons, and a CPU TabPFN experiment.

`just python-model NAME` adds the selected model extra to the same environment
as the finance and development tools. `uv sync --project src/python --frozen
--all-extras` installs every retained model runtime together. A plain sync restores
the default environment without model extras.

Dependencies for all retained models must resolve together with the data stack.
Models that need conflicting dependency sets are deferred instead of adding
separate environments or dependency overrides. Resolution is not a claim that
checkpoints have been downloaded or inference tested. Linux uses CPU Torch wheels for this small pilot; CUDA/FlashAttention setups
require a separate deliberate environment choice.

## Catalogue

`MODELS` is a read-only mapping; `model_spec("tabpfn")` returns its metadata.
Git-only runtimes are pinned to commits in `pyproject.toml`; all resolved versions
are in `uv.lock`. Checkpoint identity is a separate, required encoding argument.

| Key / extra | Checkpoint | Readout available here |
| --- | --- | --- |
| `kumo` | [Kumo-Tabular Large](https://huggingface.co/nvidia/Kumo-Tabular) | Reviewed regression-head and earlier row features |
| `exaone` | [EXAONE-Tabular](https://huggingface.co/LG-AI-Research/EXAONE-Tabular) | Explicit custom extractor |
| `tabpfn` | [TabPFN 3.5](https://huggingface.co/Prior-Labs/tabpfn_3_5) | Native `get_embeddings` adapter |
| `limix` | [LimiX-2](https://huggingface.co/stable-ai/LimiX-2) | Reviewed regression-head features |
| `causilo` | [Causilo](https://huggingface.co/nums-ai/causilo) | Requires a supplied extractor |
| `tabfm` | [Google TabFM](https://huggingface.co/google/tabfm-1.1.0-pytorch) | Explicit custom extractor |
| `sap` | [SAP RPT](https://huggingface.co/SAP/sap-rpt-1-oss) | Requires a supplied extractor; gated weights |

The custom entries do not expose automatic native embedding integrations.
The [expanded experiment](../../research/expanded/README.md) includes reviewed
TabFM and EXAONE forward-pass extractors alongside full and Fast TabPFN. Supply a reviewed layer readout through the protocol below;
`from_fitted` rejects entries without a verified native row-embedding API.

`expanded.representations` names every readout used by the panel and cross-sectional
ladder and labels it *state* (TabFM `early_concat`/`early_mean` and a null-label pass,
EXAONE first-layer item summaries) or *task-conditioned* (TabPFN query embeddings,
TabFM post-ICL state, EXAONE label token and last-layer item summaries, a supervised
MLP control). New readouts are cached at float32 precision under per-model readout
versions. Spatial estimators live in `fernandez.models` (S2SLS, SEM-ML and lag-ML with
standard errors, checked against `spreg`), `fernandez.diagnostics` (exact residual
Moran, conditional information criteria) and `fernandez.kernels`. Paired bootstrap and
model confidence sets use `arch`. Stage-one MM betas call `fernandez/betas.R` through
the `Rscript` and `robustbase` supplied by `devenv`.

### Representative comparison and remaining landscape

The [four-model protocol](../../research/panel/three-foundations/README.md)
uses TabPFN, TabFM, Kumo Large and LimiX-2 with the same numerical inputs and
prediction-head extraction. The latter two adapters use pinned upstream
architectures on CPU; integration tests check prediction-head fidelity, frozen
parameters, and query-batch consistency. LimiX uses its Torch normalization
implementation, with the upstream CPU metadata alias supplied by the adapter.
Its runtime imports Triton even for this CPU path, so the Linux extra declares it.

The [ten-model landscape](../../research/panel/three-foundations/model-landscape.md)
also covers EXAONE, Nori, Causilo, Xiaomi TabLDM, SAP RPT-1, and Stanford RT-J.
Nori now provides the dedicated `synthefy-nori` runtime, and Xiaomi TabLDM now
publishes inference code; the older installation-blocker descriptions no longer
represent current availability. These two runtimes remain outside the declared
experiment and are not installed by its extras. SAP's semantic inputs and
RT-J's relational database interface also differ from the matched numerical
table used here. Existing EXAONE evidence remains on its original cohorts.

## Encode against a fixed context

Fit the upstream model separately, using only features and labels available at
the evaluation cutoff. For TabPFN 3.5, explicitly choose
`TabPFNRegressor.create_default_for_version(ModelVersion.V3_5)`; do not rely on an
upstream default model version. Then wrap the already-fitted model:

```python
from datetime import UTC, datetime

from free_foundations import Context, PanelBatch, from_fitted

encoder = from_fitted(
    "tabpfn",
    fitted_model,
    feature_names=("assets", "debt"),
    checkpoint="Prior-Labs/tabpfn_3_5@<resolved-revision>:<checkpoint-file>",
    preprocessing="<digest-of-fitted-preprocessing-and-seed>",
    context=Context(
        identifier="<digest-of-support-features-and-labels>",
        available_at=datetime(2024, 12, 31, tzinfo=UTC),
        row_ids=support_observation_ids,
    ),
)
result = encoder.encode(
    PanelBatch(
        values=query_features,
        row_ids=query_observation_ids,
        feature_names=("assets", "debt"),
        as_of=datetime(2025, 1, 1, tzinfo=UTC),
    )
)
vectors = result.values  # (query rows, dimensions), immutable
```

The adapter requests test/query states, transposes the documented
`(ensemble, rows, channels)` output, and concatenates ensemble members by default.
This avoids assuming that different members have aligned latent coordinates.
One-row TabPFN outputs are handled explicitly. Model fitting, preprocessing,
checkpoint/seed selection and device placement remain under the caller's control.

`PanelBatch` checks shape, observation identity, ordered feature schema, and a
timezone-aware information cutoff. `Context.available_at` includes label
availability. Encoding rejects future context and overlapping labeled observation
IDs before invoking inference. These checks cannot verify the caller's timestamps
or detect a backend refitted behind the wrapper: keep the fitted model fixed.
Historical observations of the same firm can be context if their observation IDs
and information dates differ appropriately.

## Custom extractors and pooling

`TabularEncoder` accepts an `Extractor`: a callable from `PanelBatch` to `Tokens`.
Return shape `(query rows, tokens, channels)` with an optional `(rows, tokens)`
mask. The extractor must preserve row order and remove context rows. It owns the
upstream forward pass, tensor conversion, chosen layer, device, and evaluation
mode. Set `readout` to an explicit layer/token description and `checkpoint` to a
resolved revision or local content hash. Never substitute class probabilities or
point predictions without naming that different measurement explicitly.

`MeanPooling()` averages valid, aligned tokens. `SelectToken(index)` selects an
explicit token; it does not guess that token zero is CLS. `ConcatenatePooling()`
preserves fixed token coordinates and rejects masked/variable layouts. Set
`normalize=True` explicitly on `TabularEncoder` for unit-length vectors; this
changes the metric and rejects zero vectors. Every result records these choices.

No automatic minibatching is applied: table/context attention can make a row's
representation depend on the other query rows. Treat the query cohort as part of
the experiment design. Equal output shapes do not make model coordinates aligned,
and good prediction does not establish that embedding distance is economically
valid. Compare distance/network performance within each measurement system.

## Design and checks

The dependency direction is `contracts` → `pooling` → `encoding`, with an
independent `registry`; Tach enforces the actual allowed imports. Ruff checks all
rules, Pyrefly uses its strict preset, and Vulture scans production code and tests
at 80% confidence. `just python-check` always runs the complete tests.
`just python-testmon` is the incremental development loop. Hypothesis exercises
axis permutations, singleton batches, masks, immutable outputs, and native
ensemble reshaping; focused tests check leakage guards and explicit failures.
These tests use small structural backends and do not validate checkpoint numerics.

## Fernández and the measurement target

I read *Spatial linkages in international financial markets*, Quantitative
Finance 11(2), 237–245 (2011), DOI 10.1080/14697680903127403, from the supplied
local PDF. Section 2.4 uses Spearman correlation distance
`sqrt(2 * (1 - correlation))` for financial-indicator histories, followed by
exponentiation and row normalization. Thus the benchmark is not simply a
single-date ratio distance. The pooled-country application uses 126 firms over
1997–2006, estimates betas from quarterly returns, then regresses median returns
on those betas; country-level evidence is mixed. It is not an out-of-sample test
of future FF5+momentum residual covariance.

This interface keeps checkpoint, context, preprocessing, pooling and observation
identity explicit because they define the learned measurement of proximity.
It makes no identification, causal-spillover, or economic-validity claim.
