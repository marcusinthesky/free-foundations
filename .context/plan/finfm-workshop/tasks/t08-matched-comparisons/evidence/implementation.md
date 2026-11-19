# T08 comparison and DVC handoff

The matched spatial panel uses the study's quarterly calendar, January
formation rosters, excess returns and quarter effects. The common analysis
mask requires observed returns and converged issuer exposures for each
declared factor set. All graph arms use that mask. French nonmarket inputs
use the study's compounded long–short proxies. The first-stage exposures are
estimated on the same calendar. Report their estimation burden separately
from the conditional likelihood criteria.

Rank the three input sets and four checkpoints by spatial lag log-likelihood
gain per issuer-quarter over the corresponding direct-input control. Use
market-only controls and symmetrized 10-NN weights for ranking. Use
`1e-8` nats per observation as the tie tolerance and record the declared
input and model order. Paired stationary-quarter intervals condition on the
original fits. Record all failures and withhold the overall selection when
the ranking grid is incomplete.

Use January 2016 for interpretation. The selected geometry triggers ablation
when the unrounded first-coordinate share of positive inertia exceeds 25%.
Record the selected and historical ratio geometries with their own identities.
Draw descriptive conclusions from the coordinate associations and changes
under re-encoding.

The manuscript handoff is the `publication_render_matched` DVC output under
`data/publication/crsp-sec/finfm-matched/`. The research evidence index
records each source path and digest. The submission-bundle owner cites the
qualified tables and scope notes from that output.

## Implementation verification

A smoke test against the local frozen inputs produced 105 contexts across
15 formation dates and seven input variants. The operand direct control
qualified for all 15 dates. The archived January 2016 PCoA replay used the
same 967-issuer formation roster. These smoke tests used scratch outputs.
The DVC stages own the corresponding evidence for the manuscript.

The January 2016 context and checkpoint identities matched the tested
native archive cells. Their native source fingerprints differ from the
current extraction path. Cells with that mismatch require fresh extraction.

The full Python gate passed with 270 tests and two optional checkpoint tests
skipped. LaTeX, context, Semflow and DVC graph checks passed. The existing
co-movement computation still occupied the empirical queue at handoff. The
T08 reproduction, publication evidence and Lean portion of the repository
gate remain pending.
