# Fixed-formation MM beta alignment

mkdir -p /tmp/finfm-swarm/t04
The 2015 fixed-formation MM betas were aligned by issuer to the January 2016 frozen TabPFN geometry. The 878 available estimates are an exact frame match to Agent 1's verified handoff, with unique issuer IDs and finite betas. All are in the 967-issuer geometry roster. The PCoA uses unit-normalized states centered on all 967 issuers, then selects the 878 matched coordinates. The beta-ranked response regressed on an intercept and the first three coordinates has in-sample R² **0.0024803**. The three coordinate-wise Spearman correlations are 0.0263, −0.0642 and −0.0202, with arbitrary eigenvector signs. A rotation and sign-change check preserves fitted values. The coordinator independently confirmed fixed-cohort quarter frame parity in `/tmp/finfm-swarm/cohort/manifest.json`.

MM beta is a separate return-derived target estimated from observed issuer and market returns. No beta-supervised readout was fitted to produce the frozen states or the PCoA coordinates. The rank-response OLS is a descriptive in-sample summary fitted after those coordinates were computed. The inputs and beta share economic and historical information, and no statistical independence is asserted. The 878 observations are the available-estimate subset. There is no structured null, interval, pricing test or inferential claim from this result. An independent review is pending.

The panel manifest SHA-256 is `a56bd4ea963bcfd6556b75da3f769fffd875c1ce7593e776e21b1b642be594ff`, representation manifest `eb059e01597fd5ef9db09a52c93912a100dcb76efce634eeb42dbaa75c8eefa7`, state `7c5162f1087d57e036a711d877db95f84a063d1e2a50a55258095869f673cca5`, saved roster `c5e88b57c8407c92cb45ef7c6d01ec1ded825022e7a45f9e2f3528091dd2ed67`, and handoff roster `655caeef7d9c353feec5913f77c8ea9bd92f0382a10788fc917864859ab2c4a0`. The ordered 878 issuer IDs hash to `abc44a4067b47b477b44cb85397ae7a1dd748109f4a7b31f3370ff9e2f605c1a`.

At revision `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`, run with the Agent 1 handoff present.

The original pilot is preserved at revision `0acc62f`. Reproduce the exhibit and beta overlay with the maintained stage.

```sh
devenv shell -- just dvc repro research_matched_historical_geometry
```

The live command computes the beta overlay alongside the candidate coordinates. The original standalone command and its output schema are preserved at revision `d2e6a21898d8a729f68dd177c6cc4b9f962ccaa4` in `src/python/pilots/finfm/beta_alignment.py`. The digest below belongs to that historical run.

The JSON SHA-256 is `4a882809d0fb2eef14c1e013bcec96219a2ada0365a03c5a50b486622e5bd794`. The run took 4.50 seconds and recorded 793,448 KiB peak process RSS. The inherited virtual-memory limit was 16 GiB. The JSON includes measured RSS, so a repeat can have a different JSON digest even when the estimates agree.
