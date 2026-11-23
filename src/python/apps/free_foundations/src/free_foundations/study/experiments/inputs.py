"""Shared inputs of the research stages: the verified panel, cohorts and networks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

from free_foundations.methods.networks import CHARACTERISTICS, Network, roster_networks
from free_foundations.study.panel.store import inputs
from free_foundations.study.representations.contexts import original_view
from free_foundations.study.representations.store import RepresentationStore
from free_foundations.study.spec import file_hash

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np

    from free_foundations.study.spec import StudySpec


@dataclass(frozen=True)
class StudyInputs:
    """One verified prepared panel with its representation store."""

    spec: StudySpec
    tables: dict[str, pd.DataFrame]
    store: RepresentationStore | None

    @property
    def factors(self) -> pd.DataFrame:
        """Quarterly French factors indexed by quarter end."""
        frame = self.tables["factors"].copy()
        frame["quarter"] = pd.to_datetime(frame["quarter"]).dt.to_period("Q").dt.to_timestamp("Q")
        return frame.set_index("quarter").sort_index()

    def roster(self, quarter: pd.Timestamp) -> pd.DataFrame:
        """Analytical issuer rows for one quarter, sorted by issuer."""
        panel = self.tables["panel"]
        rows = panel.loc[pd.to_datetime(panel["quarter"]).eq(quarter)]
        return rows.sort_values("issuer_id").reset_index(drop=True)

    def histories(self, rows: pd.DataFrame) -> dict[str, np.ndarray]:
        """Annual as-of characteristic slots for each roster row (issuers by slots)."""
        view = original_view(rows, self.tables["characteristics"], self.spec)
        years = self.spec.characteristic_history_years
        return {
            name: view[
                [f"original:{name}:annual_lag{lag}" for lag in reversed(range(years))]
            ].to_numpy(float)
            for name in CHARACTERISTICS
        }

    def formation_equity(self, formation: int, issuers: tuple[str, ...]) -> np.ndarray:
        """Issuer market equity (USD) at the December formation, summed over classes."""
        membership = self.tables["membership"]
        selected = membership.loc[membership["formation_year"].eq(formation)]
        totals = selected.groupby("permco")["market_cap_usd"].sum()
        totals.index = "PERMCO:" + totals.index.astype(str)
        return totals.reindex(list(issuers)).to_numpy(float)

    def networks(
        self, quarter: pd.Timestamp, rows: pd.DataFrame, neighbours: tuple[int, ...]
    ) -> dict[str, Network]:
        """Every network for a roster whose information is as of ``quarter``."""
        issuers = tuple(rows["issuer_id"].astype(str))
        states = self.store.states(quarter, issuers) if self.store is not None else {}
        spec = self.spec
        return roster_networks(
            issuers,
            self.histories(rows),
            states,
            self.formation_equity(quarter.year - 1, issuers),
            rows["sic"],
            neighbours=neighbours,
            seed=spec.seed,
        )


def load(panel: Path, representations: Path | None, params: Path) -> StudyInputs:
    """Verify the prepared panel and, when given, its representation manifest."""
    spec, tables = inputs(panel, params)
    store = (
        RepresentationStore(
            representations,
            tables["panel"],
            spec,
            expected_input_digest=file_hash(panel / "manifest.json"),
        )
        if representations is not None
        else None
    )
    return StudyInputs(spec, tables, store)
