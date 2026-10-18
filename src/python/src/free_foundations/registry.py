"""Inspectable model catalogue; registration never imports a model runtime."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal


@dataclass(frozen=True)
class ModelSpec:
    """Installation and representation capabilities, independently of weights."""

    name: str
    repository: str
    extra: str
    extraction: Literal["native", "custom"]
    runtime: str

    @property
    def url(self) -> str:
        """Canonical checkpoint/model-card location."""
        return f"https://huggingface.co/{self.repository}"


_SPECS = (
    ModelSpec("exaone", "LG-AI-Research/EXAONE-Tabular", "exaone", "custom", "exaonetabular"),
    ModelSpec("tabpfn", "Prior-Labs/tabpfn_3_5", "tabpfn", "native", "tabpfn"),
    ModelSpec("limix", "stable-ai/LimiX-2", "limix", "custom", "LimiX"),
    ModelSpec("causilo", "nums-ai/causilo", "causilo", "custom", "causilo"),
    ModelSpec("tabfm", "google/tabfm-1.1.0-pytorch", "tabfm", "custom", "tabfm"),
    ModelSpec("sap", "SAP/sap-rpt-1-oss", "sap", "custom", "sap-rpt-oss"),
)
MODELS = MappingProxyType({spec.name: spec for spec in _SPECS})


def model_spec(name: str) -> ModelSpec:
    """Look up a model without downloading code or weights."""
    try:
        return MODELS[name]
    except KeyError:
        msg = f"Unknown model {name!r}; choose from {', '.join(MODELS)}"
        raise ValueError(msg) from None
