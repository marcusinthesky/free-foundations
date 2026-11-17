"""Completed source promotion preserves prior snapshots and obeys real filesystem locks."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from free_foundations.study import run
from free_foundations.study.source_io import atomic_bytes, sources_lock
from free_foundations.study.spec import StudySpec, file_hash


def _snapshot(
    output: Path,
    spec: StudySpec,
    label: str,
    *,
    csv: bytes = b"same CRSP bytes",
    phase: str = "originals",
) -> Path:
    sources = output / "sources"
    sources.mkdir(parents=True)
    (sources / "crsp.csv").write_bytes(csv)
    report = {"study_sha256": spec.digest, "crsp_sha256": file_hash(sources / "crsp.csv")}
    records = {
        "crsp-manifest.json": report,
        "sec/acquisition.json": {
            "metadata_complete": True,
            "phase": phase,
            "status": "initialized",
            "originals_pending": 0,
            "metadata_only": False,
        },
        "sec/metadata/identifier-acquisition.json": {"status": "acquired"},
        "factors/status.json": {"status": "complete"},
    }
    for name, value in records.items():
        path = sources / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
    (sources / "payload.txt").write_text(label)
    _manifest(sources, report)
    return sources


def _manifest(sources: Path, report: dict[str, str] | None = None) -> None:
    report = report or json.loads((sources / "crsp-manifest.json").read_text())
    files = run._inventory(sources)  # noqa: SLF001 -- fixture uses the real frozen inventory contract.
    (sources / "manifest.json").write_text(json.dumps({**report, "files": files}))


def _study(tmp_path: Path) -> tuple[StudySpec, Path, Path, Path]:
    spec = StudySpec()
    path = tmp_path / "study.json"
    path.write_text(json.dumps(spec.payload()))
    output = tmp_path / "study"
    return spec, path, output, output / "recovery"


def _can_lock(output: Path, *, exclusive: bool) -> bool:
    descriptor = os.open(output / ".sources.lock", os.O_RDWR)
    try:
        fcntl.flock(descriptor, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
    except BlockingIOError:
        return False
    else:
        return True
    finally:
        os.close(descriptor)


@pytest.mark.parametrize("phase", ["originals", "filings"])
@pytest.mark.parametrize("cache_link", ["hardlink", "symlink"])
def test_freeze_promotes_complete_snapshot_and_retains_old_cache_bytes(
    tmp_path: Path, phase: str, cache_link: str
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    current = _snapshot(output, spec, "old frozen payload")
    staged = _snapshot(staging, spec, "new recovered payload", phase=phase)
    cache = tmp_path / "dvc-cache-object"
    cache.write_bytes((current / "payload.txt").read_bytes())
    cache.chmod(0o444)
    (current / "payload.txt").unlink()
    if cache_link == "hardlink":
        os.link(cache, current / "payload.txt")
    else:
        (current / "payload.txt").symlink_to(cache)
    before = (current / "manifest.json").read_bytes()
    staged_manifest = (staged / "manifest.json").read_bytes()
    receipt = run.freeze(staging=staging, output=output, spec_path=spec_path)
    backup = Path(receipt["previous_sources"])
    assert not staged.exists()
    assert (current / "payload.txt").read_text() == "new recovered payload"
    assert (current / "manifest.json").read_bytes() == staged_manifest
    assert (backup / "manifest.json").read_bytes() == before
    assert (backup / "payload.txt").samefile(cache)
    assert cache.read_bytes() == b"old frozen payload"
    assert receipt["phase"] == "originals"
    assert receipt["acquisition_phase"] == phase


@pytest.mark.parametrize(
    "update",
    [
        {"phase": "metadata", "status": "metadata_ready", "metadata_only": True},
        {"metadata_complete": False},
        {"originals_pending": 1},
        {"originals_pending": False},
        {"status": "pending_network"},
        {"filing_statuses": {"no_native_facts": 1}},
    ],
)
def test_freeze_rejects_incomplete_sec_without_moving_sources(
    tmp_path: Path, update: dict[str, object]
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    current = _snapshot(output, spec, "old")
    staged = _snapshot(staging, spec, "new")
    path = staged / "sec/acquisition.json"
    path.write_text(json.dumps(json.loads(path.read_text()) | update))
    _manifest(staged)
    with pytest.raises(ValueError, match="completed originals phase"):
        run.freeze(staging=staging, output=output, spec_path=spec_path)
    assert (current / "payload.txt").read_text() == "old"
    assert (staged / "payload.txt").read_text() == "new"


@pytest.mark.parametrize("change", ["inventory", "declared_hash", "different_crsp", "spec"])
def test_freeze_rejects_mutated_or_mismatched_snapshot(tmp_path: Path, change: str) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    current = _snapshot(output, spec, "old")
    staged = _snapshot(
        staging,
        spec,
        "new",
        csv=b"different bytes" if change == "different_crsp" else b"same CRSP bytes",
    )
    if change == "inventory":
        (staged / "payload.txt").write_text("unrecorded mutation")
    elif change == "declared_hash":
        manifest = json.loads((staged / "manifest.json").read_text())
        manifest["crsp_sha256"] = "false claimed hash"
        (staged / "manifest.json").write_text(json.dumps(manifest))
    elif change == "spec":
        spec_path.write_text(json.dumps(StudySpec(top_n=99).payload()))
    with pytest.raises(ValueError, match=r"changed|inconsistent|different canonical"):
        run.freeze(staging=staging, output=output, spec_path=spec_path)
    assert (current / "payload.txt").read_text() == "old"
    assert staged.exists()


def test_promotion_rename_failure_rolls_back_prior_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    current = _snapshot(output, spec, "old")
    staged = _snapshot(staging, spec, "new")
    original = Path.rename

    def fail_promotion(source: Path, destination: Path) -> Path:
        if source == staged:
            message = "simulated promotion failure"
            raise OSError(message)
        return original(source, destination)

    monkeypatch.setattr(Path, "rename", fail_promotion)
    with pytest.raises(OSError, match="simulated promotion failure"):
        run.freeze(staging=staging, output=output, spec_path=spec_path)
    assert (current / "payload.txt").read_text() == "old"
    assert (staged / "payload.txt").read_text() == "new"
    assert not (output / "recovery/freeze-latest.json").exists()


@pytest.mark.parametrize("cache_link", ["hardlink", "symlink"])
def test_staged_acquisition_seeds_hardlinks_and_does_not_overwrite_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cache_link: str
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    current = _snapshot(output, spec, "old")
    csv = tmp_path / "incoming.csv"
    csv.write_bytes((current / "crsp.csv").read_bytes())
    cache = tmp_path / "cache-payload"
    cache.write_bytes((current / "payload.txt").read_bytes())
    (current / "payload.txt").unlink()
    if cache_link == "hardlink":
        os.link(cache, current / "payload.txt")
    else:
        (current / "payload.txt").symlink_to(os.path.relpath(cache, current))
    monkeypatch.setattr(run, "ROOT", output)
    calls = []

    def acquire_no_network(*_args: object, **_kwargs: object) -> None:
        staged = staging / "sources"
        assert (staged / "crsp.csv").samefile(current / "crsp.csv")
        assert (staged / "payload.txt").samefile(current / "payload.txt")
        assert not (staged / "payload.txt").is_symlink()
        atomic_bytes(staged / "payload.txt", b"new")
        calls.append("seeded")

    monkeypatch.setattr(run, "_acquire", acquire_no_network)
    run.acquire(csv, output=staging, spec_path=spec_path, offline=True)
    assert calls == ["seeded"]
    assert (current / "payload.txt").read_text() == "old"
    assert (staging / "sources/payload.txt").read_text() == "new"


@pytest.mark.parametrize("existing", [True, False])
def test_acquisition_preserves_existing_stage_and_never_seeds_a_different_csv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, existing: bool
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    _snapshot(output, spec, "canonical")
    if existing:
        _snapshot(staging, spec, "existing in-progress sources")
    csv = tmp_path / "incoming.csv"
    csv.write_bytes(b"different CRSP vintage")
    monkeypatch.setattr(run, "ROOT", output)

    def inspect_stage(*_args: object, **_kwargs: object) -> None:
        if existing:
            assert (staging / "sources/payload.txt").read_text() == "existing in-progress sources"
        else:
            assert not (staging / "sources").exists()

    monkeypatch.setattr(run, "_acquire", inspect_stage)
    run.acquire(csv, output=staging, spec_path=spec_path, offline=True)


@pytest.mark.parametrize("operation", ["acquire", "link", "prepare"])
def test_source_entrypoints_hold_required_lock_through_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    _, spec_path, output, _ = _study(tmp_path)
    monkeypatch.setattr(run, "ROOT", output)
    csv = tmp_path / "incoming.csv"
    csv.write_bytes(b"fixture")
    calls = []

    def work(*_args: object, **_kwargs: object) -> None:
        assert not _can_lock(output, exclusive=True)
        assert _can_lock(output, exclusive=False) == (operation == "prepare")
        calls.append(operation)

    if operation == "acquire":
        monkeypatch.setattr(run, "_acquire", work)
        run.acquire(csv, output=output, spec_path=spec_path, offline=True)
    elif operation == "link":

        def no_build(*_args: object) -> dict[str, pd.DataFrame]:
            return {"monthly": pd.DataFrame()}

        monkeypatch.setattr(run, "build_crsp", no_build)
        monkeypatch.setattr(run, "_recover_links", work)
        run.link(csv, output=output, spec_path=spec_path, offline=True)
    else:
        monkeypatch.setattr(run, "_prepare", work)
        run.prepare(output=output, spec_path=spec_path)
    assert calls == [operation]
    assert _can_lock(output, exclusive=True)


def test_freeze_holds_stage_then_canonical_exclusive_locks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec, spec_path, output, staging = _study(tmp_path)
    _snapshot(output, spec, "old")
    _snapshot(staging, spec, "new")
    original = run._freeze_validation  # noqa: SLF001 -- observe actual lock state at validation.

    def validate(staged: Path, current: Path, study: StudySpec) -> dict[str, Any]:
        assert not _can_lock(staging, exclusive=False)
        assert not _can_lock(output, exclusive=False)
        return original(staged, current, study)

    monkeypatch.setattr(run, "_freeze_validation", validate)
    run.freeze(staging=staging, output=output, spec_path=spec_path)


def test_read_lock_can_coexist_and_releases_after_error(tmp_path: Path) -> None:
    with sources_lock(tmp_path, exclusive=False):
        assert _can_lock(tmp_path, exclusive=False)
        assert not _can_lock(tmp_path, exclusive=True)
    assert _can_lock(tmp_path, exclusive=True)
