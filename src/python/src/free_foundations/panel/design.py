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
    with next-snapshot income/assets as the support label, the same pair on shared
    support rows, and their combination. ``support_draws`` re-encode the history rung on
    differently salted 256-row supports. ``decoded`` adds networks from exposures decoded
    out of each representation, calibrated to prior-window reference-factor exposures.
    ``exclude`` drops named firms from every cohort. ``support_sizes`` re-encode the history
    rung on nested prefixes of the 256-row support. ``representations`` and ``models``
    restrict a design to declared readouts; ``None`` keeps every one.
    """

    name: str
    characteristics: tuple[str, ...]
    history: int
    rungs: tuple[str, ...] = RUNGS
    extra_histories: tuple[int, ...] = ()
    alternate_target: bool = False
    save_matrices: bool = True
    support_draws: tuple[str, ...] = ()
    decoded: bool = False
    exclude: tuple[str, ...] = ()
    support_sizes: tuple[int, ...] = ()
    representations: tuple[str, ...] | None = None
    models: tuple[str, ...] | None = None
    calibration_sizes: tuple[int, ...] = ()
    encode_extra_histories: bool = True

    @property
    def cohort_histories(self) -> tuple[int, ...]:
        """History lengths at which every cohort firm must be complete and nonconstant."""
        return tuple(sorted({self.history, *self.extra_histories}))

    @property
    def output(self) -> Path:
        """Output directory; the original v1 artifacts stay at the panel root."""
        return ROOT / self.name


DRAWS = ("redraw1", "redraw2")
# Smaller nested supports; the native history rung is the 256-row cap.
SUPPORT_SIZES = (32, 64, 128)
FOCUSED = (
    "direct",
    "pca16",
    "supervised_mlp16",
    "tabfm__early_concat",
    "tabfm__early_concat_labelnull",
    "tabpfn_full__late",
    "tabpfn_full_random__late",
)
FOUNDATION_MODELS = (
    "tabpfn_full",
    "tabpfn_full_random",
    "tabpfn_full_random43",
    "tabpfn_full_random44",
    "tabfm",
    "kumo",
    "kumo_random",
    "kumo_random43",
    "kumo_random44",
    "limix",
)
FOUNDATION_READOUTS = (
    "direct",
    "pca16",
    "supervised_mlp16",
    "tabpfn_full__late",
    "tabpfn_full_random__late",
    "tabpfn_full_random43__late",
    "tabpfn_full_random44__late",
    "tabfm__late",
    "tabfm__early_concat",
    "kumo__late",
    "kumo__early_concat",
    "kumo_random__late",
    "kumo_random43__late",
    "kumo_random44__late",
    "limix__late",
)
DESIGNS = {
    "three-foundations": Design(
        "three-foundations",
        CHARACTERISTICS[:3],
        5,
        ("histories",),
        extra_histories=(3,),
        save_matrices=False,
        decoded=True,
        support_sizes=SUPPORT_SIZES,
        representations=FOUNDATION_READOUTS,
        models=FOUNDATION_MODELS,
        calibration_sizes=(32, 64, 128, 256),
        encode_extra_histories=False,
    ),
    "four": Design(
        "four", CHARACTERISTICS, 3, alternate_target=True, support_draws=DRAWS, decoded=True
    ),
    "four-h5": Design("four-h5", CHARACTERISTICS, 5, ("histories",), (3,)),
    # QXO's genuine -80% repricing on 2024-07-30 sits in the 2024 returns and 2025 prior.
    "four-xqxo": Design("four-xqxo", CHARACTERISTICS, 3, ("histories",), exclude=("QXO",)),
    # About 450 firms a year: keep fingerprints, not every N x N matrix, on a full disk.
    "three": Design(
        "three",
        CHARACTERISTICS[:3],
        5,
        extra_histories=(3,),
        alternate_target=True,
        save_matrices=False,
        support_draws=DRAWS,
        decoded=True,
    ),
    # Declared before any support-size result: no learning, unsupervised and supervised
    # controls without pretraining, one state readout with its label-null twin, and one
    # task readout from another family with its untrained-architecture twin.
    "three-support": Design(
        "three-support",
        CHARACTERISTICS[:3],
        5,
        ("histories",),
        extra_histories=(3,),
        save_matrices=False,
        decoded=True,
        support_sizes=SUPPORT_SIZES,
        representations=FOCUSED,
        models=("tabpfn_full", "tabpfn_full_random", "tabfm", "tabfm_labelnull"),
    ),
}
