"""Publication selectors must reject incomplete or inconsistent study outputs."""

import runpy
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
RENDER = runpy.run_path(str(ROOT / "src/latex/render_results.py"))
type Row = dict[str, Any]
type Cohorts = dict[str, dict[str, Row]]


def test_a_model_subset_cannot_be_rendered_as_the_study() -> None:
    rows = [
        {"approach": "histories__tabpfn_full__late", "kernel": "matched", "innovation": "diagonal"}
    ]
    with pytest.raises(ValueError, match="Incomplete publication procedures"):
        RENDER["validate_inventory"](rows, [], [])


def test_duplicate_procedures_are_rejected_before_rendering() -> None:
    row = {"approach": "histories__direct", "kernel": "matched", "innovation": "diagonal"}
    with pytest.raises(ValueError, match="Duplicate comparison procedure"):
        RENDER["validate_inventory"]([row, row], [], [])


def test_missing_or_ambiguous_source_rows_are_rejected() -> None:
    with pytest.raises(ValueError, match="found 0"):
        RENDER["select"]([], representation="direct")
    with pytest.raises(ValueError, match="found 2"):
        RENDER["select"]([{"year": "2020"}] * 2, year=2020)


def test_nonfinite_or_unreconciled_scores_are_rejected() -> None:
    for actual in (float("nan"), float("inf"), 2.0):
        with pytest.raises(ValueError, match="saved score"):
            RENDER["close"](actual, 1.0, "saved score")


def geometry_records() -> tuple[list[Row], list[Row], list[Row], list[Row]]:
    """A complete small-cohort grid with independently reconcilable spectra."""
    comparison: list[Row] = []
    annual: list[Row] = []
    summary: list[Row] = []
    spectrum: list[Row] = []
    for approach in RENDER["GEOMETRY_APPROACHES"]:
        for model in ("gram", "spatial"):
            for variance in ("full", "correlation"):
                column = f"{approach}|{model}|{variance}"
                comparison.append(
                    {
                        "column": column,
                        "approach": approach,
                        "model": model,
                        "variance": variance,
                        "theta": "0.5",
                        "lambda": "0.2",
                        "firm_days": "60",
                        "heldout_log_likelihood": "6",
                        "score_per_firm_day": "0.1",
                    }
                )
                annual.extend(
                    {"column": column, "year": str(year), "score": "1"}
                    for year in range(2020, 2026)
                )
        for year in range(2016, 2026):
            summary.append(
                {
                    "approach": approach,
                    "year": str(year),
                    "firms": "7",
                    "requested_rank": "5",
                    "rank": "5",
                    "positive_rank": "5",
                    "rank_shortfall": "False",
                    "tolerance": "1e-10",
                    "variance_share": "1",
                    "raw_reconstruction_share": "0.4",
                    "residual_reconstruction_share": "0.3",
                    "random_relative_expectation": str(5 / 6),
                    "cutoff_applicable": "False",
                    "cutoff_gap": "",
                    "cutoff_relative_gap": "",
                    "cutoff_tied": "False",
                    "cutoff_near_tied": "False",
                    "subspace_unique": "True",
                    "max_gross_weight": "2",
                }
            )
            for prefix, projected in (("raw", 40), ("residual", 30)):
                summary[-1].update(
                    {
                        f"{prefix}_total_energy": "100",
                        f"{prefix}_relative_energy": "50",
                        f"{prefix}_projected_energy": str(projected),
                        f"{prefix}_energy_defined": "True",
                        f"{prefix}_relative_defined": "True",
                        f"{prefix}_relative_reconstruction_share": str(projected / 50),
                        f"{prefix}_relative_energy_share": "0.5",
                        f"{prefix}_random_relative_mean": "0.8",
                        f"{prefix}_random_relative_lower": "0.7",
                        f"{prefix}_random_relative_upper": "0.9",
                    }
                )
            spectrum.extend(
                {
                    "approach": approach,
                    "year": str(year),
                    "component": str(component),
                    "eigenvalue": "1" if component <= 5 else "0",
                    "variance_share": "0.2" if component <= 5 else "0",
                }
                for component in range(1, 8)
            )
    return comparison, annual, summary, spectrum


def test_geometry_requires_complete_matched_models_and_evaluation_years() -> None:
    records = geometry_records()
    RENDER["validate_geometry_inventory"](*records)
    with pytest.raises(ValueError, match="geometry comparison inventory"):
        RENDER["validate_geometry_inventory"](records[0][:-1], *records[1:])
    with pytest.raises(ValueError, match="geometry evaluation years"):
        RENDER["validate_geometry_inventory"](records[0], records[1][:-1], *records[2:])


def test_geometry_rejects_inconsistent_score_normalization() -> None:
    records = geometry_records()
    records[0][0]["score_per_firm_day"] = "1"
    with pytest.raises(ValueError, match="geometry normalized score"):
        RENDER["validate_geometry_inventory"](*records)


def test_pcoa_rejects_missing_or_materially_negative_eigenvalues() -> None:
    records = geometry_records()
    with pytest.raises(ValueError, match="PCoA spectrum inventory"):
        RENDER["validate_geometry_inventory"](*records[:3], records[3][:-1])
    records[3][0]["eigenvalue"] = "-0.1"
    with pytest.raises(ValueError, match="Materially negative PCoA eigenvalue"):
        RENDER["validate_geometry_inventory"](*records)


def test_pcoa_rank_and_variance_claims_must_match_recorded_spectrum() -> None:
    records = geometry_records()
    records[2][0]["positive_rank"] = "4"
    with pytest.raises(ValueError, match="positive PCoA rank"):
        RENDER["validate_geometry_inventory"](*records)
    records[2][0]["positive_rank"] = "5"
    records[2][0]["variance_share"] = "0.9"
    with pytest.raises(ValueError, match="PCoA retained variance"):
        RENDER["validate_geometry_inventory"](*records)


def test_energy_diagnostics_reconcile_each_annual_projection_and_random_reference() -> None:
    row = geometry_records()[2][0]
    RENDER["validate_pcoa_energy"](row)
    row["raw_relative_reconstruction_share"] = "0.9"
    with pytest.raises(ValueError, match="PCoA energy identity"):
        RENDER["validate_pcoa_energy"](row)
    row["raw_relative_reconstruction_share"] = "0.8"
    row["random_relative_expectation"] = "0.5"
    with pytest.raises(ValueError, match="random subspace expectation"):
        RENDER["validate_pcoa_energy"](row)


@pytest.mark.parametrize("total", [0, 100])
def test_undefined_relative_return_energy_is_missing_instead_of_zero(total: int) -> None:
    row = geometry_records()[2][0]
    row.update(
        {
            "raw_total_energy": str(total),
            "raw_relative_energy": "0",
            "raw_projected_energy": "0",
            "raw_energy_defined": str(total > 0),
            "raw_relative_defined": "False",
            "raw_reconstruction_share": "0" if total else "",
            "raw_relative_energy_share": "0" if total else "",
            "raw_relative_reconstruction_share": "",
            **{f"raw_random_relative_{field}": "" for field in ("mean", "lower", "upper")},
        }
    )
    RENDER["validate_pcoa_energy"](row)
    row["raw_relative_reconstruction_share"] = "0"
    with pytest.raises(ValueError, match="Undefined PCoA energy ratio"):
        RENDER["validate_pcoa_energy"](row)


def test_rank_five_numerical_cutoff_ties_are_retained_and_marked_nonunique() -> None:
    _, _, summaries, _ = geometry_records()
    row = summaries[0]
    row.update(
        {
            "positive_rank": "6",
            "cutoff_applicable": "True",
            "cutoff_gap": "0",
            "cutoff_relative_gap": "0",
            "cutoff_tied": "True",
            "cutoff_near_tied": "True",
            "subspace_unique": "False",
        }
    )
    eigenvalues = [{"eigenvalue": "1"}] * 6 + [{"eigenvalue": "0"}]
    RENDER["validate_pcoa_cutoff"](row, eigenvalues)
    assert row["rank"] == "5"
    row["subspace_unique"] = "True"
    with pytest.raises(ValueError, match="marked nonunique"):
        RENDER["validate_pcoa_cutoff"](row, eigenvalues)


def test_near_cutoff_diagnostics_are_distinct_from_numerical_ties() -> None:
    row = geometry_records()[2][0]
    row.update(
        {
            "positive_rank": "6",
            "cutoff_applicable": "True",
            "cutoff_gap": str(1 - 0.9995),
            "cutoff_relative_gap": str(1 - 0.9995),
            "cutoff_tied": "False",
            "cutoff_near_tied": "True",
            "subspace_unique": "True",
        }
    )
    eigenvalues = [{"eigenvalue": "1"}] * 5 + [{"eigenvalue": "0.9995"}]
    RENDER["validate_pcoa_cutoff"](row, eigenvalues)
    row["cutoff_tied"] = "True"
    with pytest.raises(ValueError, match="cutoff tie diagnostic"):
        RENDER["validate_pcoa_cutoff"](row, eigenvalues)


def sensitivity_records() -> tuple[list[Row], Cohorts]:
    """Both timing windows and MM packages on natural and matched cohorts."""
    rows: list[Row] = []
    cohorts: Cohorts = {}
    for timing, start in (("shifted", 2016), ("contemporaneous", 2015)):
        cohorts[timing] = {}
        for table in ("common_four", "common_three"):
            for sample in ("natural", "intersection"):
                cohorts[timing][f"{table}|{sample}"] = {"firms": 4, "tickers": list("ABCD")}
                networks = list(RENDER["CHARACTERISTICS"])
                if table == "common_four":
                    networks.append("fernandez_debt_maturity")
                procedures = [("nonspatial", "ols")] + [
                    (network, estimator)
                    for network in networks
                    for estimator in ("spatial_lag_iv", "spatial_error_ml")
                ]
                for backend in ("robustbase", "robust"):
                    for network, estimator in procedures:
                        rows.append(
                            {
                                "timing": timing,
                                "backend": backend,
                                "table": table,
                                "sample": sample,
                                "sample_id": f"{table}:intersection"
                                if sample == "intersection"
                                else f"{table}:{timing}:natural",
                                "network": network,
                                "estimator": estimator,
                                "firms": "4",
                                "self_links": "False",
                                "return_start": f"{start}-01-01",
                                "return_end": f"{start + 9}-12-31",
                                "characteristic_start": "2015",
                                "characteristic_end": "2024",
                                **dict.fromkeys(
                                    (
                                        "premium_market",
                                        "se_market",
                                        "intensity",
                                        "intensity_se",
                                        "pseudo_r2_structural",
                                        "pseudo_r2_reduced",
                                    ),
                                    "0.1",
                                ),
                            }
                        )
    return rows, cohorts


def test_sensitivity_requires_both_packages_and_unchanged_intersection_firms() -> None:
    rows, cohorts = sensitivity_records()
    RENDER["validate_replication_sensitivity"](rows, cohorts)
    with pytest.raises(ValueError, match="replication sensitivity inventory"):
        RENDER["validate_replication_sensitivity"](rows[:-1], cohorts)
    cohorts["contemporaneous"]["common_four|intersection"]["tickers"] = list("ABCE")
    with pytest.raises(ValueError, match="timing comparison changes firms"):
        RENDER["validate_replication_sensitivity"](rows, cohorts)


def test_sensitivity_dates_must_include_the_complete_calendar_window() -> None:
    rows, cohorts = sensitivity_records()
    rows[0]["return_end"] = "2025-01-01"
    with pytest.raises(ValueError, match="sensitivity windows"):
        RENDER["validate_replication_sensitivity"](rows, cohorts)


def test_publication_replaces_restored_hardlinks_without_changing_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = tmp_path / "cache.tex"
    cache.write_text("recorded source")
    cache.chmod(0o444)
    target = tmp_path / "table.tex"
    target.hardlink_to(cache)
    monkeypatch.setitem(RENDER["write"].__globals__, "OUT", tmp_path)
    RENDER["write"]("table.tex", ["new table"])
    assert target.read_text() == "new table\n"
    assert cache.read_text() == "recorded source"
    assert cache.stat().st_ino != target.stat().st_ino
