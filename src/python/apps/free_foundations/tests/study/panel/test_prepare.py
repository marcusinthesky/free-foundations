"""Frozen-source integration checks for the single quarterly experiment."""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from free_foundations.study.panel import prepare as panel_prepare
from free_foundations.study.panel.store import inputs
from free_foundations.study.sources import acquire as run
from free_foundations.study.spec import StudySpec, panel_contract


def _sec_sources(
    _monthly: pd.DataFrame,
    output: Path,
    _identity: str | None,
    **_kwargs: object,
) -> dict[str, object]:
    root = output / "sec"
    (root / "companyfacts").mkdir(parents=True)
    (root / "companyfacts/0000000042.json").write_text(
        json.dumps(
            {
                "cik": 42,
                "facts": {
                    "us-gaap": {
                        "Assets": {
                            "units": {
                                "USD": [
                                    {
                                        "val": 100,
                                        "end": "2008-12-31",
                                        "filed": "2009-02-01",
                                        "accn": "accession",
                                        "form": "10-K",
                                    }
                                ]
                            }
                        }
                    }
                },
            }
        )
    )
    pd.DataFrame(
        [
            {
                "permno": 1,
                "permco": 2,
                "ticker": "ABC",
                "cik": 42,
                "effective_from": "2008-01-01",
                "effective_to": "2010-12-31",
                "status": "verified_interval",
                "evidence_url": "https://www.sec.gov/Archives/fixture",
                "accession": "accession",
            }
        ]
    ).to_csv(root / "crosswalk.csv", index=False)
    return {}


def _factor_sources(destination: Path, _spec: StudySpec, **_kwargs: object) -> None:
    destination.mkdir(parents=True)
    pd.DataFrame(
        {
            "quarter": pd.date_range("2008-03-31", "2010-12-31", freq="QE"),
            "RF": 0.01,
            "Mkt-RF": 0.02,
            "SMB": 0.01,
            "HML": 0.01,
            "RMW": 0.01,
            "CMA": 0.01,
            "Mom": 0.01,
        }
    ).to_parquet(destination / "quarterly.parquet", index=False)


def _acquire(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    study = StudySpec(
        archive_start="2008-01-01",
        archive_end="2010-12-31",
        panel_start="2009-01-01",
        top_n=1,
        window_quarters=4,
        formation_years=(2008,),
        primary_formation=2008,
        min_beta_quarters=3,
    )
    spec_path = tmp_path / "params.yaml"
    spec_path.write_text(yaml.safe_dump({"study": study.payload()}))
    csv = tmp_path / "staged.csv"
    dates = pd.date_range("2008-01-31", "2010-12-31", freq="ME")
    frame = pd.DataFrame(
        {
            "permno": 1,
            "permco": 2,
            "ticker": "ABC",
            "date": dates,
            "total_return": 0.01,
            "market_cap": 10.0,
        }
    )
    frame.loc[frame["date"].eq("2009-07-31"), "total_return"] = np.nan
    frame.to_csv(csv, index=False)
    script = tmp_path / "never_run.py"
    script.write_text('raise RuntimeError("Do not execute this extraction script")\n')
    monkeypatch.setattr(run, "acquire_sources", _sec_sources)
    monkeypatch.setattr(run, "acquire_factors", _factor_sources)
    monkeypatch.setattr(run, "_recover_links", _no_links)
    staging = tmp_path / "staging"
    run.acquire(
        csv, script, staging=staging, canonical=tmp_path / "raw", params=spec_path, offline=True
    )
    return staging / "sources", spec_path, csv


def _no_links(_monthly: pd.DataFrame, _sources: Path, *, offline: bool) -> None:
    assert offline


def test_frozen_source_to_one_unbalanced_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources, spec_path, csv = _acquire(tmp_path, monkeypatch)
    assert (sources / "crsp.csv").read_bytes() == csv.read_bytes()
    assert "Do not execute" in (sources / "extraction.py.txt").read_text()
    prepared = tmp_path / "panel"
    panel_prepare.prepare(sources, prepared, spec_path)
    study, tables = inputs(prepared, spec_path)
    population = pd.read_parquet(prepared / "population.parquet")
    manifest = json.loads((prepared / "manifest.json").read_text())
    assert len(population) == 8
    assert len(tables["panel"]) == 7
    missing = tables["panel"]["quarter"].eq(pd.Timestamp("2009-09-30"))
    assert not bool(tables["panel"].loc[missing, "observed"].iloc[0])
    assert len(tables["characteristics"]) == 32
    ratio = tables["characteristics"].loc[
        tables["characteristics"]["characteristic"].eq("market_cap_assets")
    ]
    # CRSP equity of 10 thousand USD over SEC assets of 100: available once filed,
    # missing before the filing and after the balance sheet is fifteen months old.
    assert ratio["value"].tolist()[1:6] == [100.0] * 5
    assert ratio["reason"].tolist()[-2:] == ["balance_sheet_older_than_15_months"] * 2
    assert manifest["master"] == panel_contract(tables["panel"], study)
    assert str(tables["panel"]["sic"].dtype) == "string"
    assert manifest["no_complete_case_selection"]
    assert set(tables["panel"]["issuer_id"]) == {"PERMCO:2"}
    cohort = tables["cohorts"]
    assert set(cohort["formation_year"]) == {2008}
    assert cohort["quarter"].min() == pd.Timestamp("2009-03-31")
    assert cohort["quarter"].max() == pd.Timestamp("2009-12-31")


@pytest.mark.parametrize("cache_link", ["hardlink", "symlink"])
def test_prepare_rerun_preserves_all_previous_dvc_cache_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cache_link: str
) -> None:
    sources, spec_path, _ = _acquire(tmp_path, monkeypatch)
    prepared = tmp_path / "panel"
    panel_prepare.prepare(sources, prepared, spec_path)
    cache = tmp_path / "dvc-cache"
    cache.mkdir()
    old = []
    for number, path in enumerate(sorted(path for path in prepared.rglob("*") if path.is_file())):
        cached = cache / str(number)
        content = path.read_bytes()
        cached.write_bytes(content)
        cached.chmod(0o444)
        path.unlink()
        if cache_link == "hardlink":
            os.link(cached, path)
        else:
            path.symlink_to(cached)
        old.append((path, cached, content))
    panel_prepare.prepare(sources, prepared, spec_path)
    for path, cached, content in old:
        assert cached.read_bytes() == content
        assert path.exists()
        assert not path.is_symlink()
        assert not path.samefile(cached)
    _, tables = inputs(prepared, spec_path)
    assert len(tables["panel"]) == 7
    assert len(pd.read_parquet(prepared / "factors.parquet")) == 12


def test_source_vintage_and_prepared_features_reject_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources, spec_path, csv = _acquire(tmp_path, monkeypatch)
    prepared = tmp_path / "panel"
    panel_prepare.prepare(sources, prepared, spec_path)
    facts = next((prepared / "broad").glob("part-*.parquet"))
    frame = pd.read_parquet(facts)
    frame["value"] = "999"
    frame.to_parquet(facts, index=False)
    with pytest.raises(ValueError, match="Frozen artifact bytes changed"):
        inputs(prepared, spec_path)
    csv.write_text(csv.read_text().replace(",0.01,", ",0.02,"))
    with pytest.raises(ValueError, match="CRSP source vintage already exists"):
        run.acquire(
            csv,
            staging=sources.parent,
            canonical=tmp_path / "raw",
            params=spec_path,
            offline=True,
        )
    (sources / "sec/crosswalk.csv").write_text("changed")
    with pytest.raises(ValueError, match="Frozen artifact bytes changed"):
        panel_prepare.prepare(sources, prepared, spec_path)
