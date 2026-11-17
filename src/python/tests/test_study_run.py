"""Frozen-source integration checks for the single quarterly experiment."""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.study import run
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
    study = StudySpec(archive_start="2008-01-01", archive_end="2010-12-31", top_n=1)
    spec_path = tmp_path / "study.json"
    spec_path.write_text(json.dumps(study.payload()))
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
    output = tmp_path / "study"
    run.acquire(csv, script, output=output, spec_path=spec_path, offline=True)
    return output, spec_path, csv


def _no_links(_monthly: pd.DataFrame, _sources: Path, *, offline: bool) -> None:
    assert offline


def test_frozen_source_to_one_unbalanced_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output, spec_path, csv = _acquire(tmp_path, monkeypatch)
    assert (output / "sources/crsp.csv").read_bytes() == csv.read_bytes()
    assert "Do not execute" in (output / "sources/extraction.py.txt").read_text()
    run.prepare(output=output, spec_path=spec_path)
    study, tables = run.inputs(output, spec_path)
    population = pd.read_parquet(output / "prepared/population.parquet")
    manifest = json.loads((output / "prepared/manifest.json").read_text())
    assert len(population) == 8
    assert len(tables["panel"]) == 7
    missing = tables["panel"]["quarter"].eq(pd.Timestamp("2009-09-30"))
    assert not bool(tables["panel"].loc[missing, "observed"].iloc[0])
    assert len(tables["characteristics"]) == 32
    assert tables["characteristics"]["value"].isna().all()
    assert manifest["master"] == panel_contract(tables["panel"], study)
    assert manifest["no_complete_case_selection"]
    assert set(tables["panel"]["issuer_id"]) == {"PERMCO:2"}
    assert tables["history"]["quarter"].min() == pd.Timestamp("2008-03-31")


@pytest.mark.parametrize("cache_link", ["hardlink", "symlink"])
def test_prepare_rerun_preserves_all_previous_dvc_cache_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cache_link: str
) -> None:
    output, spec_path, _ = _acquire(tmp_path, monkeypatch)
    run.prepare(output=output, spec_path=spec_path)
    prepared = output / "prepared"
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
    run.prepare(output=output, spec_path=spec_path)
    for path, cached, content in old:
        assert cached.read_bytes() == content
        assert path.exists()
        assert not path.is_symlink()
        assert not path.samefile(cached)
    _, tables = run.inputs(output, spec_path)
    assert len(tables["panel"]) == 7
    assert len(pd.read_parquet(prepared / "factors.parquet")) == 12


def test_source_vintage_and_prepared_features_reject_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output, spec_path, csv = _acquire(tmp_path, monkeypatch)
    run.prepare(output=output, spec_path=spec_path)
    facts = next((output / "prepared/broad").glob("part-*.parquet"))
    frame = pd.read_parquet(facts)
    frame["value"] = "999"
    frame.to_parquet(facts, index=False)
    with pytest.raises(ValueError, match="Frozen artifact bytes changed"):
        run.inputs(output, spec_path)
    csv.write_text(csv.read_text().replace(",0.01,", ",0.02,"))
    with pytest.raises(ValueError, match="CRSP source vintage already exists"):
        run.acquire(csv, output=output, spec_path=spec_path, offline=True)
    (output / "sources/sec/crosswalk.csv").write_text("changed")
    with pytest.raises(ValueError, match="Frozen artifact bytes changed"):
        run.prepare(output=output, spec_path=spec_path)


def test_companyfacts_only_source_cannot_be_reported_as_full_filing_xbrl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output, spec_path, _ = _acquire(tmp_path, monkeypatch)
    run.prepare(output=output, spec_path=spec_path)
    run.encode(output=output, spec_path=spec_path)
    prepared = json.loads((output / "prepared/manifest.json").read_text())
    manifest = json.loads((output / "representations/manifest.json").read_text())
    full = [record for record in manifest["states"] if record["rung"] == "full_xbrl"]
    assert len(full) == 7
    assert {record["status"] for record in full} == {"source_rung_unavailable"}
    assert {record["reason"] for record in full} == {"original_filing_recovery_incomplete"}
    assert manifest["master"] == prepared["master"]
    assert not prepared["source_recovery"]["complete"]
    assert not prepared["source_recovery"]["full_xbrl_complete"]


def test_task_dispatch_reuses_identical_master(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from free_foundations.study import analysis  # noqa: PLC0415

    output, spec_path, _ = _acquire(tmp_path, monkeypatch)
    run.prepare(output=output, spec_path=spec_path)
    observed: list[tuple[str, dict[str, object]]] = []

    def record(
        panel: pd.DataFrame,
        _characteristics: pd.DataFrame,
        _factors: pd.DataFrame,
        _states: object,
        study: StudySpec,
        _destination: Path,
        **kwargs: object,
    ) -> None:
        observed.append((str(kwargs["tasks"]), panel_contract(panel, study)))

    def empty_states(*_args: object, **_kwargs: object) -> dict[object, object]:
        return {}

    monkeypatch.setattr(run, "load_representations", empty_states)
    monkeypatch.setattr(analysis, "run_analyses", record)
    run.analyze(output=output, spec_path=spec_path)
    run.analyze(output=output, spec_path=spec_path, replication_only=True)
    assert [task for task, _ in observed] == ["measurement", "replication"]
    assert observed[0][1] == observed[1][1]
