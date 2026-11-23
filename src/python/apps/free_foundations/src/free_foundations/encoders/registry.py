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
    ModelSpec("kumo", "nvidia/Kumo-Tabular", "kumo", "custom", "structured-data-models"),
    ModelSpec("tabpfn", "Prior-Labs/tabpfn_3_5", "tabpfn", "native", "tabpfn"),
    ModelSpec("limix", "stable-ai/LimiX-2", "limix", "custom", "LimiX"),
    ModelSpec("tabfm", "google/tabfm-1.1.0-pytorch", "tabfm", "custom", "tabfm"),
)
MODELS = MappingProxyType({spec.name: spec for spec in _SPECS})


def model_spec(name: str) -> ModelSpec:
    """Look up a model without downloading code or weights."""
    try:
        return MODELS[name]
    except KeyError:
        msg = f"Unknown model {name!r}; choose from {', '.join(MODELS)}"
        raise ValueError(msg) from None
