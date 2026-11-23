"""Run one representation extraction."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from free_foundations.study.representations.contexts import load_contexts
from free_foundations.study.representations.encoding import write_states
from free_foundations.study.spec import PARAMS, StudySpec, file_hash

if TYPE_CHECKING:
    from pathlib import Path


def encode(  # noqa: PLR0913 -- explicit input and output paths plus cell selectors.
    prepared: Path,
    weights: Path,
    states: Path,
    output: Path,
    params: Path = PARAMS,
    *,
    rung: str,
    model: str,
    contexts: Path,
) -> None:
    """Extract matched full-coverage states independently of financial estimation."""
    spec = StudySpec.read(params)
    manifest = prepared / "manifest.json"
    contract = json.loads(manifest.read_bytes())["master"]
    if contract["population_sha256"] != spec.population_digest or rung not in spec.rungs:
        msg = "The model cell does not match the prepared population or information rung."
        raise ValueError(msg)
    digest = file_hash(manifest)
    write_states(
        load_contexts(contexts, (rung,), digest),
        spec,
        output,
        contract=contract,
        weights=weights,
        states_cache=states,
        input_digest=digest,
        only_model=model,
    )
