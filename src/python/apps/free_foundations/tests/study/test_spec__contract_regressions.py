"""Scientific-contract, factor-definition and saved-result publication regressions."""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.study import factors, features
from free_foundations.study.factors import acquire_factors, parse_monthly, quarterly_factors
from free_foundations.study.publication import render
from free_foundations.study.spec import StudySpec, frame_digest, panel_contract

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _zip_csv(text: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("research.csv", text)
    return buffer.getvalue()


def _source(columns: tuple[str, ...]) -> bytes:
    rows = ["Public research data", "," + ",".join(columns)]
    rows.extend(f"2001{month:02d}," + ",".join(["1.00"] * len(columns)) for month in range(1, 13))
    rows.extend(
        ["", "Annual Factors: January-December", "2001," + ",".join(["999"] * len(columns))]
    )
    return _zip_csv("\n".join(rows))


def test_monthly_parser_excludes_annual_rows_and_retains_missing_sentinels() -> None:
    parsed = parse_monthly(_source(("Mkt-RF", "RF")))
    assert len(parsed) == 12
    assert parsed["month"].dt.year.eq(2001).all()
    np.testing.assert_allclose(parsed[["Mkt-RF", "RF"]], 0.01)
    missing = parse_monthly(_zip_csv("preamble\n, Mom\n200101,-99.99\n200102,-999\n"))
    assert missing["Mom"].isna().all()
    with pytest.raises(ValueError, match="monthly YYYYMM"):
        parse_monthly(_zip_csv("Annual Factors\n2001,5\n"))


def test_quarterly_market_and_rf_are_compounded_separately() -> None:
    monthly = pd.DataFrame(
        {
            "month": pd.date_range("2001-01-01", periods=3, freq="MS"),
            "Mkt-RF": [0.1, -0.02, 0.04],
            "RF": [0.01, 0.02, 0.03],
            "Mom": [0.02, 0.03, -0.01],
        }
    )
    result = quarterly_factors(monthly).iloc[0]
    expected_rf = np.prod(1 + monthly["RF"]) - 1
    expected_market = np.prod(1 + monthly["Mkt-RF"] + monthly["RF"]) - 1 - expected_rf
    assert result["RF"] == pytest.approx(expected_rf)
    assert result["Mkt-RF"] == pytest.approx(expected_market)
    assert result["Mom"] == pytest.approx(np.prod(1 + monthly["Mom"]) - 1)
    assert result["quarter"] == pd.Timestamp("2001-03-31")


def test_missing_or_duplicate_factor_month_is_not_a_complete_quarter() -> None:
    monthly = pd.DataFrame(
        {
            "month": pd.to_datetime(["2001-01-01", "2001-03-01"]),
            "RF": [0.01, 0.01],
            "Mkt-RF": [0.1, 0.2],
        }
    )
    result = quarterly_factors(monthly)
    assert result[["RF", "Mkt-RF"]].isna().all().all()
    duplicate = pd.DataFrame(
        {
            "month": pd.to_datetime(["2001-01-01", "2001-03-01", "2001-01-31"]),
            "RF": [0.01, 0.01, 0.01],
            "Mkt-RF": [0.1, 0.2, 0.1],
        }
    )
    with pytest.raises(ValueError, match="Duplicate monthly"):
        quarterly_factors(duplicate)


def test_factor_acquisition_reuses_frozen_bytes_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        message = "Cached factor acquisition must not call the network"
        raise AssertionError(message)

    monkeypatch.setattr(factors.httpx, "get", forbidden)
    spec = replace(StudySpec(), archive_end="2001-12-31", feature_start="2001-01-01")
    assert not acquire_factors(tmp_path, spec, offline=True)
    (tmp_path / factors.FILES["ff5"]).write_bytes(
        _source(("Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"))
    )
    (tmp_path / factors.FILES["momentum"]).write_bytes(_source(("Mom",)))
    before = {path.name: path.read_bytes() for path in tmp_path.glob("*.zip")}
    assert acquire_factors(tmp_path, spec, offline=True)
    assert len(pd.read_parquet(tmp_path / "monthly.parquet")) == 12
    assert len(pd.read_parquet(tmp_path / "quarterly.parquet")) == 4
    assert before == {path.name: path.read_bytes() for path in tmp_path.glob("*.zip")}
    status = json.loads((tmp_path / "status.json").read_text())
    assert status["status"] == "complete"
    assert status["missing_months"] == []


def test_contract_binds_observed_masks_and_configuration_version(tmp_path: Path) -> None:
    spec = StudySpec()
    path = tmp_path / "study.json"
    path.write_text(json.dumps(spec.payload()))
    assert StudySpec.read(path) == spec
    path.write_text(json.dumps(spec.payload() | {"version": "unknown-version"}))
    with pytest.raises(ValueError, match="supported explicit version"):
        StudySpec.read(path)
    panel = pd.DataFrame(
        {
            "issuer_id": ["A", "B"],
            "quarter": pd.to_datetime(["2010-03-31"] * 2),
            "total_return": [0.1, np.nan],
            "observed": [True, False],
        }
    )
    before = panel_contract(panel, spec)
    after = panel.copy()
    after.loc[1, ["observed", "total_return"]] = [True, -0.2]
    changed = panel_contract(after, spec)
    assert changed["roster_sha256"] == before["roster_sha256"]
    assert changed["mask_sha256"] != before["mask_sha256"]
    after.loc[1, "observed"] = False
    with pytest.raises(ValueError, match="flags disagree"):
        panel_contract(after, spec)


@pytest.mark.parametrize(
    "build",
    [
        lambda: StudySpec(frequency="monthly"),
        lambda: StudySpec(return_lookback_quarters=0),
        lambda: StudySpec(bootstrap_blocks=(0,)),
        lambda: StudySpec(bootstrap_draws=-1),
        lambda: StudySpec(rungs=("fernandez", "standard_xbrl", "full_xbrl", "full_xbrl")),
    ],
)
def test_invalid_scientific_contract_is_rejected(build: Callable[[], StudySpec]) -> None:
    with pytest.raises(ValueError, match=r"quarterly|lookbacks|Bootstrap|unique"):
        build()


def _publication_inputs(root: Path) -> tuple[StudySpec, pd.DataFrame]:
    prepared = root / "prepared"
    prepared.mkdir(parents=True)
    spec = replace(StudySpec(), archive_end="2010-03-31", feature_start="2010-01-01")
    population = pd.DataFrame(
        {
            "issuer_id": ["A", "B"],
            "quarter": pd.to_datetime(["2010-03-31"] * 2),
            "total_return": [0.1, np.nan],
            "observed": [True, False],
            "xbrl_available": [True, False],
            "xbrl_status": ["available", "unresolved_identity"],
        }
    )
    panel = population.iloc[:1].copy()
    panel.to_parquet(prepared / "panel.parquet", index=False)
    population.to_parquet(prepared / "population.parquet", index=False)
    pd.DataFrame(
        {"characteristic": ["market_to_book"], "status": ["unverifiable_public_price"]}
    ).to_parquet(prepared / "characteristics.parquet", index=False)
    manifest = {
        "master": panel_contract(panel, spec),
        "population_sha256": frame_digest(population),
        "availability": {"available": 1, "unresolved_identity": 1},
    }
    (prepared / "manifest.json").write_text(json.dumps(manifest))
    return spec, panel


def test_publication_reads_saved_parquets_and_keeps_missing_stages_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec, panel = _publication_inputs(tmp_path)
    destination = tmp_path / "measurement"
    destination.mkdir()
    score = pd.DataFrame(
        {
            "quarter": [pd.Timestamp("2010-03-31")],
            "method": ["baseline"],
            "status": ["available"],
            "score_per_issuer": [-123.456],
        }
    )
    score.to_parquet(destination / "scores.parquet", index=False)
    (destination / "manifest.json").write_text(
        json.dumps(
            {
                "master": panel_contract(panel, spec),
                "status": "available",
                "files": {"scores": "scores.parquet"},
            }
        )
    )
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = json.loads((tmp_path / "publication/claims-audit.json").read_text())
    assert audit["status"] == "results_pending"
    assert not audit["claims"]["new_empirical_findings_available"]
    saved = pd.read_csv(tmp_path / "publication/measurement-score-summary.csv")
    assert saved.loc[0, "mean_score_per_issuer"] == -123.456
    text = (tmp_path / "src/latex/build/crsp-study.tex").read_text()
    assert "-123.456" in text
    assert "results\\_pending" in text


def test_publication_rejects_changed_master_or_stage_mask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec, panel = _publication_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)
    wrong = panel_contract(panel, spec) | {"mask_sha256": "wrong"}
    stage = tmp_path / "replication"
    stage.mkdir()
    (stage / "manifest.json").write_text(json.dumps({"master": wrong, "status": "complete"}))
    with pytest.raises(ValueError, match="different roster"):
        render(tmp_path, spec)
    (stage / "manifest.json").unlink()
    changed = panel.assign(total_return=0.9)
    changed.to_parquet(tmp_path / "prepared/panel.parquet", index=False)
    with pytest.raises(ValueError, match="panel bytes/roster/mask"):
        render(tmp_path, spec)


def test_streamed_features_match_small_tables_and_load_only_requested_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "sec"
    (source / "companyfacts").mkdir(parents=True)
    facts = {
        "us-gaap": {
            "Assets": {
                "units": {
                    "USD": [
                        {
                            "val": 100,
                            "end": "2023-12-31",
                            "filed": "2024-02-01",
                            "accn": "a",
                            "form": "10-K",
                        }
                    ]
                }
            }
        },
        "custom": {
            "Missing": {
                "units": {
                    "USD": [
                        {
                            "val": None,
                            "end": "2023-12-31",
                            "filed": "2024-02-01",
                            "accn": "a",
                            "form": "10-K",
                        }
                    ]
                }
            }
        },
    }
    links = []
    for cik, permco in ((42, 2), (43, 3)):
        (source / f"companyfacts/{cik:010}.json").write_text(
            json.dumps({"cik": cik, "facts": facts})
        )
        links.append(
            {
                "permco": permco,
                "cik": cik,
                "status": "verified_interval",
                "effective_from": "2009-01-01",
                "effective_to": "2025-12-31",
                "evidence_url": "https://www.sec.gov/Archives/a",
                "accession": "a",
            }
        )
    pd.DataFrame(links).to_csv(source / "crosswalk.csv", index=False)
    quarterly = pd.DataFrame(
        [
            {"issuer_id": f"PERMCO:{permco}", "permco": permco, "quarter": pd.Timestamp(quarter)}
            for permco in (2, 3)
            for quarter in ("2024-06-30", "2024-09-30")
        ]
    )
    monthly = pd.DataFrame({"date": pd.to_datetime(["2024-03-28", "2024-06-28"])})
    original = features.load_source_facts
    requested_ciks: list[set[int] | None] = []

    def limited(path: Path, ciks: set[int] | None = None) -> pd.DataFrame:
        requested_ciks.append(ciks)
        assert ciks is not None
        assert len(ciks) == 1
        return original(path, ciks)

    monkeypatch.setattr(features, "load_source_facts", limited)
    memory = features.build_features(quarterly, monthly, source, StudySpec())
    destination = tmp_path / "prepared"
    streamed = features.build_features(
        quarterly, monthly, source, StudySpec(), destination=destination
    )
    for name in ("availability", "characteristics", "crosswalk"):
        pd.testing.assert_frame_equal(streamed[name], memory[name])
    assert streamed["broad"].empty
    assert streamed["facts"].empty
    assert len(requested_ciks) == 4
    schema = pd.read_parquet(destination / "schema.parquet")
    assert set(schema.columns) == {
        "feature_id",
        "quarter",
        "is_standard",
        "entity_wide",
        "dimensions",
        "value_type",
    }
    assert schema["feature_id"].str.contains("custom:Missing", regex=False).any()
    keys = pd.MultiIndex.from_tuples(
        [("PERMCO:2", pd.Timestamp("2024-06-30"))], names=["issuer_id", "quarter"]
    )
    selected = features.read_feature_rows(destination / "broad", keys)
    assert len(selected) == 2
    assert selected["issuer_id"].eq("PERMCO:2").all()
    assert selected["quarter"].eq(pd.Timestamp("2024-06-30")).all()
    assert selected.loc[selected["concept"].eq("custom:Missing"), "value"].isna().all()
    standard = features.read_feature_rows(destination / "broad", keys, standard_only=True)
    assert len(standard) == 1
    assert standard.iloc[0]["concept"] == "us-gaap:Assets"


def test_empty_streamed_feature_dataset_retains_filterable_schema(tmp_path: Path) -> None:
    quarterly = pd.DataFrame(
        {"issuer_id": ["PERMCO:2"], "permco": [2], "quarter": [pd.Timestamp("2024-06-30")]}
    )
    monthly = pd.DataFrame({"date": pd.to_datetime(["2024-03-28"])})
    destination = tmp_path / "prepared"
    features.build_features(
        quarterly, monthly, tmp_path / "sources", StudySpec(), destination=destination
    )
    keys = pd.MultiIndex.from_frame(quarterly[["issuer_id", "quarter"]])
    assert features.read_feature_rows(destination / "broad", keys, standard_only=True).empty
