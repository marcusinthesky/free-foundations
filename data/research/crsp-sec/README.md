---
description: The in-sample CRSP–SEC study contract, from population to intervals.
---

# Quarterly CRSP–SEC study

This is the empirical contract for version `crsp-sec-quarterly-v2` in
[`params.yaml`](../../../params.yaml). The study is descriptive and inferential: every
estimate is fitted in sample with its interval; nothing is a forecast or backtest.

## Population and returns

The staged CRSP CIZ monthly extract covers 2001–2025; `mthret` is a decimal total
return including delisting returns, applied once. Each December ranks US common stocks
by capitalization (ties by PERMNO) and the top 1,000 form the next year's roster.
Selected classes are grouped by formation PERMCO into issuer portfolios with lagged
capitalization weights; a missing component return leaves the issuer outcome missing.
Three monthly returns compound into each quarterly outcome. No complete-case sample is
constructed: entry, exit and missing cells stay in the panel.

A formation cohort is one December roster followed for the next 40 quarters,
including exits. The analytical panel keeps issuer-quarters with verified CRSP–SEC
links and as-of CompanyFacts. Unresolved links are reported as coverage, not filled.

## Information and characteristics

Quarter-start information uses facts filed before the preceding CRSP close at 16:00
New York time. Fernández's four characteristics use CRSP issuer market equity (ME)
at the month of the latest as-of balance sheet, summed over the issuer's classes in
the extract, with entity-wide US-GAAP books:

| Characteristic | Definition |
| --- | --- |
| Market cap / assets | ME / `Assets` |
| Market-to-book | ME / positive parent `StockholdersEquity` |
| Dividend yield | annual `PaymentsOfDividendsCommonStock` (else `PaymentsOfDividends`) / ME at that fiscal year end |
| Debt maturity | noncurrent / total reported debt, excluding leases |

Missing tags stay missing. Values outside plausible ranges (filer scale errors) and
balance sheets older than 15 months are unavailable with their own reasons. Every
value records its CRSP and SEC components.

Two information rungs feed the models: `fernandez` (ten annual as-of slots of the four
characteristics) and `standard_xbrl` (the latest as-of value of every entity-wide
standard-taxonomy CompanyFacts concept, by unit and period kind, reported by at least
10% of the view's issuer-quarters; the floor reads disclosure coverage, never returns).
States are encoded each January and networks held for that year's quarters, matching
the annual December roster formation. Four pinned models (TabPFN 3.5, TabFM 1.1, Kumo-Tabular, LimiX-2) and a
direct control (support-median imputation, indicators, standardization) encode both.
The model context label is next-quarter market cap / assets, available strictly
before the query quarter. No readout or decoder is fitted on the representations.

## Networks

Fernández's networks keep her literal `W = rownorm(exp(-d))` on Spearman chord
distances of characteristic histories, reranked on each pair's common years; pairs
without two common years take the neutral distance √2. Comparison networks are
symmetrized, row-normalized k-nearest-neighbour graphs (k = 10; 5 and 20 as
sensitivities) on chord distances of each representation, the direct control,
Fernández's joint distance and size; industry links same SIC-2 (current SIC); a
permutation null relabels the Fernández joint graph. A k-NN graph depends only on
distance order: smooth kernels on concentrated embedding distances are nearly
uniform, which leaves the spatial coefficient unidentified with an intercept.

## Estimation and intervals

- **Fernández cross-sections (replication):** for each formation, MM CAPM betas
  (R `robustbase`) on each issuer's observed quarters (at least eight) and median
  quarterly excess returns. OLS, spatial lag by 2SLS and ML, and spatial error by ML,
  without an intercept (her specification) and with one (identified). Networks use
  formation-date information; window-end histories are a fidelity sensitivity.
  Intervals: statadic Wald intervals and, for the primary 2015 formation, a stationary
  quarter bootstrap (999 draws, Politis–White block length) refitting betas, medians
  and every spatial model. Moran's I and LM tests use OLS with an intercept.
  Her equation 8a/8b portfolio VaR is evaluated at the fitted parameters.
- **Co-movement panels:** quarterly excess returns 2011–2025 with period effects,
  regressor MM beta × Mkt-RF, and that quarter's as-of graph. Missing returns remove
  their issuer from that quarter's graph. Intervals: profile-likelihood curvature and
  a stationary quarter bootstrap; networks are compared by per-quarter log-likelihood
  differences with stationary-bootstrap intervals and Holm adjustment.
- **Alignment:** Spearman Mantel correlations of each distance with the realized
  excess-return correlation distance over the primary window, with node-bootstrap
  intervals, permutation p-values and paired gaps.

Statadic supplies the cross-section fits, covariances and diagnostics. Bootstrap
refits and the panels use an eigenvalue profile likelihood, which must reproduce
statadic on the original sample before any draw is used.

## Limitations

CompanyFacts reports revised values, not filing-date vintages. Pretrained weights
postdate the sample, so representations are retrospective measurements. ME sums only
the classes present in the extract, the extract lacks terminal-return flags, and SIC
is current rather than historical. None of these is certified away by a pipeline run.
