"""Versioned scientific choices and identities shared by every empirical stage."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

CHARACTERISTICS = (
    "market_cap_assets",
    "market_to_book",
    "dividend_yield",
    "debt_maturity",
)
RUNGS = ("fernandez", "standard_xbrl")
PARAMS = Path("params.yaml")
# Settings that change the prepared master panel or formation cohorts. Analysis
# settings are bound by each downstream manifest through the full digest instead.
POPULATION_FIELDS = (
    "version",
    "archive_start",
    "archive_end",
    "feature_start",
    "top_n",
    "frequency",
    "formation_years",
    "window_quarters",
)


@dataclass(frozen=True)
class StudySpec:
    """One common population, calendar and in-sample inference convention.

    ``formation_years`` name Decembers whose top-``top_n`` roster starts a window of
    ``window_quarters`` outcome quarters. Fernández networks use her literal
    ``exp(-d)`` kernel. Comparison networks are symmetrized, row-normalized
    ``neighbours``-nearest-neighbour graphs, which depend only on distance order;
    ``neighbour_sensitivities`` repeat them. Only spatial coefficients, premia,
    scales and period effects are estimated.
    """

    version: str = "crsp-sec-quarterly-v2"
    archive_start: str = "2001-01-01"
    archive_end: str = "2025-12-31"
    feature_start: str = "2009-01-01"
    panel_start: str = "2011-01-01"
    top_n: int = 1000
    frequency: str = "quarterly"
    characteristic_history_years: int = 10
    window_quarters: int = 40
    formation_years: tuple[int, ...] = (2010, 2011, 2012, 2013, 2014, 2015)
    primary_formation: int = 2015
    neighbours: int = 10
    neighbour_sensitivities: tuple[int, ...] = (5, 20)
    min_beta_quarters: int = 8
    seed: int = 42
    block_columns: int = 500
    standard_min_coverage: float = 0.1
    support_rows: int = 256
    generated_beta_draws: int = 999
    likelihood_draws: int = 9999
    mantel_draws: int = 999
    rungs: tuple[str, ...] = RUNGS
    models: tuple[str, ...] = ("tabpfn_full", "tabfm", "kumo", "limix")

    def __post_init__(self) -> None:
        """Reject a second clock or invalid numerical settings at the shared boundary."""
        for valid, message in self._rules():
            if not valid:
                raise ValueError(message)

    def _rules(self) -> list[tuple[bool, str]]:
        start, end = pd.Timestamp(self.archive_start), pd.Timestamp(self.archive_end)
        draws = (self.generated_beta_draws, self.likelihood_draws, self.mantel_draws)
        return [
            (self.frequency == "quarterly", "Every analysis must use the quarterly clock."),
            (
                self.top_n >= 1 and self.block_columns >= 1 and self.support_rows >= 2,
                "Population, block and support sizes must be positive.",
            ),
            (tuple(self.rungs) == RUNGS, "The contract requires the declared rungs in order."),
            (len(set(self.models)) == len(self.models), "Model identifiers must be unique."),
            (
                0 <= self.standard_min_coverage <= 1,
                "Standard-rung coverage must be a share between zero and one.",
            ),
            (
                min(self.neighbours, *self.neighbour_sensitivities) >= 1,
                "Neighbour counts must be positive.",
            ),
            (
                3 <= self.min_beta_quarters <= self.window_quarters,
                "MM betas need at least three and at most the window's quarters.",
            ),
            (
                self.characteristic_history_years >= 1 and self.window_quarters >= 2,
                "Characteristic histories and outcome windows must be positive.",
            ),
            (
                self.primary_formation in self.formation_years,
                "The primary formation year must be one of the declared formations.",
            ),
            (min(draws) >= 0 and self.seed >= 0, "Draw counts and the seed must be nonnegative."),
            (
                start <= pd.Timestamp(self.feature_start) <= pd.Timestamp(self.panel_start) <= end,
                "The archive must contain the feature era, which must contain the panel.",
            ),
        ]

    def window(self, formation: int) -> pd.DatetimeIndex:
        """Outcome quarter ends following one December formation."""
        return pd.period_range(
            pd.Period(f"{formation + 1}Q1", freq="Q"), periods=self.window_quarters, freq="Q"
        ).to_timestamp("Q")

    @property
    def panel_calendar(self) -> pd.DatetimeIndex:
        """Quarter ends of the spatial co-movement panel."""
        return pd.period_range(self.panel_start, self.archive_end, freq="Q").to_timestamp("Q")

    def payload(self) -> dict[str, Any]:
        """Return JSON-compatible settings, including the common-mask policy."""
        return json.loads(json.dumps(asdict(self)))

    @property
    def population_digest(self) -> str:
        """Identify only the settings that define the prepared roster, mask and cohorts."""
        payload = self.payload()
        return digest_json({name: payload[name] for name in POPULATION_FIELDS})

    @property
    def digest(self) -> str:
        """Identify every scientific setting, independently of source-file identities."""
        return digest_json(self.payload())

    @classmethod
    def read(cls, path: Path = PARAMS) -> StudySpec:
        """Read the ``study`` section of DVC params, refusing an undeclared version."""
        value = yaml.safe_load(path.read_text())["study"]
        if value.get("version") != cls().version:
            msg = "Study parameters need the supported explicit version."
            raise ValueError(msg)
        for field in ("formation_years", "neighbour_sensitivities", "rungs", "models"):
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
        "population_sha256": spec.population_digest,
        "panel_sha256": frame_digest(panel),
        "roster_sha256": frame_digest(keys),
        "mask_sha256": frame_digest(mask),
        "rows": len(panel),
        "issuers": int(panel["issuer_id"].nunique()),
        "quarters": sorted(panel["quarter"].astype(str).unique().tolist()),
        "observed_issuer_quarters": int(panel["observed"].sum()),
        "frequency": spec.frequency,
    }
