---
description: Paired quarter schedule fixture and pending financial refits.
---

# Paired schedule fixture

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`, the synthetic fixture
passed for 99 draws, seed 42, 12 quarters and expected block length 2.218.
It checked deterministic indices, original calendar order, label
correspondence and identical missingness across arms. The fixture addressed
schedule mechanics. The workspace's inference tests cover schedule
reproducibility and replicate-zero order.

The historical estimator computes MM betas once per common quarter draw, drops issuers with missing draw-specific beta or median, and restricts and renormalizes the graph. Its interval routine selects finite values independently by endpoint. A paired mean-minus-median analysis requires a common validity mask and must compute differences within each draw. Existing saved median draws cannot supply the missing mean arm or establish paired MM-refit intervals.

The coordinator verified raw CRSP SHA-256 `bb58e9f3ba63f9b713dd4015f851125a6db9d495bdd134e1395261fda44fa25c`, panel manifest `a56bd4ea963bcfd6556b75da3f769fffd875c1ce7593e776e21b1b642be594ff`, and representation manifest `eb059e01597fd5ef9db09a52c93912a100dcb76efce634eeb42dbaa75c8eefa7`. The coordinator reports exact parity for 39,600 fixed-formation quarter rows.

Financial paired refits and panel intervals remain pending verified point-fit contracts, the shared compute queue, and empirical runtime and fit diagnostics. The cause of historical 10-NN shrinkage remains unresolved. Terminal outcome limitations remain relevant.

## Financial runner and inventory

`paired_refit.py` consumes Agent 1's ordered 878-issuer return matrix, roster, literal exponential joint graph and point fits. It reconstructs the issuer-quarter observations from the study contract, checks the matrix, refits actual R MM betas on each common quarter schedule and compares original-sample no-intercept profile fits to both matched point fits. Python indexes outcomes directly with the same ordered schedule passed to R. R uses one worker. Within each draw both outcomes share the same finite beta and return mask and the same restricted, row-renormalized graph. The lag ML, error ML and lag IV slope and spatial estimates share an estimator-specific joint finite-fit rule. ML estimates within `1e-4` of the profile interval boundary fail that rule. Draw IDs, dropped issuer counts and paired differences are saved. The fixed-roster and shared-attrition summaries are separate. Each summary records attempted draws and joint failures and requires at least 80% of requested draws, rounded up. This is a pilot feasibility threshold, not a coverage guarantee.

A private fixture reversed the supplied roster. The runner rejected the
mismatch before graph or panel reads. This check used runner SHA-256
`527a917a69e3a342ce72623aed43f7ea909004fd278f1a011ea34b387ef0bb0d`
before the layout and formatting change.

The formation cohort, original characteristics and their graph are fixed. Within every draw the quarter sequence, issuer observation mask, mean and median returns, MM beta and spatial parameters are recomputed. Missing issuers induce a graph restriction and row renormalization. Checkpoints, representation extraction and graph construction are not refitted. The original median intercept fit is invalid and no paired intercept interval is produced. No independent coverage or stationarity assessment has been performed. The default expected block length 2.218 is rounded from the historical estimate. Sensitivities use 1.109 and 4.436 quarters and the same seed 42.

The runner compiled in the pinned environment. It has not been exercised on financial data, and its numerical parity assertions and runtime remain unverified. The following commands are pending until at least 20 GiB is free on the shared filesystem and the panel job has started. Run one at a time, starting with the baseline. `ulimit` applies a 16 GiB virtual-memory cap, which also constrains RSS, and the shell records elapsed time and the runner records Python and child peak RSS. Use the 99-draw resource and fit results before deciding whether a 999-draw run fits the deadline and budget.

```sh
mkdir -p /tmp/finfm-swarm
flock /tmp/finfm-swarm-compute.lock bash -c 'test "$(df -Pk /tmp | awk "NR==2 {print \$4}")" -ge 20971520 && ulimit -v 16777216 && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" && time timeout 1800 devenv shell -- just python::pilot finfm/paired_refit.py --source /tmp/finfm-swarm/mean-median --draws 99 --block 2.218 --output /tmp/finfm-swarm/t06/baseline' > /tmp/finfm-swarm/t06-baseline.log 2>&1
flock /tmp/finfm-swarm-compute.lock bash -c 'test "$(df -Pk /tmp | awk "NR==2 {print \$4}")" -ge 20971520 && ulimit -v 16777216 && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" && time timeout 1800 devenv shell -- just python::pilot finfm/paired_refit.py --source /tmp/finfm-swarm/mean-median --draws 99 --block 1.109 --output /tmp/finfm-swarm/t06/short' > /tmp/finfm-swarm/t06-short.log 2>&1
flock /tmp/finfm-swarm-compute.lock bash -c 'test "$(df -Pk /tmp | awk "NR==2 {print \$4}")" -ge 20971520 && ulimit -v 16777216 && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" && time timeout 1800 devenv shell -- just python::pilot finfm/paired_refit.py --source /tmp/finfm-swarm/mean-median --draws 99 --block 4.436 --output /tmp/finfm-swarm/t06/long' > /tmp/finfm-swarm/t06-long.log 2>&1
```

These commands create only task scratch outputs, including MM refits, paired draws, conditional percentile summaries and metadata. Capture output digests and review fit attrition and boundary rates before accepting any result. The panel interval requires the separately verified panel contributions and remains unimplemented.
