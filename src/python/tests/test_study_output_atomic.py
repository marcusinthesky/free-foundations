"""Direct numerical reruns preserve earlier immutable DVC cache file objects."""

# Integration checks deliberately include the internal NPZ and MM cache boundaries.
# ruff: noqa: SLF001

from __future__ import annotations

import os
from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.study import analysis, encoding
from free_foundations.study.spec import CHARACTERISTICS, StudySpec

if TYPE_CHECKING:
    from pathlib import Path


def _freeze_files(root: Path, cache: Path, kind: str) -> list[tuple[Path, Path, bytes]]:
    cache.mkdir()
    frozen = []
    for index, path in enumerate(sorted(item for item in root.rglob("*") if item.is_file())):
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
    return frozen


def _assert_cache_untouched(frozen: list[tuple[Path, Path, bytes]]) -> None:
    for destination, cached, before in frozen:
        assert cached.read_bytes() == before
        assert not destination.is_symlink()
        assert not destination.samefile(cached)


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_encoder_npz_replaces_dvc_links_without_changing_frozen_states(
    tmp_path: Path, kind: str
) -> None:
    output = tmp_path / "states"
    output.mkdir()
    filename = output / "states.npz"
    encoding._save_states(filename, {"model": np.array([[1.0, 2.0]])})
    frozen = _freeze_files(output, tmp_path / "cache", kind)
    encoding._save_states(filename, {"model": np.array([[3.0, 4.0]])})
    with np.load(filename, allow_pickle=False) as states:
        np.testing.assert_array_equal(states["model"], [[3, 4]])
    _assert_cache_untouched(frozen)


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
@pytest.mark.parametrize("failed_original", [False, True])
def test_mm_wrapper_refits_in_fresh_files_then_replaces_every_cache_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str, *, failed_original: bool
) -> None:
    dates = pd.date_range("2010-03-31", periods=3, freq="QE")
    sample = pd.DataFrame(
        {"date": dates, "ticker": "A", "excess": [0.1, 0.2, 0.3], "market": [0.2, 0.1, 0.4]}
    )
    spec = replace(StudySpec(), generated_beta_draws=0)
    directories = []

    def legacy_wrapper(values: pd.DataFrame, destination: Path, **_options: object) -> pd.DataFrame:
        directories.append(destination)
        cache = destination / "cache"
        cache.mkdir()
        estimates = pd.DataFrame(
            {
                "replicate": [0],
                "ticker": ["A"],
                "term": ["market"],
                "estimate": [float(values["excess"].sum())],
                "converged": [not failed_original],
            }
        )
        values.to_csv(cache / "mm-study-capm-input.csv", index=False)
        estimates.to_csv(cache / "mm-study-capm-output.csv", index=False)
        (cache / "mm-study-capm-output-runtime.csv").write_text("name,value\nbackend,fixture\n")
        if failed_original:
            message = "At least one robust MM fit on the original sample did not converge."
            raise RuntimeError(message)
        return estimates

    monkeypatch.setattr(analysis, "robust_betas", legacy_wrapper)
    output = tmp_path / "analysis"
    analysis._mm_estimates(sample, dates, spec, output)
    frozen = _freeze_files(output, tmp_path / "cache", kind)
    changed = sample.assign(excess=sample["excess"] + 0.5)
    result = analysis._mm_estimates(changed, dates, spec, output)
    assert len(directories) == 2
    assert directories[0] != directories[1]
    assert all(not path.exists() for path in directories)
    assert result.loc[0, "estimate"] == pytest.approx(changed["excess"].sum())
    assert result.loc[0, "converged"] == (not failed_original)
    _assert_cache_untouched(frozen)


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_analysis_cli_rerun_replaces_numeric_tables_and_pairwise_archives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    dates = pd.date_range("2010-03-31", periods=3, freq="QE")
    issuers = ("A", "B", "C")
    rng = np.random.default_rng(59)
    panel = pd.DataFrame(
        [
            {"quarter": date, "issuer_id": issuer, "total_return": rng.normal(), "observed": True}
            for date in dates
            for issuer in issuers
        ]
    )
    chars = panel[["issuer_id", "quarter"]].copy()
    for characteristic in CHARACTERISTICS:
        chars[characteristic] = rng.normal(size=len(chars))
    factors = pd.DataFrame(
        {"quarter": dates, "RF": 0.001, **dict.fromkeys(analysis.FACTOR_NAMES, 0.01)}
    )
    spec = replace(
        StudySpec(),
        feature_start="2010-01-01",
        archive_end="2010-09-30",
        generated_beta_draws=0,
        bootstrap_draws=0,
    )

    def fixed_mm(
        _sample: pd.DataFrame, _dates: pd.DatetimeIndex, _spec: StudySpec, _output: Path
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "replicate": [0, 0, 0],
                "ticker": list(issuers),
                "term": ["market"] * 3,
                "estimate": [1.0, 2.0, 3.0],
                "converged": [True] * 3,
            }
        )

    monkeypatch.setattr(analysis, "_mm_estimates", fixed_mm)
    output = tmp_path / "analysis"
    analysis.run_analyses(panel, chars, factors, {}, spec, output, tasks="replication")
    frozen = _freeze_files(output, tmp_path / "cache", kind)
    changed = panel.assign(total_return=panel["total_return"] + 0.001)
    result = analysis.run_analyses(changed, chars, factors, {}, spec, output, tasks="replication")
    assert not result["core"].empty
    assert list((output / "pairwise").glob("*.npz"))
    assert (output / "core.parquet").exists()
    _assert_cache_untouched(frozen)
