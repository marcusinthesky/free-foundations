"""Publication requires defined financial results and full source-recovery evidence."""

from __future__ import annotations

import json
import os
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pytest

from free_foundations.study.publication import render
from free_foundations.study.spec import StudySpec, frame_digest, panel_contract

if TYPE_CHECKING:
    from pathlib import Path


def _saved_study(
    root: Path,
    *,
    defined: tuple[bool, bool, bool] = (True, True, False),
    source: str | None = "complete",
    models: str = "complete",
) -> StudySpec:
    spec = replace(
        StudySpec(),
        feature_start="2010-01-01",
        archive_end="2010-03-31",
        bootstrap_draws=19,
        generated_beta_draws=5,
    )
    quarter = pd.Timestamp("2010-03-31")
    population = pd.DataFrame(
        {
            "issuer_id": ["PERMCO:1", "PERMCO:2"],
            "quarter": [quarter, quarter],
            "total_return": [0.1, np.nan],
            "observed": [True, False],
            "xbrl_available": [True, True],
            "xbrl_status": ["available", "available"],
            "xbrl_reason": ["Verified public scalar", "Verified public scalar"],
        }
    )
    prepared = root / "prepared"
    prepared.mkdir(parents=True)
    population.to_parquet(prepared / "panel.parquet", index=False)
    population.to_parquet(prepared / "population.parquet", index=False)
    pd.DataFrame({"characteristic": ["debt_maturity"], "status": ["available"]}).to_parquet(
        prepared / "characteristics.parquet", index=False
    )
    master = panel_contract(population, spec)
    preparation = {
        "master": master,
        "population_sha256": frame_digest(population),
        "availability": {"available": 2},
        "availability_reasons": {"Verified public scalar": 2},
    }
    if source is not None:
        preparation["source_recovery"] = {
            "status": source,
            "complete": source == "complete",
            "full_xbrl_complete": source == "complete",
            "reasons": [] if source == "complete" else ["Original filing recovery is pending."],
            "unresolved_linkage_issuer_quarters": 0,
            "sec_phase": "originals" if source == "complete" else "metadata",
            "sec_status": "initialized" if source == "complete" else "metadata_ready",
            "originals_pending": 0 if source == "complete" else 12,
        }
    (prepared / "manifest.json").write_text(json.dumps(preparation))
    representations = root / "representations"
    representations.mkdir()
    (representations / "manifest.json").write_text(
        json.dumps({"master": master, "status": models, "states": []})
    )
    core_defined, score_defined, decoder_defined = defined
    frames = {
        "replication": {
            "core": pd.DataFrame(
                {
                    "quarter": [quarter],
                    "method": ["fernandez_joint"],
                    "estimator": ["ols"],
                    "status": ["available"],
                    "premium_market": [0.05 if core_defined else np.nan],
                    "intensity": [0.0],
                }
            )
        },
        "measurement": {
            "scores": pd.DataFrame(
                {
                    "quarter": [quarter],
                    "method": ["full_xbrl/model|gram|correlation"],
                    "status": ["available"],
                    "score_per_issuer": [-1.5 if score_defined else np.nan],
                }
            ),
            "decoder_quality": pd.DataFrame(
                {
                    "quarter": [quarter],
                    "method": ["full_xbrl/model"],
                    "status": ["available"],
                    "decoder_r2": [0.9 if decoder_defined else np.nan],
                    "labeled_issuers": [2],
                }
            ),
        },
    }
    for stage, tables in frames.items():
        folder = root / stage
        folder.mkdir()
        for name, frame in tables.items():
            frame.to_parquet(folder / f"{name}.parquet", index=False)
        (folder / "manifest.json").write_text(
            json.dumps(
                {
                    "master": master,
                    "status": "available",
                    "files": {name: f"{name}.parquet" for name in tables},
                }
            )
        )
    return spec


def _claims(root: Path) -> dict[str, Any]:
    return json.loads((root / "publication/claims-audit.json").read_text())


def test_completed_stages_with_undefined_fits_cannot_claim_empirical_findings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _saved_study(tmp_path, defined=(False, False, False))
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "no_defined_empirical_results"
    assert audit["defined_numerical_rows"] == 0
    assert audit["defined_rows_by_task"]["replication"]["core"] == 0
    assert audit["defined_rows_by_task"]["measurement"]["scores"] == 0
    assert not audit["claims"]["new_empirical_findings_available"]
    summary = pd.read_csv(tmp_path / "publication/measurement-score-summary.csv")
    assert summary.empty


def test_decoder_quality_alone_is_not_a_defined_financial_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _saved_study(tmp_path, defined=(False, False, True))
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["defined_numerical_rows"] == 1
    assert audit["status"] == "no_defined_empirical_results"
    assert not audit["claims"]["new_empirical_findings_available"]


@pytest.mark.parametrize("defined", [(True, False, True), (False, True, True)])
def test_each_financial_task_needs_defined_results_before_publication_is_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defined: tuple[bool, bool, bool]
) -> None:
    spec = _saved_study(tmp_path, defined=defined)
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "incomplete_empirical_results"
    assert not audit["claims"]["new_empirical_findings_available"]


@pytest.mark.parametrize("source", ["metadata_only", "incomplete", None])
def test_partial_or_unrecorded_sec_recovery_cannot_produce_completed_study_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str | None
) -> None:
    spec = _saved_study(tmp_path, source=source)
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "source_recovery_pending"
    assert audit["defined_numerical_rows"] == 2
    assert not audit["claims"]["sec_source_recovery_complete"]
    assert not audit["claims"]["new_empirical_findings_available"]
    assert audit["source_recovery"]["reasons"]
    assert audit["source_reasons"] == {"Verified public scalar": 2}


@pytest.mark.parametrize(
    "bad_field", ["full_xbrl_complete", "originals_pending", "unresolved_linkage_issuer_quarters"]
)
def test_inconsistent_complete_source_receipt_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_field: str
) -> None:
    spec = _saved_study(tmp_path)
    path = tmp_path / "prepared/manifest.json"
    prepared = json.loads(path.read_text())
    prepared["source_recovery"][bad_field] = False if bad_field == "full_xbrl_complete" else 3
    path.write_text(json.dumps(prepared))
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "source_recovery_pending"
    assert audit["source_recovery"]["status"] == "incomplete"
    assert not audit["claims"]["new_empirical_findings_available"]


def test_unavailable_model_stage_keeps_results_pending_even_with_defined_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _saved_study(tmp_path, models="incomplete")
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "results_pending"
    assert not audit["claims"]["new_empirical_findings_available"]


def test_completed_sources_and_defined_financial_tasks_allow_qualified_findings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _saved_study(tmp_path)
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    audit = _claims(tmp_path)
    assert audit["status"] == "complete"
    assert audit["claims"]["new_empirical_findings_available"]
    assert audit["claims"]["sec_source_recovery_complete"]
    assert audit["defined_rows_by_task"]["replication"]["core"] == 1
    assert audit["defined_rows_by_task"]["measurement"]["scores"] == 1
    text = (tmp_path / "src/latex/build/crsp-study.tex").read_text()
    assert "uses 19 paired quarterly resamples" in text
    assert "requests 5 MM reestimates" in text
    assert "exactly that same repaired Gram" in text


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_rerender_replaces_linked_tables_and_manuscript_without_modifying_dvc_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    spec = _saved_study(tmp_path)
    monkeypatch.chdir(tmp_path)
    render(tmp_path, spec)
    cache = tmp_path / "cache"
    cache.mkdir()
    target = tmp_path / "src/latex/build/crsp-study.tex"
    paths = [*sorted((tmp_path / "publication").iterdir()), target]
    frozen = []
    for index, path in enumerate(paths):
        cached = cache / f"{index:04}-{path.name}"
        before = path.read_bytes()
        cached.write_bytes(before)
        cached.chmod(0o444)
        path.unlink()
        if kind == "hardlink":
            os.link(cached, path)
        else:
            path.symlink_to(cached)
        frozen.append((path, cached, before))
    scores = tmp_path / "measurement/scores.parquet"
    frame = pd.read_parquet(scores).assign(score_per_issuer=-2.5)
    frame.to_parquet(scores, index=False)
    render(tmp_path, spec)
    for destination, cached, before in frozen:
        assert cached.read_bytes() == before
        assert not destination.is_symlink()
        assert not destination.samefile(cached)
    summary = pd.read_csv(tmp_path / "publication/measurement-score-summary.csv")
    assert summary.loc[0, "mean_score_per_issuer"] == -2.5
