---
type: task
title: Attribute peer selection to financial feature groups with shapiq
description: Attribute peer selection to financial feature groups with shapiq
links: []
status: backlog
---

# Attribute peer selection to financial feature groups with shapiq

## Goal

Explore an optional appendix question after the primary ablation. How much does each financial feature group contribute to recovering the peers selected by the full embedding? Adapt the [PriorLabs remove-and-recontextualize approach](https://github.com/PriorLabs/tabpfn-extensions/blob/main/src/tabpfn_extensions/interpretability/README.md) using a custom shapiq game for peer overlap. The submission can proceed independently.

## Acceptance

- [ ] Prespecify four disjoint feature groups and record the remaining fields as a fixed baseline. Pin the selected checkpoint, formation roster, feature blocks, context and neighbour rule.
- [ ] Evaluate all 16 coalitions by retaining the same groups in support and query, re-encoding and measuring the mean fraction of each issuer’s full-graph neighbours recovered. Verify full-coalition overlap equals one.
- [ ] Compute exact group Shapley values and check that they sum to the full-minus-baseline overlap. Compare the results with single-group omissions and examine joint removal where groups appear redundant.
- [ ] Save the group definitions, coalition scores and attribution table in a separate evidence record. Document whether joint attribution adds a descriptive finding worth including in the appendix.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

_No open children._

`0 open; 0 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
