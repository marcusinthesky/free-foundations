---
description: Qualification of the saved primary-formation Fernández-design baseline.
---

# Primary-formation baseline audit

The saved 2015 formation follows 878 estimator issuers through 2016–2025, using
their observed complete quarterly returns, subject to formation linkage and
minimum-history requirements. Missing quarters and uncertain terminal events
can select outcomes; see the [coverage receipt](../../t02-data-cohorts/evidence/coverage.md).
The
formation-date joint characteristic graph uses pairwise reranked Spearman chord
distances, root-mean-square aggregation across the four ratios, zero diagonal,
and the literal row-normalized `exp(-d)` kernel. This is a CRSP–SEC
reimplementation of the Fernández design, not a reproduction of her sample.
The saved no-intercept lag ML coefficient is 0.859996, with a conditional
statadic Wald interval [0.727213, 0.992778]. The intercept lag ML, lag IV and
error ML rows are all unavailable: statadic reports an invalid or boundary
fit. The no-intercept choice is part of the historical specification, not
evidence that an intercept is unnecessary.

The joint graph has no isolates, 836.81 effective neighbours and mean row total
variation from uniform 0.078935 (equivalently mean L1 distance 0.15787). Its
saved `neutral_pairs` value of 250,217 is the **maximum** of the four separate
characteristics' undefined-pair counts, not the number of neutral joint pairs.
Undefined component correlations, including constant histories or fewer than
two common slots, receive chord distance √2 before joint aggregation. Diffuse
weights and the boundary failures limit interpretation of the large coefficient.

The 999-draw stationary-quarter percentile interval for the same coefficient
is [0.224658, 0.964480], with median 0.857707. This refits generated betas,
medians and spatial models conditional on the selected formation graph, while
failed draw-specific fits can change the roster and restrict and renormalize
the graph. It is not an interval for an intercept model or a matched-graph
contrast, nor is coverage established by the saved draws. The refit audit and
remaining parity and attrition limitations are in [refit.md](../../t06-uncertainty-robustness/evidence/refit.md).

## Lineage and checks

Offline inspection used the saved replication parquet and manifest with the
frozen uv project and cached pinned devenv runtime libraries. The manifest
records study digest `e67c3891e2c66ad5a9677f20e15e76bc4e2fc44c8b902940cb205533dda1687d`.
The `dvc.lock` replication dependency on `infra/nix/devenv.nix` has MD5
`89be8d454f423d3525b8aa41bbbc05ef`, matching Git version `52028ba`; the
subsequent change `4bb2ea3` only adds TeX packages. The current `devenv.lock`,
`src/python/uv.lock`, and replication semantic fingerprint match their recorded
MD5s. This explains the changed dependency, but is not a full replay or a fresh
verification of every DVC input and output.

An independent bounded calculation reconstructed this joint graph from the
formation rows and characteristic histories, then profiled the no-intercept
lag model on the 878 saved original betas and medians. The fast coefficient
was 0.8599956361 versus saved statadic 0.8599956767; the premium differed by
6.34 × 10⁻¹⁰ and log likelihoods agreed to displayed precision. This checks
graph and profile parity on saved inputs, not a new robust beta fit.

A check after the study layout move used the same ordered 878 medians. The
cross-sectional sample standard deviation of peer averages was 0.000248 for
the joint exponential graph and 0.010649 for the binary, symmetrized 10-NN
graph built from the same joint ratios. These are decimal return units and
describe the graph calculation on the saved outcomes. The current replication
artifacts are in `data/research/crsp-sec/experiments/replication/summary/`.
