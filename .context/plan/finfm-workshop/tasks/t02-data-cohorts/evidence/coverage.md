---
description: Bounded audit of the frozen 2015 formation cohort and saved quarterly outcomes.
---

# 2015 formation coverage receipt

**Decision.** The existing saved quarterly outcomes support a clearly labelled
US reimplementation on observed quarters, conditional on the stated roster,
SEC availability, minimum-history and estimation requirements. They do **not**
certify a complete exit-adjusted cohort: absent rows have unknown causes, the
extract has no terminal-event flag, and an incomplete quarter remains missing.
The resulting selection can affect estimates. Do not claim a top-1,000 issuer
sample, complete terminal-return coverage, or an exact replication of the
original market and accounting sources. The count meeting the minimum return
history is not a count of successfully fitted MM betas or spatial estimates.

## Provenance and reconciliation

At code base `793ae46`, the bounded audit reads the frozen CRSP CSV and prepared
parquet files without modifying them. It verifies the CSV against the frozen
source and prepared manifests, checks the bytes of membership, cohorts, panel,
population, characteristics and factors against the prepared manifest, rebuilds
the December membership, and checks the full stored cohort frame digest. It
constructs only the 2015 fixed-formation monthly ledger, compounds it to
quarters with the production functions, and compares all columns, row order,
values and missingness using `frame_digest`. All **39,600** reconstructed
quarter rows match the stored 2015 rows. This verifies the accounting path,
not the economic completeness of the raw extract.

| Identity | SHA-256 |
| --- | --- |
| Frozen `data/raw/crsp-sec/crsp.csv` | `bb58e9f3ba63f9b713dd4015f851125a6db9d495bdd134e1395261fda44fa25c` |
| Prepared `panel/manifest.json` bytes | `a56bd4ea963bcfd6556b75da3f769fffd875c1ce7593e776e21b1b642be594ff` |
| Stored all-formations cohort frame | `089378a120db9ef58455acb4b2de816dda10b8f78cbec7dd2135f6bb1f3aee6f` |
| Private monthly ledger file | `6305c29bbfdad7abd17ff0662228766e1ad3f1b206ec4ae6cdc162000a3acc92` |
| Private monthly ledger frame | `43823c30762cf95d16c7ea22e575f46c3930ae8e8e189bef6bed69ed0eb051f6` |

The private, ephemeral receipt is `/tmp/finfm-cohort-793ae46/manifest.json`,
with `cohort_monthly.parquet` and the audit script beside it. The ledger is
bound to both the source bytes and the existing prepared manifest; it is not
a DVC output, a new prepared contract, or a representation input. Audit command
uses the locked `src/python` uv project with the pinned devenv libraries:
`uv run --project src/python --offline --frozen --package free-foundations python /tmp/finfm-cohort-793ae46/audit.py`.
No pipeline reproduction or source acquisition was performed.

## Ledger contract and example

The private ledger key is (`formation_year`, `issuer_id`, `month`); month is
calendar month-end, `issuer_id` is formation `PERMCO:<id>`, and returns are
decimal. It contains `permco`, `total_return`, `observed`, `status`,
`constituents` (ordered selected PERMNOs as JSON), `constituent_weights` (JSON
of PERMNO and prior-calendar-month cap weight), `market_cap_usd`,
`source_count`, `selected_count`, `issuer_identity_changed`,
`missing_source_count`, `missing_return_count`, `invalid_return_count`, and
`missing_lagged_cap_count`. The separate membership table gives formation
security rank and formation capitalization; compare later December memberships
for top-1,000 rank-outs, not exact ranks below the cutoff. Missing weights are
null and missing outcomes stay null. Formation PERMCO remains the issuer key
if a source PERMCO changes; the identity flag records that event.

For example, formation 2015, `PERMCO:10107`, January 2016 has constituent
`[75694]`, weight `1.0`, observed total return `-0.081222`, and current selected
class market cap USD `3,075,323,790`. Quarterly return is the product of the
three gross monthly issuer returns minus one only if all three are observed.
The export's CIZ `mthret` is already a total return, including any delisting
component, and is applied once; the export cannot tell us which returns contain
such a component. A return of -100% is valid but does not establish a terminal
event or authorize filling later missing months.

## Fernández-to-US coverage bridge

| Item | Benchmark / US implementation and denominator |
| --- | --- |
| Selection | Fernández is the characteristic-history spatial CAPM benchmark. This US implementation ranks **securities** by December CRSP capitalization, ties by PERMNO, then groups selected classes by formation PERMCO. December 2015 gives **1,000 securities, 990 issuers**, including 10 issuers with two selected classes. The frozen export includes securities ever in a December top 1,000 and their eligible histories, not a comprehensive all-security panel. |
| Formation accounting | Of 990 issuer rows in 2016 Q1, **967** have linked, available as-of CompanyFacts and enter the analytical formation roster; **22** have unresolved linkage and **1** has no available native facts. Of all 990, the four original characteristics available at formation number 0 / 1 / 2 / 3 / 4 for **29 / 7 / 130 / 340 / 484** issuers. Availability of any native facts does not imply complete original ratios. |
| Fixed cohort | January 2016–December 2025 comprises **118,800 issuer-months**: 97,903 observed, 20,895 missing source, 2 missing lagged cap. The 40-quarter grid comprises **39,600 issuer-quarters**: 32,547 observed, 7,051 missing source and 2 missing lagged cap. Missing quarters contain 0 / 1 / 2 observed months in **6,874 / 96 / 83** cases. |
| Analytical outcomes | The 967 formation-eligible issuers yield 38,680 possible issuer-quarters, of which **32,021** are observed. **878 / 967** have at least eight observed quarters; 89 do not. Across all 990 cohort issuers, 893 meet that history threshold. Convergence and any downstream exclusions require separate reporting. |
| Rank changes | At December 2016, **59** of the original 1,000 securities are still in the extract that month but outside that December's top 1,000; at December 2025, **120** are. They remain in the original cohort. The corresponding counts outside the selected annual roster regardless of current source presence are **117** and **405**. These are snapshots, not unique exit totals. |
| Missing / exits | **284 / 990** issuers have at least one missing-source quarter. Of the original 1,000 securities, **277** have their last 2016–25 source row before December 2025, and **8** have no row in that window. Such absences can reflect eligibility filtering, exit or gaps; none identifies a delisting. No observed selected-security return in the window equals -100%, and the source has no terminal flags. |
| Design and information | Quarterly CRSP CIZ total returns are compounded once; the original-ratio histories and exponential spatial weights reimplement the benchmark with US SEC CompanyFacts, US selection and explicit missingness. CompanyFacts values can be revised rather than filing-date vintages, issuer market equity includes only classes in the extract, and SIC is current. These limits and changes belong beside any results. |

The analytic sample's observed-quarter count does not correct survivor or
missing-exit bias; a partial terminal quarter is withheld even when a terminal
loss might have occurred. Terminal-event evidence and settlement assumptions
would be needed to identify a different outcome. No claim of terminal loss
coverage can be inferred from the sample's observed return values.
