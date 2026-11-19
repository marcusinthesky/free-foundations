# Common-roster PCoA comparison

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`, the frozen `fernandez:tabpfn_full` states for quarters ending 2016-03-31 and 2017-03-31 contain 967 and 959 issuers. Their intersection contains 850 issuers, ordered ID SHA-256 `83b82d8687a1c833b411dd85fd0456cc54e4d934d7968153fb5bcf`. After unit normalization and recentering on that intersection, the three principal angles between the top-three issuer-coordinate subspaces are 18.77, 25.00 and 38.61 degrees. This is a descriptive two-date comparison with no null distribution or interval.

The state hashes are `7c5162f1087d57e036a711d877db95f84a063d1e2a50a55258095869f673cca5` and `878962fc2abd887492875146918859f75b1e545906b85dbb139d8118b7419571`. Panel and representation manifest hashes match the coordinator's verified cohort receipt. The script checks the representation store provenance and includes a rotation and sign invariance fixture.

Run from the repository root with the pinned environment and the shared compute lock.

```sh
flock /tmp/finfm-swarm-compute.lock env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' timeout 1800 devenv shell -- bash -c 'ulimit -v 16777216; time uv run --offline --project src/python --locked python .context/plan/finfm-workshop/tasks/t04-pcoa-interpretation/evidence/stability.py' > /tmp/finfm-swarm/t04/stability.json 2> /tmp/finfm-swarm/t04/stability.log
```

Output SHA-256 is `c1aeb49837f1ee95548cb9bd2a2d1e04c1ba1dc72808f81534625cd9849d71f9`. Elapsed time was 4.51 seconds. The 16 GiB virtual memory limit was enforced. Peak RSS was not recorded in this run.

The saved January 2016 pilot also replayed successfully under the same lock and environment. Its output at `/tmp/finfm-swarm/t04/pilot.json` has SHA-256 `1bb27acffd36a1ba2d42d283c9dfb66ce51faa573259c63d60a2ecc017a370aa` and elapsed time 7.60 seconds. Its original method and limitations are in `interpretation.md`.

The fixed-formation beta alignment is recorded separately in `beta-alignment-receipt.md`. For t04.3, formation-dated normalized holdings and their timing relative to return observations have not been established. The source cannot identify terminal events or guarantee terminal-return coverage, so portfolio exit and settlement accounting is unresolved. Spanning evidence and interval assumptions are also unavailable. Consequently, these receipts support descriptive geometry and beta alignment, with no mimicking-factor, spanning, pricing or inferential stability claim. Both results await independent review.
