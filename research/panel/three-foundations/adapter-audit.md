# Frozen representation audit

The extraction point is the input to the model's regression prediction function,
which can itself contain nonlinear layers. It is not necessarily the input to
its final linear projection. The comparison uses one prediction member per model.

| Model | Source-level extraction route | Runtime treatment |
|---|---|---|
| TabPFN 3.5 | Native query embeddings are the `test_emb` argument to the bundled output heads; regression applies its residual MLP and output projection to this vector. | Official native embedding API, one estimator, CPU. |
| TabFM 1.1 | The post-context normalization output goes directly into the regression decoder. | Pinned official architecture, bfloat16 as in the existing experiment. |
| Kumo Large | A pre-forward hook observes the input to the in-context block's head. | Pinned official Large architecture, float32, CPU; one member. |
| LimiX-2 | A pre-forward hook observes the input to the regression decoder. | Pinned official architecture, float32, CPU; deterministic feature-position generator. |

Kumo and LimiX use query batches of 128, retaining the entire support table in
every batch. Their optional integration tests reconstruct the head outputs from
the extracted features, compare batched and unbatched query states, check finite
ordered arrays, and verify that parameter version counters do not change.
Both checkpoint tests passed before the financial run, with batching tolerances
of 0.00002 in absolute and relative error. These tests can be repeated with:

```sh
RUN_FOUNDATION_INTEGRATION=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 \
  src/python/.venv/bin/pytest -q src/python/tests/test_foundations.py
```

LimiX's CPU path uses its upstream Torch RMS normalization. The pinned runtime
reads the Triton spelling of the normalization width in one CPU attention path;
the adapter supplies the equivalent `normalized_shape` value as metadata. It
changes no checkpoint weights or normalization operations. The Linux extra
includes Triton because upstream imports it even when the Torch path is selected.

The prepared numerical feature table is common across models. Their prediction
interfaces retain their own internal preprocessing, and supplied outcomes are
normalized within the relevant context. Smaller encoder contexts therefore
change adaptation, including context normalization; the separate financial
calibration-size experiment holds that context fixed.

New cached feature arrays retain float32 precision. Cache identity includes
checkpoint revision, model and random seed identifier, context digest, and
readout version. The shared input contexts retain ordered firm identifiers,
feature names, labels, and historical cutoffs. The publication audit verifies
that these contexts and every unchanged overlapping score reproduce the earlier
three-support experiment.

## Observed initialization behavior

The completed run audited all 120 cached Kumo initialization readouts (three
seeds, ten years, four encoder contexts). Every array has exactly zero
within-cohort coordinate range across query firms. Upstream attention output
projections and residual feed-forward output projections are initialized at
zero, so the row readout tokens remain independent of query characteristics
before training. The financial decoder therefore receives constant features;
its fold-specific intercepts produce identical forecasts across the three draws.
The repeated scores and intervals are an architectural initialization property,
not three independent confirmations of pretraining value. The manuscript reports
this baseline explicitly and uses the varying TabPFN controls for the richer
weight comparison. No initialization rule was changed after examining scores.
