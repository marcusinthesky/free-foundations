"""Qualify and read independent T08 representation cells."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import numpy as np

from free_foundations.artifacts.metadata import write_json
from free_foundations.encoders.backends import cache as state_cache
from free_foundations.encoders.backends.checkpoints import resolve
from free_foundations.study.representations import provenance
from free_foundations.study.representations.arrays import _save_states, _validate_embeddings
from free_foundations.study.representations.contexts import load_contexts
from free_foundations.study.representations.encoding import (
    _foundation_blocks,
    conventional_states,
    feature_blocks,
)
from free_foundations.study.representations.matched_contexts import RUNGS, select_columns
from free_foundations.study.spec import CHARACTERISTICS, StudySpec, digest_json, file_hash

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    import pandas as pd
    from numpy.typing import NDArray

    from free_foundations.encoders.context import Prepared


@contextmanager
def _device(device: str) -> Iterator[None]:
    previous = os.environ.get("FF_DEVICE")
    os.environ["FF_DEVICE"] = device
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("FF_DEVICE", None)
        else:
            os.environ["FF_DEVICE"] = previous


def _read_payload(
    file: Path, digest: str, model: str, issuer_ids: tuple[str, ...]
) -> NDArray[np.float64]:
    if file_hash(file) != digest:
        message = f"Representation checksum mismatch at {file}."
        raise ValueError(message)
    with np.load(file, allow_pickle=False) as arrays:
        if arrays.files != [model]:
            message = f"Unexpected representation inventory at {file}."
            raise ValueError(message)
        values = np.asarray(arrays[model], dtype=np.float64)
    _validate_embeddings(values, len(issuer_ids))
    return values


def _legacy_manifest(
    root: Path | None, contexts: dict[str, Any]
) -> tuple[str | None, dict[str, dict[str, Any]]]:
    if root is None:
        return None, {}
    manifest_file = root / "manifest.json"
    manifest = json.loads(manifest_file.read_text())
    if (
        digest_json(manifest["provenance"]) != manifest["provenance_sha256"]
        or manifest["master"] != contexts["master"]
        or manifest["input_digest"] != contexts["input_digest"]
    ):
        message = f"Legacy cell belongs to an invalid or different master experiment at {root}."
        raise ValueError(message)
    records = {}
    for row in manifest["states"]:
        if "path" not in row:
            continue
        if row["quarter"] in records or any(
            row[key] != manifest[key] for key in ("master", "input_digest", "provenance_sha256")
        ):
            message = f"Invalid legacy cell record at {root}/{row['quarter']}."
            raise ValueError(message)
        records[row["quarter"]] = row
    return file_hash(manifest_file), records


def _native_contracts(
    blocks: list[Prepared], model: str, checkpoint: dict[str, Any]
) -> list[dict[str, Any]]:
    contracts = [state_cache.identity(block, model, checkpoint) for block in blocks]
    return [
        {
            "context_digest": contract["context_digest"],
            "cache_contract_sha256": digest_json(contract),
            "execution": contract["execution"],
        }
        for contract in contracts
    ]


def _legacy_payload(  # noqa: PLR0913 -- check every identity before archive qualification.
    root: Path,
    record: dict[str, Any],
    data: Prepared,
    rung: str,
    model: str,
    *,
    blocks: list[Prepared],
    native: list[dict[str, Any]],
    direct: NDArray[np.float64] | None,
) -> NDArray[np.float64] | None:
    if (
        record["status"] != "complete"
        or record["rung"] != rung
        or record["models"] != [model]
        or record["context_digest"] != data.digest
        or tuple(record["support_ids"]) != data.support_ids
        or tuple(record["issuer_ids"]) != data.tickers
        or tuple(record["features"]) != data.features
        or record["blocks"] != [list(block.features) for block in blocks]
        or record["available_at"] != (data.available_at.isoformat() if data.available_at else None)
        or record["native_cache_contracts"].get(model, []) != native
    ):
        return None
    values = _read_payload(
        root / record["quarter"] / rung / "states.npz",
        record["sha256"],
        model,
        data.tickers,
    )
    if direct is not None and not np.array_equal(values, direct):
        return None
    return values


def _qualification_inputs(data: Prepared, quarter: str) -> dict[str, Any]:
    return {
        "quarter": quarter,
        "issuer_ids": data.tickers,
        "support_ids": data.support_ids,
        "features": data.features,
        "context_digest": data.digest,
        "preprocessing": data.preprocessing,
        "available_at": data.available_at.isoformat() if data.available_at else None,
    }


def encode_cell(  # noqa: C901, PLR0912, PLR0913, PLR0915 -- independent DVC cell and provenance.
    contexts: Path,
    weights: Path,
    cache: Path,
    output: Path,
    params: Path,
    *,
    rung: str,
    model: str,
    legacy_cell: Path | None = None,
    device: str = "cuda",
    omit: str | None = None,
) -> None:
    """Use verified contexts to qualify archived or freshly extracted states."""
    spec = StudySpec.read(params)
    valid = rung in RUNGS and model in {"direct", *spec.models}
    if not valid or (omit is not None and (omit not in CHARACTERISTICS or rung not in RUNGS[:3])):
        message = f"Undeclared T08 cell {rung}/{model}, omission {omit!r}."
        raise ValueError(message)
    context_file = contexts / "manifest.json"
    context_manifest = json.loads(context_file.read_text())
    if context_manifest["master"]["population_sha256"] != spec.population_digest:
        message = "T08 contexts disagree with the configured master population."
        raise ValueError(message)
    digest = context_manifest["input_digest"]
    legacy_digest, archived = _legacy_manifest(legacy_cell, context_manifest)
    checkpoint = resolve(model, weights, download=False) if model != "direct" else None
    device = device.strip()
    if device != "cpu" and not (device == "cuda" or device.startswith("cuda:")):
        message = f"Unsupported T08 execution device {device!r}."
        raise ValueError(message)
    records = []
    with _device(device):
        for quarter, _, prepared in load_contexts(contexts, (rung,), digest):
            if any(row["quarter"] == quarter for row in records):
                message = f"Duplicate T08 context quarter {quarter}."
                raise ValueError(message)
            if prepared is None:
                records.append(
                    {"quarter": quarter, "status": "unavailable", "reason": "no dated context"}
                )
                continue
            data = prepared if omit is None else select_columns(prepared, omit, omit=True)
            common = _qualification_inputs(data, quarter)
            if not np.isfinite(data.support).any() or not np.isfinite(data.query).any():
                records.append(
                    common
                    | {"status": "unavailable", "reason": "no finite support or query features"}
                )
                continue
            blocks = feature_blocks(prepared, spec.block_columns)
            if omit is not None:
                retained = set(data.features)
                blocks = [
                    block
                    if retained.issuperset(block.features)
                    else select_columns(block, omit, omit=True)
                    for block in blocks
                    if retained.intersection(block.features)
                ]
            direct = conventional_states(data)["direct"] if checkpoint is None else None
            native = _native_contracts(blocks, model, checkpoint) if checkpoint is not None else []
            archived_row = archived.get(quarter)
            reused = (
                _legacy_payload(
                    legacy_cell,
                    archived_row,
                    data,
                    rung,
                    model,
                    blocks=blocks,
                    native=native,
                    direct=direct,
                )
                if legacy_cell is not None and archived_row is not None and omit is None
                else None
            )
            origin = "archive" if reused is not None else "extracted"
            values = reused if reused is not None else direct
            if values is None:
                observed: list[dict[str, Any]] = []
                try:
                    values = _foundation_blocks(blocks, model, (weights, cache), observed)
                except ValueError as error:
                    if not str(error).startswith("Adapter embeddings must "):
                        raise
                    records.append(common | {"status": "unavailable", "reason": str(error)})
                    continue
                if observed != native:
                    message = f"Native execution contract changed during {quarter}/{rung}/{model}."
                    raise ValueError(message)
            _validate_embeddings(values, len(data.tickers))
            destination = output / quarter / "states.npz"
            destination.parent.mkdir(parents=True, exist_ok=True)
            _save_states(destination, {model: values})
            records.append(
                common
                | {
                    "status": "available",
                    "source": origin,
                    "archive_payload_sha256": archived_row["sha256"]
                    if reused is not None and archived_row is not None
                    else None,
                    "sha256": file_hash(destination),
                    "native_cache_contracts": native,
                    "blocks": [list(block.features) for block in blocks],
                    "removed_columns": [
                        name for name in prepared.features if name not in data.features
                    ]
                    if omit is not None
                    else [],
                }
            )
    expected_dates = {
        str(quarter.date()) for quarter in spec.panel_calendar if quarter.quarter == 1
    }
    if {row["quarter"] for row in records} != expected_dates:
        message = f"Qualified T08 cell {rung}/{model} has missing or unexpected quarters."
        raise ValueError(message)
    implementation = provenance.implementation(spec)
    output.mkdir(parents=True, exist_ok=True)
    write_json(
        output / "manifest.json",
        {
            "model": model,
            "rung": rung,
            "omit": omit,
            "device": device if checkpoint is not None else "cpu",
            "readout": "late" if checkpoint is not None else "support-median-indicators-zscore",
            "master": context_manifest["master"],
            "input_digest": digest,
            "contexts_sha256": file_hash(context_file),
            "legacy_cell_sha256": legacy_digest,
            "provenance": {"implementation": implementation, "runtime": provenance.runtime(spec)},
            "states": records,
        },
    )


def load_cell(
    path: Path, quarter: pd.Timestamp, issuers: tuple[str, ...]
) -> NDArray[np.float64] | None:
    """Read one qualified cell and match the requested issuer sequence exactly."""
    manifest = json.loads((path / "manifest.json").read_text())
    date = str(quarter.date())
    records = [row for row in manifest["states"] if row["quarter"] == date]
    if len(records) != 1:
        message = f"Expected one T08 representation record for {date} in {path}."
        raise ValueError(message)
    record = records[0]
    if record["status"] == "unavailable":
        return None
    if record["status"] != "available":
        message = f"Invalid T08 representation status at {path}/{date}."
        raise ValueError(message)
    saved = tuple(record["issuer_ids"])
    positions = {issuer: position for position, issuer in enumerate(saved)}
    if (
        len(positions) != len(saved)
        or len(set(issuers)) != len(issuers)
        or not set(issuers) <= positions.keys()
    ):
        message = f"T08 representation issuer identity mismatch at {path}/{date}."
        raise ValueError(message)
    return _read_payload(path / date / "states.npz", record["sha256"], manifest["model"], saved)[
        [positions[issuer] for issuer in issuers]
    ]
