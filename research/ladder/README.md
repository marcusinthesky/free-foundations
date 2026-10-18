# Cross-sectional replication and measurement ladder

The reference is Viviana Fernández, *Spatial linkages in international financial
markets*, Quantitative Finance 11(2), 237–245 (2011),
[DOI](https://doi.org/10.1080/14697680903127403). This directory replaces the
earlier pilot-universe cross-section in [`research/fernandez`](../fernandez/README.md)
with the 1,000-issuer universe and adds a ladder that changes one component at a time.

## R0: practical replication

[`r0/`](r0/RESULTS.md) reproduces the paper's two-stage spatial CAPM as closely as
public US data allow:

1. Robust MM CAPM betas (`robustbase::lmrob`, MM) from 40 complete quarterly excess
   returns, 2016Q1–2025Q4, with an intercept.
2. Each firm's median quarterly excess return regressed on its beta, no intercept.
3. One network per characteristic from Spearman chord distances between 2015–2024
   annual histories, `exp(-d)`, row-normalized.
4. OLS with residual Moran's I, spatial lag by S2SLS with `[X, WX]` instruments,
   spatial error by concentrated Gaussian ML, Shapiro–Wilk, pseudo-R².

`common_four` is the faithful design: one firm sample with every network. With the
strict lease-inclusive debt definition it has only 33 firms; `common_three` drops debt
maturity (395 firms). `coverage_*` tables use each characteristic's maximal cohort and
are not comparable with each other. The
[replication manifest](r0/replication-manifest.md) separates reported choices,
implementation conventions and substitutions. Matching the paper's coefficient
magnitudes is not a success criterion.

## R1–R4: one combined network per row

Each [`four`](four/RESULTS.md) and [`three`](three/RESULTS.md) table holds firms,
outcome, exposures and estimator fixed; arms are never ranked against each other.

| Rung | Networks |
| --- | --- |
| Reference | Nonspatial OLS; uniform network |
| R0 single | Each Fernández characteristic network on the arm's cohort |
| R1 joint classical | RMS of Spearman distances; direct and Ledoit–Wolf Mahalanobis distance between joint ten-year histories |
| R2 matched learned | The same history rows: PCA, autoencoder, random autoencoder, supervised MLP, TabPFN, TabFM, EXAONE readouts |
| R2 alternate target | R2 with next-year net income/assets as the support label |
| R3 richer inputs | Histories plus 2024 broad SEC concepts, every method |
| R4 factors | Every network with FF5+momentum MM exposures (six premiums); the quarterly long-short factors are compounded daily-factor proxies, prod(1 + f) − 1 |

Foundation-model readouts are labelled by what they condition on. *State* readouts
(TabFM `early_concat`/`early_mean`, its null-label pass, EXAONE first-layer item
summaries) precede in-context prediction, although TabFM support labels still enter
its cell embeddings. *Task-conditioned* readouts (TabPFN query embeddings, TabFM
post-ICL states, EXAONE label token and last-layer summaries, the supervised MLP) are
`E(x | X_support, y_support)` for the declared support target.

Kernels: `exp` is equation (10); `median` divides distances by their median positive
value; `matched` chooses a bandwidth giving the joint Fernández network's effective
neighbour count. None is tuned on returns.

## Inference

- Standard errors: S2SLS per equation (2); ML from the information matrix,
  checked against `spreg`. The paper's outer-product standard errors cannot be
  reproduced because `log|I − λW|` has no per-observation decomposition.
- Residual Moran: exact Cliff–Ord moments for regression residuals, valid with
  self-links (spreg's `MoranRes` assumes a zero diagonal).
- Conditional AIC/BIC/HQIC with n = firms. Rows with equal parameter counts rank
  identically, so the criteria are informative across nonspatial/spatial rows and
  CAPM/FF5+momentum exposures only. No criteria for S2SLS.
- Generated-beta bootstrap: stationary resampling of quarters (expected block four),
  applied jointly to returns and factors; MM exposures and medians recomputed with
  W fixed; 199 valid replicates.
- Placebos: 99 permutations P W P' within 2024 log-assets terciles per network.

## Running

```sh
devenv shell just python-ladder      # R0 and R1-R4, both arms; R0 needs Rscript
```

Parquet matrices, bootstrap draws and R scratch files are ignored by Git, hashed
in `manifest.json` and held by DVC (`dvc pull research/ladder`).
