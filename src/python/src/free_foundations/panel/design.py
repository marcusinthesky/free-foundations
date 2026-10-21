"""The single retained measurement study and its bounded diagnostic inventories."""

from dataclasses import dataclass
from pathlib import Path

from free_foundations.fernandez.characteristics import CHARACTERISTICS

PRINCIPAL = (
    "direct",
    "pca16",
    "supervised_mlp16",
    "tabpfn_full__late",
    "tabfm__late",
    "kumo__late",
    "limix__late",
)
PRETRAINED = PRINCIPAL[3:]
RESET_MODELS = tuple(
    f"{model}_random{suffix}" for model in ("tabpfn_full", "kumo") for suffix in ("", "43", "44")
)
FOUNDATION_MODELS = ("tabpfn_full", "tabfm", "kumo", "limix", *RESET_MODELS)
FOUNDATION_READOUTS = (*PRINCIPAL, *(f"{model}__late" for model in RESET_MODELS))
SUPPORT_SIZES = (32, 64, 128)
CALIBRATION_SIZES = (32, 64, 128, 256)
PREPARED = Path("research/panel/prepared")
STATES = Path("research/panel/representations")
VALIDATION = Path("research/panel/three-foundations-validation")


@dataclass(frozen=True)
class Design:
    """Fixed cohorts and information sets; no canonical subset-run interface."""

    name: str = "three-foundations"
    characteristics: tuple[str, ...] = CHARACTERISTICS[:3]
    history: int = 5
    # Preserve the original eligibility rule, including its shorter-history check.
    cohort_histories: tuple[int, ...] = (3, 5)
    output: Path = Path("research/panel/three-foundations")


STUDY = Design()
