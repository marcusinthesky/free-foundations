# Chronological panel designs

The [original panel](RESULTS.md) at this directory's root is the v1 record cited by
the report: one strict four-characteristic design, spherical innovations, the
`exp(-d)` kernel and late foundation-model readouts. Its files are left unchanged.

The extension runs three declared designs, each in its own subdirectory. Designs
differ in firms and must not be ranked against each other.

| Design | Cohort | Networks | Results |
| --- | --- | --- | --- |
| `four` | All four characteristics, three-year histories | Histories, broad and metrics rungs; alternate support target | [four](four/RESULTS.md) |
| `four-h5` | All four, five-year histories | Five- and three-year networks on the same firms | [four-h5](four-h5/RESULTS.md) |
| `three` | Cap/assets, market-to-book, dividend yield; five-year histories | All rungs, plus three-year networks on the same firms | [three](three/RESULTS.md) |

Every design fits one spatial coefficient per network, kernel and innovation arm on
2016–2019 and scores 2020–2025 daily excess-return densities:

- **Innovation arms.** `spherical` is the paper-aligned reference. `diagonal` gives
  every firm its own innovation variance under the same rule for every network; at
  λ = 0 it is exactly the diagonal FF5+momentum benchmark. `correlation` imposes prior
  raw sample variances on every approach, so only implied correlations differ.
- **Kernels.** `exp` (equation 10), `median`-scaled, and `matched` to that year's
  joint Fernández effective-neighbour count, separating neighbour ranking from the
  amount of smoothing.
- **Uncertainty.** Paired `arch` stationary-bootstrap intervals for summed daily
  differences (21- and 63-day expected blocks), model confidence sets within each
  kernel and innovation family, and within-size-tercile placebos `P W P'`.
- **Measurement audit.** [`audit/`](audit/summary.csv) re-encodes cohorts with query
  subsets, alternative support draws, shuffled or null support labels, and the
  alternate support target, reporting embedding drift and distance-rank agreement.

Distances carry a JSON sidecar fingerprint (context digest, readout, metric, code
hash) and are always recomputed from the fingerprinted embedding cache.
Run `devenv shell just python-panel [designs]` and `just python-encoder-audit`.
