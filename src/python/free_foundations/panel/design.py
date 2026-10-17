"""Declared panel designs: characteristic arm, history lengths, rungs and outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from free_foundations.fernandez.characteristics import CHARACTERISTICS
from free_foundations.panel.characteristics import ROOT

if TYPE_CHECKING:
    from pathlib import Path

RUNGS = ("histories", "broad", "metrics")


@dataclass(frozen=True)
class Design:
    """One matched comparison; designs are reported separately and never ranked.

    ``history`` is the principal network history length. ``extra_histories`` add
    Fernández and history-rung networks of other lengths on the same firms, so the
    cohort requires the longest history. ``alternate_target`` adds the history rung
    with next-snapshot income/assets as the support label.
    """

    name: str
    characteristics: tuple[str, ...]
    history: int
    rungs: tuple[str, ...] = RUNGS
    extra_histories: tuple[int, ...] = ()
    alternate_target: bool = False
    save_matrices: bool = True

    @property
    def cohort_histories(self) -> tuple[int, ...]:
        """History lengths at which every cohort firm must be complete and nonconstant."""
        return tuple(sorted({self.history, *self.extra_histories}))

    @property
    def output(self) -> Path:
        """Output directory; the original v1 artifacts stay at the panel root."""
        return ROOT / self.name


DESIGNS = {
    "four": Design("four", CHARACTERISTICS, 3, alternate_target=True),
    "four-h5": Design("four-h5", CHARACTERISTICS, 5, ("histories",), (3,)),
    # About 450 firms a year: keep fingerprints, not every N x N matrix, on a full disk.
    "three": Design(
        "three",
        CHARACTERISTICS[:3],
        5,
        extra_histories=(3,),
        alternate_target=True,
        save_matrices=False,
    ),
}
