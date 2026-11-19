"""Collect independent frozen readouts into the research representation store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from free_foundations.artifacts.metadata import write_json
from free_foundations.study.representations.arrays import _save_states
from free_foundations.study.spec import StudySpec, digest_json, file_hash


def assemble(parts: Path, output: Path, params: Path) -> None:  # noqa: C901, PLR0912, PLR0915
    """Validate shared provenance and observation order before publishing a manifest."""
    spec = StudySpec.read(params)
    header: dict[str, Any] | None = None
    records = []
    runtimes: dict[str, Any] = {}
    dates: set[str] | None = None
    rosters: dict[str, tuple[list[str], list[str]]] = {}
    for rung in spec.rungs:
        groups: dict[str, list[dict[str, Any]]] = {}
        for model in ("direct", *spec.models):
            source = parts / rung / model / "manifest.json"
            manifest = json.loads(source.read_text())
            current = {
                k: manifest[k]
                for k in ("master", "input_digest", "provenance", "provenance_sha256")
            }
            if digest_json(current["provenance"]) != current["provenance_sha256"]:
                msg = f"Corrupt extraction provenance in {source}"
                raise ValueError(msg)
            quarters = {row["quarter"] for row in manifest["states"]}
            if dates is not None and dates != quarters:
                msg = f"Missing or unexpected quarter in {source}"
                raise ValueError(msg)
            dates = quarters
            runtimes[f"{rung}:{model}"] = current["provenance"]["runtimes"]
            if header is not None and (
                current["master"] != header["master"]
                or current["input_digest"] != header["input_digest"]
                or current["provenance"]["implementation"] != header["provenance"]["implementation"]
            ):
                msg = f"Inconsistent representation input or provenance in {source}"
                raise ValueError(msg)
            header = current
            for record in manifest["states"]:
                if (
                    record["provenance_sha256"] != current["provenance_sha256"]
                    or record["input_digest"] != current["input_digest"]
                    or ("provenance" in record and record["provenance"] != current["provenance"])
                ):
                    msg = f"Cell record belongs to another extraction in {source}"
                    raise ValueError(msg)
                if record["rung"] != rung:
                    msg = f"Unexpected rung in {source}"
                    raise ValueError(msg)
                if "path" not in record:
                    records.append(record)
                    continue
                if set(record["models"]) - {model}:
                    msg = f"Unexpected model in {source}"
                    raise ValueError(msg)
                if manifest.get("relative_paths"):
                    record["path"] = str(source.parent / record["path"])
                groups.setdefault(record["quarter"], []).append(record)
        for quarter, cells in sorted(groups.items()):
            common = cells[0]
            values = {}
            contracts: dict[str, Any] = {}
            for cell in cells:
                roster = cell["support_ids"], cell["issuer_ids"]
                if (
                    rosters.setdefault(quarter, roster) != roster
                    or cell["context_digest"] != common["context_digest"]
                ):
                    msg = f"Inconsistent context at {quarter}/{rung}"
                    raise ValueError(msg)
                path = Path(cell["path"])
                if file_hash(path) != cell["sha256"]:
                    msg = f"State checksum mismatch at {path}"
                    raise ValueError(msg)
                with np.load(path, allow_pickle=False) as arrays:
                    if sorted(arrays.files) != cell["models"] or values.keys() & arrays.files:
                        msg = f"Inconsistent state inventory at {path}"
                        raise ValueError(msg)
                    values.update({key: arrays[key] for key in arrays.files})
                contracts.update(cell["native_cache_contracts"])
            destination = output / quarter / rung / "states.npz"
            destination.parent.mkdir(parents=True, exist_ok=True)
            _save_states(destination, values)
            complete = set(values) == {*spec.models, "direct"}
            records.append(
                common
                | {
                    "models": sorted(values),
                    "native_cache_contracts": contracts,
                    "path": str(destination.relative_to(output)),
                    "sha256": file_hash(destination),
                    "status": "complete" if complete else "incomplete",
                }
            )
    if header is None:
        msg = "The representation inventory is empty."
        raise ValueError(msg)
    output.mkdir(parents=True, exist_ok=True)
    status = (
        "complete" if records and all(r["status"] == "complete" for r in records) else "incomplete"
    )
    if len({digest_json(runtime) for runtime in runtimes.values()}) > 1:
        provenance = header["provenance"] | {"runtimes": runtimes}
        header.update({"provenance": provenance, "provenance_sha256": digest_json(provenance)})
        for row in records:
            row["provenance_sha256"] = header["provenance_sha256"]
            if "provenance" in row:
                row["provenance"] = provenance
    records.sort(key=lambda row: (row["quarter"], spec.rungs.index(row["rung"])))
    write_json(
        output / "manifest.json",
        header | {"states": records, "status": status, "relative_paths": True},
    )
