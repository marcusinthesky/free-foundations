---
description: Fixture replay and remaining requirements for the fixed-formation pricing test.
---

# Pricing pilot

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`, the synthetic
restriction check reproduced a price of 0.010000 and a pricing-error RMS
of zero. Injecting an orthogonal error left the price at 0.010000 and raised
RMS to 0.014142. The [restriction receipt](restriction.md) contains the
arithmetic and reproduction command.

The t03 matched 2015 formation contains 878 issuers over 40 quarters and 31,731 observed issuer-quarters. Using the saved untransformed MM beta and each issuer's arithmetic mean observed quarterly excess return, equal-issuer-weight ordinary least squares without an intercept gives a slope of **0.0205905130** and cross-sectional pricing-error RMS of **0.0367943052**, both in quarterly decimal return units. The loading matrix has rank 1. The empirical SEM point fit and this descriptive price have different estimating equations. The estimate is conditional on observed returns, with the terminal-outcome limitations in the cohort audit.

The script verifies the input digests, issuer order, all observed-quarter counts and medians against the saved roster. The t03 inputs and their preliminary status are described in [the matched comparison](../../t03-spatial-inference/evidence/mean_median.md). The historical issuer contributions were saved at `/tmp/finfm-swarm/pricing/issuer_contributions.csv`, SHA-256 `71ba0cfa3755b902954304f20b85d21d7547de0dee2880423d458e2f9c6a1136`. The historical result was `/tmp/finfm-swarm/pricing/result.json`, SHA-256 `25a60de5e2f6182dba31eac97dd78e2086e4dc264d4be63a0b1f93674b1a61f4`. The [live script](../../../../../../src/python/pilots/finfm/pricing_mean.py) replaces the historical script with SHA-256 `380857c76ae7af40cfbb41c7df4e243b5340c956a7c0a16c5e5be0adadac3de9`. It recorded 138,852 KiB peak RSS and 0.233 seconds elapsed for the Python command. The last free-space check before the calculation showed 23 GiB, but free space fell below 20 GiB afterward. Reproduce using the compute lock after the agreed 20 GiB free-space floor is restored.

```sh
flock /tmp/finfm-swarm-compute.lock env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' timeout 1800 devenv shell -- bash -c 'ulimit -v 16777216; time just python::pilot finfm/pricing_mean.py --source /tmp/finfm-swarm/mean-median --output /tmp/finfm-swarm/pricing'
```

For the exact null the restrictions are the N−1 components of mean returns orthogonal to the one-column loading matrix. With fewer quarters than issuers, the empirical covariance of these restrictions is rank deficient. An ordinary full-rank Wald inverse and standard chi-square reference therefore lack justification. Generated beta uncertainty, missing observations and time dependence also require an explicit procedure and validation. A lower-dimensional test needs prespecified contrast vectors and a validated joint null and critical values. The slope and RMS above are descriptive point estimates. No empirical joint test or interval is accepted here.

The mimicking-factor comparison requires t04.3 dated normalized weights, returns and spanning evidence alongside the t05.2 matched sample and an uncertainty procedure. These inputs have not been accepted in this receipt.

The live pilot also reports the mean of the 40 verified quarterly market
excess returns, the fitted premium minus that factor mean, and the RMS
under the factor-mean restriction. Each issuer mean uses its observed
quarters. The factor mean uses the common formation calendar. This
comparison is descriptive and has no joint-test critical value.

A fresh handoff reproduced the input digests and the fitted premium.
The quarterly market-factor mean was 0.0331025893, the fitted premium
minus that mean was −0.0125120763, and the factor-mean pricing-error RMS
was 0.0400639341 over the same 878 issuers.
