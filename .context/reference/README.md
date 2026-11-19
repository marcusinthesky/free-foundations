---
title: References
description: Bibliographic metadata and compact source context, one directory per citation key.
---

# References

```bash
just reference-new shannon1948 "A Mathematical Theory of Communication"
just sync
```

Each `KEY/README.md` owns flat CSL (Citation Style Language) metadata such as
`type`, `title`, `author`, `issued`, `DOI` and `URL`, plus a local `description`
and optional `links`. Its directory name is the citation key; never author an
`id` or nested `csl` object. Edit the new record's metadata and body to explain
what the source establishes. Supporting files may live beside it.

Schema validity does not independently verify publication metadata. Keep the
source or verification details with the record, and use `just check` to check
structure, declared links and generated-view freshness.

`just sync` also derives `src/latex/refs.bib` through Pandoc. Cite the directory
key with `\citep{shannon1948}` in the manuscript. Edit records rather than the
export; `just check` rejects stale bibliography output.

<!-- insitu:begin sql
id = "reference-records"
model = "records"
template = "records.md.j2"
-->

| Record | Description |
| --- | --- |
| [A closer look at TabPFN v2: understanding its strengths and extending its capabilities](ye2025/README.md) | TabPFN representations. |
| [A generalized spatial two-stage least squares procedure for estimating a spatial autoregressive model with autoregressive disturbances](kelejian1998/README.md) | Spatial IV estimation. |
| [A model of inductive bias learning](baxter2000/README.md) | Inductive bias transfer. |
| [A simple sequentially rejective multiple test procedure](holm1979/README.md) | Familywise adjustment. |
| [Accurate predictions on small data with a tabular foundation model](hollmann2025/README.md) | TabPFN encoder. |
| [Asset embeddings](gabaix2025asset/README.md) | Learned asset representations. |
| [Asset pricing with spatial interaction](kou2018/README.md) | Spatial asset pricing panel. |
| [Autoencoder asset pricing models](gu2021/README.md) | Autoencoder asset pricing. |
| [Automatic block-length selection for the dependent bootstrap](politis2004/README.md) | Block-length selection. |
| [Beyond IID: how general are tabular foundation models, really?](purucker2026/README.md) | Tabular models under shift. |
| [Characteristics are covariances: a unified model of risk and return](kelly2019/README.md) | Characteristics as covariances. |
| [Common risk factors in the returns on stocks and bonds](fama1993/README.md) | CRSP market equity convention. |
| [Correction to "Automatic block-length selection for the dependent bootstrap" by D. Politis and H. White](patton2009/README.md) | Block-length correction. |
| [EDGAR application programming interfaces](sec-edgar-api/README.md) | SEC data interfaces. |
| [High breakdown-point and high efficiency robust estimates for regression](yohai1987/README.md) | MM regression. |
| [Introduction to spatial econometrics](lesage2009/README.md) | Spatial model interpretation. |
| [Is cosine-similarity of embeddings really about similarity?](steck2024/README.md) | Limits of cosine similarity. |
| [Kumo-Tabular: a foundation model for tabular prediction](nvidia2026kumo/README.md) | Kumo-Tabular encoder. |
| [Likelihood ratio tests for model selection and non-nested hypotheses](vuong1989/README.md) | Non-nested likelihood comparison. |
| [LimiX-2: a contextual mechanism network towards general structured-data intelligence](zhang2026limix/README.md) | LimiX-2 encoder. |
| [Making and evaluating point forecasts](gneiting2011/README.md) | Proper scoring conventions. |
| [MathEconLib: machine-checked mathematical economics in Lean 4](matheconlib2026/README.md) | Lean finite-probability conventions. |
| [Predicting what you already know helps: provable self-supervised learning](lee2021/README.md) | Self-supervised transfer. |
| [Simple diagnostic tests for spatial dependence](anselin1996/README.md) | LM spatial diagnostics. |
| [Spatial GARCH models for unknown spatial locations: an application to financial stock returns](fulle2024spatial/README.md) | Spatial dependence in returns. |
| [Spatial econometrics: methods and models](anselin1988/README.md) | Spatial likelihood estimation. |
| [Spatial linkages in international financial markets](fernandez2007/README.md) | Working paper with estimation details. |
| [Spatial linkages in international financial markets](fernandez2011/README.md) | Replicated spatial CAPM benchmark. |
| [Statistical foundations of prior-data fitted networks](nagler2023/README.md) | Theory of prior-data fitted networks. |
| [TabFM: a zero-shot foundation model for tabular data](kong2026tabfm/README.md) | TabFM encoder. |
| [The benefit of multitask representation learning](maurer2016/README.md) | Multitask representation bounds. |
| [The detection of disease clustering and a generalized regression approach](mantel1967/README.md) | Distance-matrix association. |
| [The fundamental structure of risk: from characteristics to covariance](alouadi2026/README.md) | Characteristic covariance structure. |
| [The stationary bootstrap](politis1994/README.md) | Stationary bootstrap. |
| [Transformers can do Bayesian inference](muller2022/README.md) | Prior-data fitted networks. |
| [Understanding the surprising generalization properties of tabular foundation models](shaheen2026/README.md) | Tabular model generalization. |
| [robust: Port of the S+ Robust Library](wang2024robust/README.md) | Alternative MM backend. |
| [robustbase: Basic Robust Statistics](maechler2024robustbase/README.md) | Primary MM implementation. |
| [statadic: composable statistics on JAX](statadic2026/README.md) | Statistical estimation library. |

<!-- insitu:end -->
