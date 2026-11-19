# Python

Typed encoders and one financial measurement study. Importing the public interface
never downloads weights or imports an optional model runtime.

## Install and check

```sh
just python::setup         # locked workspace, model runtimes and tools (uses the network)
just python::check         # lint, strict types, Tach, test layout, Vulture, tests, build
just python::test-changed  # Testmon's impacted tests during development
just python::run processed prepare-panel
```

This directory is a uv workspace. The `free-foundations` application lives in
`apps/free_foundations`, with its tests in `apps/free_foundations/tests` mirroring
the source modules they exercise: `study/sources/sec.py` owns `tests/study/sources/test_sec.py` and
feature files such as `test_sec__parsing.py`. `just python::layout` enforces this.

The environment includes scientific Python, spatial estimators, Arrow, `arch`,
data-acquisition tools, DVC and quality checks. The model extras `tabpfn`, `tabfm`,
`kumo` and `limix` are installed by setup so strict type checking covers their
adapters. Model versions and Git revisions are locked in
`uv.lock`. Actual device selection is explicit and included in state provenance;
CUDA is used when available, with CPU fallback.

## Research commands

The [study contract](../../data/research/crsp-sec/README.md) has one parameter file,
[`params.yaml`](../../params.yaml), and one master panel. Commands are organized by
data layer, each with explicit inputs and outputs:

```sh
free-foundations raw acquire --crsp-csv X.csv --extraction-script X.py
free-foundations raw freeze        # promote completed staging
free-foundations raw fetch-checkpoints   # verify the four pinned weights
free-foundations processed prepare-panel # roster, mask, cohorts, characteristics
free-foundations processed prepare-contexts
free-foundations processed encode --rung fernandez --model tabpfn_full
free-foundations processed direct --rung fernandez
free-foundations processed assemble-states
free-foundations research replicate --formation 2015
free-foundations research collect-replication
free-foundations research estimate-comovement  # quarterly spatial panels
free-foundations research measure-alignment   # Mantel alignment
free-foundations publication render     # tables, figure, metrics
```

Run them through `just dvc repro <stage>` to honor dependencies. Acquisition is the
raw financial-source network boundary. Missing weights are fetched by raw fetch-checkpoints.

`cli` exposes the four layers. `study.sources` owns acquisition and source adapters,
`study.panel` owns panel preparation and verification, and `study.representations`
owns dated contexts, extraction and saved-state readers. `study.experiments`
produces research results and `study.publication` renders them. Reusable fitting
and graph methods live in `methods`, including the Fernández R estimator.
`encoders` owns the public interfaces and pinned backend adapters.

All research stages verify the shared panel, roster and outcome-mask hashes.
Features use dated disclosures before each quarter's trading cutoff. Native
missingness passes to tabular models; the direct control uses support-median
imputation with indicators. Deterministic column blocks retain every eligible field.

## Model catalogue

| Key / extra | Model | Retained readout |
| --- | --- | --- |
| `tabpfn` | TabPFN 3.5 | Native query embeddings |
| `tabfm` | Google TabFM 1.1 | Post-ICL query-row state |
| `kumo` | Kumo-Tabular Large | Query regression-head features |
| `limix` | LimiX-2 | Query regression-head features |

`MODELS` is read-only; `model_spec(name)` returns installation metadata. Checkpoint
identity is a separate required encoding argument. Model acquisition verifies
pinned expected bytes. Numerical state caches verify source/runtime/checkpoint
identity, ordered observations, payload checksums, shapes and finite values.
Historical cache entries cannot satisfy a changed extraction contract.

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
at 80% confidence. `just python::check` always runs the complete tests.
`just python::test-changed` is the incremental development loop. Hypothesis exercises
axis permutations, singleton batches, masks, immutable outputs, and native
ensemble reshaping; focused tests check leakage guards and explicit failures.
These tests use small structural backends and do not validate checkpoint numerics.
