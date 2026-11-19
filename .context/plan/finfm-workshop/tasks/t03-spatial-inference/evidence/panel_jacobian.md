# Panel likelihood fixture

Revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`. Run with `devenv shell -- just python::pilot finfm/panel_jacobian.py`.

The three-issuer symmetric row-normalized fixture matches the implementation to a direct Gaussian likelihood with an estimated period intercept for lag and error models at -0.7, 0 and 0.7, within 1e-10. The full Gaussian determinant includes the common eigenvalue. Removing the common mode changes each period's log determinant by `-log(1-rho)` and defines a distinct contrast likelihood. Numerical sensitivity on the saved sample remains pending.

The independent orthonormal-basis fixture also checks the full contrast likelihood for two unequal-size periods and non-symmetric row-stochastic graphs. For both processes at -0.7, 0 and 0.7, it matches the implementation within 1e-10. The contrast likelihood profiles variance using `sum(n_t - 1)` dimensions and removes the common-mode determinant. The earlier replay only removed the determinant and has been corrected before execution.

The historical pilot SHA-256 digests are `6b1555b1da84efd6c312d460e384836ba90032b35f3a21da4b7fd0cf1158eaf5` for `panel_jacobian.py`, `f23052db1093f71749d4aee6c2c4cdee9671ad35a51e97713f5f93f5bbf4d65e` for `panel_contrast.py` and `cbe4c75e0c73affc00002e165610c62182dccdbf330c7d5975a96921638039ba` for `panel_replay.py`. The saved beta table has columns `ticker` and `mm_beta`.

Saved source tables under `data/research/crsp-sec/experiments/comovement/summary` include 54,906 observations in 60 quarters. SHA-256 values are `0119a89ae972c890fe7897d2c77fd2d3504bbd8c6a519dd91128eb52dc8a50a6` for betas, `0b6b713bc547b1af611bce4689e5a2d262b162318ac7faad9c477f119219a42d` for contributions, `ef54d2b35069f5c8472f14e3b71a6642c91004f1614f9a1dda88169338d71c1e` for estimates and `162e75d81e8eedf0ba62e81544249bdd54782788f5241a4cc92f7e84abc0a521` for the ledger. These tables are historical inputs and require matched-mask and graph verification before use as new evidence.

A read of the saved estimates and contributions found 60 contributions per arm and process, summing to the saved log likelihoods. For direct and TabPFN respectively, the saved error coefficients are 0.288938 and 0.248992 and the lag coefficients are 0.277330 and 0.245428. At these full-likelihood optima, removing the common-mode Jacobian adds 20.4598 and 17.1803 to the error log likelihoods and 19.4882 and 16.8963 to the lag log likelihoods. These are fixed-coefficient Jacobian-only adjustments, not contrast-likelihood values or optima.

The full matched replay script is `panel_replay.py`. The compute lock was acquired but the available disk was 15,563,324 KiB, below the required 20 GiB, so the replay exited before loading inputs. Saved contribution pairing has not yet been verified against ordered issuer identities and graph hashes. The empirical numbers above remain historical results pending this verification.

A read-only pivot of `contributions.parquet` found exactly one value per network, process and quarter, with 60 common quarters from 2011-03-31 through 2025-12-31. The direct minus TabPFN saved log-likelihood contributions sum to 75.483841 for error and 56.222356 for lag. These are date-paired historical contributions, pending independent ordered-roster and graph verification.

Once the disk floor is restored, run the pending replay from the repository root:

```sh
mkdir -p /tmp/finfm-swarm/panel
flock /tmp/finfm-swarm-compute.lock bash -c 'test "$(df -Pk /tmp | awk "NR==2 {print \$4}")" -ge 20971520 || exit 40; ulimit -v 16777216; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""; time timeout 1800 devenv shell -- just python::pilot finfm/panel_replay.py --mask-receipt /tmp/finfm-swarm/panel/masks.json --output /tmp/finfm-swarm/panel > /tmp/finfm-swarm/panel/replay.log 2>&1'
```

Successful output is expected under `/tmp/finfm-swarm/panel/` as `graphs.csv`, `fits.csv`, `contributions.csv`, and `replay.log`. The script must be reviewed against historical output and its results independently checked before handing paired contributions to inference. The script has not been run past its disk preflight.

## Independent quarterly roster check

The coordinator reconstructed the ordered eligibility mask for every quarter
from the prepared table and saved MM betas. All 60 issuer counts agree with
the saved ledger, totaling 54,906 observations. Each annual state declares
both arms on the same issuer rows and contains every eligible issuer for its
four quarters. The check writes ordered-mask hashes for comparison during
the graph replay. The saved fit tables do not provide issuer-level hashes
against which to check those histories directly.

```sh
devenv shell -- just python::pilot \
  finfm/panel_masks.py \
  > /tmp/finfm-swarm/panel/masks.json
```

The standalone mask checker is preserved at revision `d2e6a21898d8a729f68dd177c6cc4b9f962ccaa4`. Run the mask command above from that revision to reconstruct the independent receipt for the live replay.

The roster receipt SHA-256 is
`1cb7a6000c2057ad9588277038a8059391242f31c10bb2e42f77f25cc919cc56`.

## Matched replay after pilot consolidation

The live replay verified all 60 ordered issuer masks against the independent
receipt before computing the fits. Both arms used those masks. The four
full-likelihood estimates and log likelihoods reproduced the saved fits to
the script's coefficient and likelihood tolerances. All 240 quarterly
likelihood contributions also agreed within 6 × 10⁻¹⁴. The contrast-likelihood
coefficients were 0.295910 and 0.254782 for error and 0.283879 and 0.250968
for lag, in direct and TabPFN order. The graph inventory CSV had SHA-256
`95868e8691cab599f973ddfa17e082a8731cf05720a949c50c8199e6954c871a`.
The historical tables provide no original graph hashes for comparison.
