"""Versioned scientific choices and identities shared by every empirical stage."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

CHARACTERISTICS = (
    "market_cap_assets",
    "market_to_book",
    "dividend_yield",
    "debt_maturity",
)
RUNGS = ("fernandez", "standard_xbrl", "full_xbrl")
ROOT = Path("research/crsp-study")


@dataclass(frozen=True)
class StudySpec:
    """One common population, calendar and reproducible set of estimator conventions."""

    version: str = "crsp-sec-quarterly-v1"
    archive_start: str = "2001-01-01"
    archive_end: str = "2025-12-31"
    feature_start: str = "2009-01-01"
    top_n: int = 1000
    frequency: str = "quarterly"
    return_lookback_quarters: int = 20
    characteristic_history_years: int = 10
    min_eigenvalue: float = 1e-6
    seed: int = 42
    block_columns: int = 500
    support_rows: int = 256
    bootstrap_draws: int = 9999
    generated_beta_draws: int = 999
    bootstrap_blocks: tuple[int, ...] = (4, 2, 8)
    rungs: tuple[str, ...] = RUNGS
    models: tuple[str, ...] = ("tabpfn_full", "tabfm", "kumo", "limix")

    def __post_init__(self) -> None:
        """Reject a second clock or invalid numerical settings at the shared boundary."""
        if self.frequency != "quarterly":
            msg = "Every empirical analysis must use the quarterly master clock."
            raise ValueError(msg)
        if self.top_n < 1 or self.block_columns < 1 or self.support_rows < 2:
            msg = "Population, block and support sizes must be positive."
            raise ValueError(msg)
        if not 0 < self.min_eigenvalue < 1:
            msg = "The minimum correlation eigenvalue must lie in (0, 1)."
            raise ValueError(msg)
        if set(self.rungs) != set(RUNGS):
            msg = "The scientific contract requires all three information rungs."
            raise ValueError(msg)
        if len(self.rungs) != len(RUNGS) or len(set(self.models)) != len(self.models):
            msg = "Information rungs and model identifiers must be unique."
            raise ValueError(msg)
        if self.return_lookback_quarters < 1 or self.characteristic_history_years < 1:
            msg = "Return and characteristic lookbacks must be positive."
            raise ValueError(msg)
        if self.bootstrap_draws < 0 or self.generated_beta_draws < 0 or self.seed < 0:
            msg = "Bootstrap counts and the random seed must be nonnegative."
            raise ValueError(msg)
        if not self.bootstrap_blocks or any(block < 1 for block in self.bootstrap_blocks):
            msg = "Bootstrap blocks must be nonempty positive quarter counts."
            raise ValueError(msg)
        if (
            not pd.Timestamp(self.archive_start)
            <= pd.Timestamp(self.feature_start)
            <= pd.Timestamp(self.archive_end)
        ):
            msg = "The return archive must include the feature study's start date."
            raise ValueError(msg)

    def payload(self) -> dict[str, Any]:
        """Return JSON-compatible settings, including the common-mask policy."""
        return json.loads(json.dumps(asdict(self)))

    @property
    def digest(self) -> str:
        """Identify every scientific setting, independently of source-file identities."""
        return digest_json(self.payload())

    @classmethod
    def read(cls, path: Path) -> StudySpec:
        """Read the declared study without silently adopting new defaults for old versions."""
        value = json.loads(path.read_text())
        if value.get("version") != cls().version:
            msg = "Study configuration needs the supported explicit version."
            raise ValueError(msg)
        for field in ("bootstrap_blocks", "rungs", "models"):
            if field in value:
                value[field] = tuple(value[field])
        return cls(**value)


def digest_json(value: object) -> str:
    """Hash a deterministic JSON representation; reject nonfinite metadata."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def file_hash(path: Path) -> str:
    """Hash source bytes without loading large documents into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frame_digest(frame: pd.DataFrame) -> str:
    """Bind column order, row order, values and missingness of a canonical table."""
    digest = hashlib.sha256(json.dumps(list(frame.columns)).encode())
    digest.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())
    return digest.hexdigest()


def panel_contract(panel: pd.DataFrame, spec: StudySpec) -> dict[str, Any]:
    """Make independently selected samples or outcome masks detectably incompatible."""
    required = {"issuer_id", "quarter", "total_return", "observed"}
    if not required.issubset(panel.columns):
        msg = f"Master panel lacks {sorted(required - set(panel.columns))}."
        raise ValueError(msg)
    if panel.duplicated(["issuer_id", "quarter"]).any():
        msg = "Master panel has duplicate issuer-quarter keys."
        raise ValueError(msg)
    if panel["observed"].isna().any() or not panel["observed"].isin([True, False]).all():
        msg = "Master observed flags must be explicit booleans."
        raise ValueError(msg)
    returns = pd.to_numeric(panel["total_return"], errors="raise").to_numpy(float)
    if np.isinf(returns).any() or not np.array_equal(
        np.isfinite(returns), panel["observed"].to_numpy(bool)
    ):
        msg = "Master observed flags disagree with finite total returns."
        raise ValueError(msg)
    keys = panel[["issuer_id", "quarter"]]
    mask = panel[["issuer_id", "quarter", "observed"]]
    return {
        "study_sha256": spec.digest,
        "panel_sha256": frame_digest(panel),
        "roster_sha256": frame_digest(keys),
        "mask_sha256": frame_digest(mask),
        "rows": len(panel),
        "issuers": int(panel["issuer_id"].nunique()),
        "quarters": sorted(panel["quarter"].astype(str).unique().tolist()),
        "observed_issuer_quarters": int(panel["observed"].sum()),
        "frequency": spec.frequency,
    }
