# Expanded public-data universe

1,000 SEC issuers; 997 have Yahoo prices.
Observed prices span 2008-01-02 to 2025-12-31.
FF5, momentum and RF span 2008-01-02 to 2025-12-31.
There are 11,483 annual filing-availability snapshots.

These are acquisition and availability results, not estimates from the spatial models.
The candidates are current US exchange listings ranked by current market capitalization.
One share class is kept per SEC CIK, with USD US-GAAP annual 10-K assets required.
Current-listing selection retains survivorship bias.

## Annual availability

The eligibility column requires positive assets known at the preceding year end and
at least 500 observed daily returns in the prior three-calendar-year window.
Future prices do not select the cohort; missing outcomes need separate handling.
Debt uses the existing strict, period-aligned, lease-inclusive mapping.
Market-cap/assets, dividend yield, full histories, and broader model inputs
still require their own construction and audits before a new spatial comparison.

| Year | Assets | Equity > 0 | Strict debt | Assets + prior returns | With strict debt |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2010 | 19 | 17 | 1 | 18 | 1 |
| 2011 | 292 | 246 | 26 | 289 | 26 |
| 2012 | 553 | 477 | 58 | 546 | 58 |
| 2013 | 683 | 608 | 99 | 660 | 98 |
| 2014 | 701 | 630 | 111 | 670 | 109 |
| 2015 | 726 | 649 | 128 | 693 | 124 |
| 2016 | 748 | 667 | 135 | 719 | 133 |
| 2017 | 770 | 682 | 132 | 739 | 128 |
| 2018 | 791 | 694 | 129 | 766 | 129 |
| 2019 | 814 | 716 | 123 | 788 | 123 |
| 2020 | 838 | 734 | 124 | 807 | 123 |
| 2021 | 861 | 761 | 138 | 833 | 136 |
| 2022 | 887 | 792 | 138 | 859 | 137 |
| 2023 | 919 | 809 | 138 | 888 | 136 |
| 2024 | 934 | 816 | 141 | 925 | 141 |
| 2025 | 945 | 833 | 149 | 937 | 149 |

## Reproduction and artifacts

Run `devenv shell just python-universe` with `EDGAR_IDENTITY` set.
The requested screen contains up to 2,000 candidates.
The configuration is frozen per output directory; change `--output` for another design.
Downloads resume from individual compressed SEC files and cached Yahoo batches.
`universe.csv` lists issuers; `universe-exclusions.json` records exclusions.
`price-coverage.json`, `price-failures.json`, and `coverage.csv` record availability.
The cache preserves SEC facts, Yahoo OHLC/actions, adjusted closes, and French factors.
`availability.parquet` and per-issuer snapshots retain asset filing dates and accessions.
`manifest.json` hashes the acquired files. Large inputs are ignored by Git.

The main study should use annual changing cohorts with identical observations across
approaches within each comparison. Exact Fernandez replication remains a separate
strict cohort. Imputations or alternative debt definitions are extensions.
The working paper design and conditional stability proof are in `src/latex/main.tex`.
