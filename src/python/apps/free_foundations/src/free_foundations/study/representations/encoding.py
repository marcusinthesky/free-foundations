"""Extract frozen states from shared dated contexts."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from free_foundations.artifacts.metadata import write_json
from free_foundations.encoders.backends import cache as state_cache
from free_foundations.encoders.backends.checkpoints import expected as checkpoint_expected
from free_foundations.encoders.backends.encoding import foundation_states
from free_foundations.study.representations import provenance as origins
from free_foundations.study.spec import (
    StudySpec,
    digest_json,
    file_hash,
    panel_contract,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    import pandas as pd

    from free_foundations.encoders.context import Prepared


from free_foundations.study.representations.arrays import _save_states, _validate_embeddings
from free_foundations.study.representations.contexts import _contexts, load_contexts


def feature_blocks(data: Prepared, width: int) -> list[Prepared]:
    """Partition every ordered column exactly once, without random feature subsampling."""
    if width < 1:
        message = "Block width must be positive."
        raise ValueError(message)
    blocks = []
    for start in range(0, len(data.features), width):
        stop = min(start + width, len(data.features))
        blocks.append(
            replace(
                data,
                support=data.support[:, start:stop],
                query=data.query[:, start:stop],
                features=data.features[start:stop],
                digest=digest_json({"parent": data.digest, "columns": [start, stop]}),
            )
        )
    if tuple(name for block in blocks for name in block.features) != data.features:
        message = "Column partition lost or duplicated source features."
        raise ValueError(message)
    return blocks


def conventional_states(data: Prepared) -> dict[str, np.ndarray]:
    """The direct control: the same features, support-median imputed with indicators.

    Imputation and standardization use the labeled support rows only and fit no
    parameter to returns; the result is a deterministic coordinate system for the
    same information the foundation models receive.
    """
    imputer = SimpleImputer(strategy="median", keep_empty_features=True, add_indicator=True)
    train = imputer.fit_transform(data.support)
    query = imputer.transform(data.query)
    scaler = StandardScaler().fit(train)
    return {"direct": np.asarray(scaler.transform(query), dtype=float)}


def _foundation_blocks(
    blocks: list[Prepared], model: str, models: tuple[Path, Path], contracts: list[dict[str, Any]]
) -> np.ndarray:
    pieces = []
    for block in blocks:
        # Use the same identity calculation as foundation_states; approved metadata
        # suffices here because its existing resolver verifies the actual weight bytes.
        identity = (
            state_cache.identity(block, model, checkpoint_expected(model))
            if model in state_cache.RUNTIMES
            else None
        )
        readouts = foundation_states(block, model, *models)
        values = np.asarray(readouts.get("late"), dtype=float)
        _validate_embeddings(values, len(block.tickers))
        pieces.append(values)
        contracts.append(
            {
                "context_digest": block.digest,
                "cache_contract_sha256": digest_json(identity) if identity is not None else None,
                "execution": identity["execution"] if identity is not None else None,
            }
        )
    return np.concatenate(pieces, axis=1)


def _unavailable_context(common: dict[str, Any]) -> dict[str, Any]:
    return common | {
        "status": "training_context_unavailable",
        "reason": "fewer_than_two_observed_past_context_labels",
    }


def encode_panel(  # noqa: PLR0913 -- matched source/context/model availability ledger.
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    broad: pd.DataFrame | Path,
    spec: StudySpec,
    output: Path,
    *,
    weights: Path,
    states_cache: Path,
    input_digest: str | None = None,
    only_rung: str | None = None,
    only_model: str | None = None,
    context_root: Path | None = None,
) -> None:
    """Extract all declared states; unsupported cells are statuses, never smaller cohorts.

    Quarters before the panel start are context only: they supply labeled support
    rows but no query states, because no analysis reads them.
    """
    rungs = spec.rungs if only_rung is None else (only_rung,)
    contexts = (
        _contexts(panel, characteristics, broad, spec, rungs)
        if context_root is None
        else load_contexts(context_root, rungs, input_digest)
    )
    write_states(
        contexts,
        spec,
        output,
        contract=panel_contract(panel, spec),
        weights=weights,
        states_cache=states_cache,
        input_digest=input_digest,
        only_model=only_model,
    )


def write_states(  # noqa: PLR0913 -- state extraction inputs and provenance.
    contexts: Iterator[tuple[str, str, Prepared | None]],
    spec: StudySpec,
    output: Path,
    *,
    contract: dict[str, Any],
    weights: Path,
    states_cache: Path,
    input_digest: str | None,
    only_model: str | None,
) -> None:
    """Extract the requested readouts from verified, ordered contexts."""
    output.mkdir(parents=True, exist_ok=True)
    models = (
        spec.models if only_model is None else (() if only_model == "direct" else (only_model,))
    )
    direct = only_model in {None, "direct"}
    expected = set(models) | ({"direct"} if direct else set())
    if not set(models).issubset(spec.models):
        message = "Unknown representation rung or model."
        raise ValueError(message)
    provenance = {
        "implementation": origins.implementation(spec),
        "runtimes": origins.runtime(spec),
    }
    provenance_digest = digest_json(provenance)
    records: list[dict[str, Any]] = []
    for quarter, rung, data in contexts:
        common = {
            "quarter": quarter,
            "master": contract,
            "input_digest": input_digest,
            "provenance_sha256": provenance_digest,
            "rung": rung,
        }
        if data is None:
            records.append(_unavailable_context(common))
            continue
        blocks = feature_blocks(data, spec.block_columns)
        path = output / quarter / rung
        path.mkdir(parents=True, exist_ok=True)
        context = common | {
            "context_digest": data.digest,
            "support_ids": data.support_ids,
            "issuer_ids": data.tickers,
            "features": data.features,
            "blocks": [list(block.features) for block in blocks],
            "preprocessing": "native NA for foundation models; support-only controls",
            "available_at": data.available_at.isoformat() if data.available_at else None,
            "provenance": provenance,
        }
        write_json(path / "context.json", context)
        states: dict[str, np.ndarray] = {}
        try:
            states = conventional_states(data) if direct else {}
            for values in states.values():
                _validate_embeddings(values, len(data.tickers))
        except (ImportError, ValueError, RuntimeError, OSError) as error:
            states = {}
            records.append(
                common
                | {
                    "model": "controls",
                    "status": "model_rung_unavailable",
                    "reason": str(error),
                    "context_digest": data.digest,
                }
            )
        native_contracts: dict[str, list[dict[str, Any]]] = {}
        for model in models:
            try:
                model_contracts: list[dict[str, Any]] = []
                states[model] = _foundation_blocks(
                    blocks, model, (weights, states_cache), model_contracts
                )
                native_contracts[model] = model_contracts
            except (ImportError, ValueError, RuntimeError, OSError) as error:
                records.append(
                    common
                    | {
                        "model": model,
                        "status": "model_rung_unavailable",
                        "reason": str(error),
                        "context_digest": data.digest,
                    }
                )
        destination = path / "states.npz"
        _save_states(destination, states)
        record = context | {
            "status": "complete" if expected.issubset(states) else "incomplete",
            "models": sorted(states),
            "sha256": file_hash(destination),
            "path": str(destination.relative_to(output)),
            "native_cache_contracts": native_contracts,
        }
        write_json(path / "manifest.json", record)
        records.append(record)
    available = any("path" in record and record["models"] for record in records)
    complete = bool(records) and all(record["status"] == "complete" for record in records)
    status = "complete" if complete else "incomplete" if available else "unavailable"
    write_json(
        output / "manifest.json",
        {
            "master": contract,
            "status": status,
            "states": records,
            "relative_paths": True,
            "input_digest": input_digest,
            "provenance": provenance,
            "provenance_sha256": provenance_digest,
        },
    )
