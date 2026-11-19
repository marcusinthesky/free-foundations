---
description: Preliminary matched mean and median spatial fits for the 2015 formation.
---

# Matched mean and median pilot

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`,
`mean_median.py` reconstructed the fixed 2015 formation using the saved available
roster and MM betas. It recomputes the joint characteristic distance and
row-normalized exponential graph and checks the 878 medians against the saved
roster. The 2016–2025 return matrix contains 31,731 observed issuer-quarters
for both summaries. Means are conditional on observed returns and subject to
the documented terminal-outcome limitation.

The no-intercept lag ML estimates are 0.8599956767 for medians and
0.8988004208 for means. Their beta slopes are 0.0029778950 and 0.0030468937.
The no-intercept error ML estimates are 0.9436676030 and 0.9661958934, with
slopes 0.0023787812 and 0.0024883384. The median intercept fits and mean
intercept error fit report invalid or boundary status. The mean intercept lag
fit reports -0.9278375816 with standard error 1.2681075401. This is a point
fit and does not establish an interval for the paired contrast. The pilot
checks saved parity on every available median fit. All four median fit statuses
match the saved rows.

As an issuer-quarter influence sensitivity, winsorizing the pooled observed
returns at the 1st and 99th percentiles, -0.441666 and 0.558397, preserves the
observation mask and saved betas. The no-intercept mean lag coefficient becomes
0.929534 and its beta slope 0.00167210. The mean error coefficient becomes
0.967166 and its slope 0.00095871. Both mean intercept fits become unavailable.
The median fits are unchanged. This sensitivity holds the original MM betas
fixed, so it does not measure the effect of refitting those betas.

Run from the repository root using the shared compute lock and one BLAS thread.

```sh
flock /tmp/finfm-swarm-compute.lock env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' timeout 1800 devenv shell -- bash -c 'ulimit -v 16777216; time just python::pilot finfm/mean_median.py --output /tmp/finfm-swarm/mean-median'
```

The pilot outputs are under `/tmp/finfm-swarm/mean-median/`. Their SHA-256
digests are `7a1005540fd58273537a2daf5c0daa5926bcca4457ffdb0b6d0f8df4ea354a6b`
for `fits.json`, `b0b414f35dee4e723350936b14348aa03be2685ed080530ac6ecdfd68d4dc76b`
for `returns.parquet`, `655caeef7d9c353feec5913f77c8ea9bd92f0382a10788fc917864859ab2c4a0`
for `roster.parquet`, and `482fce647389d208c1787ac9ea5b90872501c30794c4ad173c956f3e47274811`
for `weights.npy`. Rows and columns of the graph and return matrix follow the
available saved roster order. These files provide the paired-refit inputs.

The final measured run took 9.42 seconds with peak RSS 927,724 KiB. A 16 GiB
address-space limit and 30-minute timeout were set. Paired uncertainty and
an explicit mismatch-rejection test remain outstanding. Further empirical runs
are deferred until free disk space meets the agreed 20 GiB floor. The same
command above is the reproduction command once that floor is restored.
