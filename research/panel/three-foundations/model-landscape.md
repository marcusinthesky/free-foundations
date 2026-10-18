# Tabular model landscape and declared selection

Reviewed on 18 October 2026. The financial experiment selects a representative
four-model set before inspecting its new financial scores. Selection covers
different tabular prediction architectures and objectives while keeping the
numerical information set and financial readout common. It does not estimate
an average effect for all foundation models.

| Model | Learning/data interface | Role in this study | Primary source |
|---|---|---|---|
| TabPFN 3.5 | Synthetic-task conditional prediction | Core; regression-head features; three weight controls | [Model card](https://huggingface.co/Prior-Labs/tabpfn_3_5) |
| Google TabFM 1.1 | Synthetic tables, row/column representation and in-context prediction | Core; regression-head and earlier cell features | [Paper](https://arxiv.org/abs/2609.37959) |
| Kumo-Tabular Large | Synthetic structural equations; conditional quantile prediction | Core; regression-head and earlier row features; three weight controls | [Official release](https://huggingface.co/blog/nvidia/kumo-tabular) |
| LimiX-2 | Synthetic mechanisms; context-conditional masked modeling | Core; regression-head features | [Paper](https://arxiv.org/abs/2609.17488) |
| EXAONE-Tabular | Synthetic tasks; cross-axis attention and summaries | Existing supplementary results, kept on their original cohorts | [Model card](https://huggingface.co/LG-AI-Research/EXAONE-Tabular) |
| Nori | Synthetic-task in-context regression | Landscape; public dedicated runtime available, outside declared core | [Model card](https://huggingface.co/Synthefy/Nori) |
| Causilo | Synthetic tables; refined row representations and in-context prediction | Landscape; outside declared core | [Paper](https://arxiv.org/abs/2609.22866) |
| Xiaomi TabLDM | Synthetic structural equations; in-context prediction | Landscape; released inference code available, outside declared core | [Paper](https://arxiv.org/abs/2609.03880) |
| SAP RPT-1 | Real tables and semantic representations | Landscape; semantic input interface differs from numeric matched experiment; gated checkpoint | [Model card](https://huggingface.co/SAP/sap-rpt-1-oss) |
| Stanford RT-J | Pretraining on relational databases; entity prediction | Landscape; multi-table relational interface differs from single-table experiment | [Model card](https://huggingface.co/stanford-star/rt-j) |

Kumo's inclusion also reflects its leading default-model position in the public
TabArena aggregate and regression leaderboards inspected on this date. The
[leaderboard](https://huggingface.co/spaces/TabArena/leaderboard) measures tabular
prediction, which motivates model coverage rather than determining financial
measurement validity. The inspected aggregate CSV reported Kumo Large at Elo
1981 and LimiX-2 at 1972; the regression CSV reported 2369 and 2245 respectively.
These are dated selection context, not financial evidence or claims about
future rankings.

Self-supervised learning constructs prediction targets from the training records;
those records can be observed or synthetically generated. LimiX combines masked
self-supervision with synthetic structural models. In-context adaptation
supplies examples to a frozen predictor. These are distinct design choices.
The common theoretical bridge is a task-relevant statistic, a declared economic
target, and a fitted readout under the financial distribution. Model names do
not by themselves establish causal identification, and TabLDM is a large-data
prediction model rather than a latent diffusion model.

The public model artefacts and runtime revisions are pinned in the checkpoint
manifest and dependency lock. The financial protocol specifies the actual
extraction points, common inputs, initialization procedures, and local execution
checks. All core models use one prediction member under common preprocessing;
benchmark ensembles are not imported into the matched financial comparison.
