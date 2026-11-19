---
description: Fixture replay and remaining requirements for the fixed-formation pricing test.
---

# Pricing pilot

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`, the arithmetic fixture replayed successfully with `devenv shell -- bash -c 'cd src/python && UV_CACHE_DIR=/tmp/finfm-uv-cache uv run --locked --offline --no-sync python ../../.context/plan/finfm-workshop/tasks/t05-sapt-restrictions/evidence/pricing_fixture.py'`. The script SHA-256 is `6697a62278c3c1e5b6f012df8bda627913b7300cf9058ef2d1892ef37f161b00`. Its output was `restricted 0.010000 0.000000; injected 0.010000 0.014142`. The fixture verifies arithmetic with known loadings and an orthogonal injected error. It does not validate inference.

The t03 matched 2015 formation contains 878 issuers over 40 quarters and 31,731 observed issuer-quarters. Using the saved untransformed MM beta and each issuer's arithmetic mean observed quarterly excess return, equal-issuer-weight ordinary least squares without an intercept gives a slope of **0.0205905130** and cross-sectional pricing-error RMS of **0.0367943052**, both in quarterly decimal return units. The loading matrix has rank 1. The empirical SEM point fit and this descriptive price have different estimating equations. The estimate is conditional on observed returns, with the terminal-outcome limitations in the cohort audit.

The script verifies the input digests, issuer order, all observed-quarter counts and medians against the saved roster. The t03 inputs and their preliminary status are described in [the matched comparison](../../t03-spatial-inference/evidence/mean_median.md). The issuer contributions are saved at `/tmp/finfm-swarm/pricing/issuer_contributions.csv`, SHA-256 `71ba0cfa3755b902954304f20b85d21d7547de0dee2880423d458e2f9c6a1136`. The result is `/tmp/finfm-swarm/pricing/result.json`, SHA-256 `25a60de5e2f6182dba31eac97dd78e2086e4dc264d4be63a0b1f93674b1a61f4`. The [script](pricing_mean.py) SHA-256 is `d8ac742dfb00df3086a5516aa13b8ffa08a8472e0d4596fa78a8cc1694c80f80`. It recorded 138,852 KiB peak RSS and 0.233 seconds elapsed for the Python command. The last free-space check before the calculation showed 23 GiB, but free space fell below 20 GiB afterward. Reproduce using the compute lock after the agreed 20 GiB free-space floor is restored.

```sh
flock /tmp/finfm-swarm-compute.lock env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' timeout 1800 devenv shell -- bash -c 'ulimit -v 16777216; time uv run --project src/python --offline --frozen --package free-foundations python .context/plan/finfm-workshop/tasks/t05-sapt-restrictions/evidence/pricing_mean.py'
```

For the exact null the restrictions are the N−1 components of mean returns orthogonal to the one-column loading matrix. With fewer quarters than issuers, the empirical covariance of these restrictions is rank deficient. An ordinary full-rank Wald inverse and standard chi-square reference therefore lack justification. Generated beta uncertainty, missing observations and time dependence also require an explicit procedure and validation. A lower-dimensional test needs prespecified contrast vectors and a validated joint null and critical values. The slope and RMS above are descriptive point estimates. No empirical joint test or interval is accepted here.

The mimicking-factor comparison requires t04.3 dated normalized weights, returns and spanning evidence alongside the t05.2 matched sample and an uncertainty procedure. These inputs have not been accepted in this receipt.
