"""Render saved quarterly results after reconciling their exact master experiment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.data import write_json
from free_foundations.study.source_io import atomic_bytes, atomic_csv
from free_foundations.study.spec import StudySpec, file_hash, frame_digest, panel_contract

if TYPE_CHECKING:
    from numpy.typing import NDArray

STAGES = ("representations", "measurement", "replication")
DISPLAY_COLUMNS = {
    "core": ["quarter", "method", "estimator", "status", "premium_market", "intensity"],
    "decoder_quality": ["quarter", "method", "status", "decoder_r2", "labeled_issuers"],
    "conditional_intervals": [
        "contrast_family",
        "left",
        "right",
        "difference",
        "block_quarters",
        "lower",
        "upper",
        "defined_quarters",
    ],
    "generated_intervals": [
        "quarter",
        "method",
        "estimator",
        "parameter",
        "status",
        "defined_draws",
        "lower",
        "upper",
    ],
    "geometry": [
        "quarter",
        "method",
        "firms",
        "undefined_pairs",
        "identity_shrink",
        "positive_rank",
    ],
    "forecasts": [
        "quarter",
        "method",
        "status",
        "parameter",
        "variance_fallbacks",
        "exposure_fallbacks",
    ],
    "calendar": ["quarter", "firms", "observed_firms", "status"],
}


def _escape(value: object) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "{": r"\{",
        "}": r"\}",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    return "".join(replacements.get(character, character) for character in str(value))


def _table(frame: pd.DataFrame, *, limit: int = 80) -> str:
    """Display a bounded preview; the complete table remains a saved CSV artifact."""
    if frame.empty:
        return "No numerical result is available for this task.\n"
    return frame.head(limit).to_latex(index=False, escape=True, longtable=len(frame) > 25)


def _stage_records(root: Path, master: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for stage in STAGES:
        path = root / stage / "manifest.json"
        if not path.exists():
            records[stage] = {"status": "not_run"}
            continue
        record = json.loads(path.read_text())
        if record.get("master") != master:
            message = f"{stage} used a different roster, clock, outcome mask or specification."
            raise ValueError(message)
        status = record.get("status")
        if stage == "representations" and status is None:
            states = record.get("states", [])
            for state in states:
                if state.get("master") != master:
                    message = "A representation state belongs to a different master experiment."
                    raise ValueError(message)
            status = (
                "complete"
                if states and all(item.get("status") == "complete" for item in states)
                else "incomplete"
            )
        records[stage] = record | {"status": status or "recorded", "sha256": file_hash(path)}
    return records


def _defined_rows(frame: pd.DataFrame, table: str) -> NDArray[np.bool_]:
    field = {
        "core": "premium_market",
        "scores": "score_per_issuer",
        "decoder_quality": "decoder_r2",
    }.get(table)
    defined = np.zeros(len(frame), dtype=bool)
    if field is not None and field in frame:
        defined = np.isfinite(pd.to_numeric(frame[field], errors="coerce").to_numpy(float))
        if "status" in frame:
            defined &= frame["status"].eq("available").to_numpy(bool)
    return defined


def _result_tables(
    root: Path,
    destination: Path,
    records: dict[str, dict[str, Any]],
    master: dict[str, Any],
) -> tuple[list[str], list[dict[str, object]]]:
    """Consume actual saved parquet schemas; perform no estimator fitting or selection."""
    parts: list[str] = []
    inventory: list[dict[str, object]] = []
    for stage in ("replication", "measurement"):
        folder = root / stage
        files = records[stage].get("files", {})
        for name in (*DISPLAY_COLUMNS, "scores", "exposures"):
            if name not in files:
                continue
            filename = files[name]
            path = folder / filename
            if not path.resolve().is_relative_to(folder.resolve()):
                message = "Saved-result path escapes its declared analytical stage."
                raise ValueError(message)
            if not path.exists():
                message = f"Declared saved-result table is missing: {stage}/{name}."
                raise ValueError(message)
            frame = pd.read_parquet(path)
            provenance: dict[str, object] = {
                "stage": stage,
                "table": name,
                "source": str(path),
                "sha256": file_hash(path),
                "rows": len(frame),
                "columns": frame.columns.tolist(),
                "master": master,
            }
            defined = _defined_rows(frame, name)
            provenance["defined_numerical_rows"] = int(defined.sum())
            inventory.append(provenance)
            write_json(destination / f"{stage}-{name}.json", provenance)
            atomic_csv(destination / f"{stage}-{name}.csv", frame)
            if frame.empty:
                continue
            if name == "scores":
                selected = frame.loc[defined]
                summary = (
                    selected.groupby("method", sort=True)
                    .agg(
                        defined_quarters=("quarter", "size"),
                        mean_score_per_issuer=("score_per_issuer", "mean"),
                    )
                    .reset_index()
                )
                summary["calendar_quarters"] = len(master["quarters"])
                atomic_csv(destination / f"{stage}-score-summary.csv", summary)
                parts.extend(
                    [
                        r"\paragraph{Observed quarterly predictive scores}",
                        (
                            "Means use defined scores only; missing quarters remain in the "
                            "saved calendar and intervals."
                        ),
                        _table(summary),
                    ]
                )
            elif name == "exposures":
                counts = (
                    frame.groupby("status", sort=True).size().reset_index(name="issuer_quarters")
                )
                parts.extend([r"\paragraph{Published-factor proxy availability}", _table(counts)])
            else:
                columns = [column for column in DISPLAY_COLUMNS[name] if column in frame]
                parts.extend(
                    [f"\\paragraph{{{_escape(stage + ': ' + name)}}}", _table(frame[columns])]
                )
    return parts, inventory


def _source_recovery(prepared: dict[str, Any]) -> dict[str, Any]:
    """Require affirmative full-source evidence before publishing a completed study."""
    receipt = prepared.get("source_recovery")
    if not isinstance(receipt, dict):
        return {
            "status": "not_evaluated",
            "complete": False,
            "full_xbrl_complete": False,
            "reasons": ["No full-source recovery receipt was saved during preparation."],
        }
    complete = (
        receipt.get("status") == "complete"
        and receipt.get("complete") is True
        and receipt.get("full_xbrl_complete") is True
        and receipt.get("unresolved_linkage_issuer_quarters") == 0
        and receipt.get("originals_pending") == 0
    )
    normalized: dict[str, Any] = {
        "status": "not_evaluated",
        "full_xbrl_complete": False,
        "reasons": [],
    } | receipt
    if normalized["status"] == "complete" and not complete:
        normalized["declared_status"] = "complete"
        normalized["status"] = "incomplete"
    return normalized | {"complete": complete}


def _numerical_availability(inventory: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    counts = {"replication": {"core": 0}, "measurement": {"scores": 0, "decoder_quality": 0}}
    for item in inventory:
        stage, table = str(item["stage"]), str(item["table"])
        if stage in counts and table in counts[stage]:
            counts[stage][table] += int(str(item["defined_numerical_rows"]))
    return counts


def render(root: Path, spec: StudySpec) -> None:
    """Publish only saved results, with explicit unavailable sources and pending claims."""
    destination = root / "publication"
    destination.mkdir(parents=True, exist_ok=True)
    prepared = json.loads((root / "prepared/manifest.json").read_text())
    master = prepared["master"]
    panel = pd.read_parquet(root / "prepared/panel.parquet")
    if master != panel_contract(panel, spec):
        message = "Prepared panel bytes/roster/mask do not match the publication experiment."
        raise ValueError(message)
    population = pd.read_parquet(root / "prepared/population.parquet")
    if prepared.get("population_sha256") != frame_digest(population):
        message = "Population availability ledger changed after preparation."
        raise ValueError(message)
    records = _stage_records(root, master)
    characteristics = pd.read_parquet(root / "prepared/characteristics.parquet")
    coverage = (
        population.groupby("quarter", sort=True)
        .agg(
            population_issuers=("issuer_id", "size"),
            xbrl_issuers=("xbrl_available", "sum"),
            observed_return_issuers=("observed", "sum"),
        )
        .reset_index()
    )
    atomic_csv(destination / "quarterly-coverage.csv", coverage)
    status_rows = population[["xbrl_status"]].rename(columns={"xbrl_status": "status"})
    status_rows["reason"] = population.get("xbrl_reason", pd.Series("", index=population.index))
    sources = (
        status_rows.fillna("not_evaluated")
        .groupby(["status", "reason"], dropna=False)
        .size()
        .reset_index(name="issuer_quarters")
    )
    atomic_csv(destination / "source-availability.csv", sources)
    components = (
        characteristics.groupby(["characteristic", "status"])
        .size()
        .reset_index(name="issuer_quarters")
        if not characteristics.empty
        else pd.DataFrame(columns=["characteristic", "status", "issuer_quarters"])
    )
    atomic_csv(destination / "characteristic-availability.csv", components)
    result_parts, inventory = _result_tables(root, destination, records, master)
    defined_results = sum(int(str(item["defined_numerical_rows"])) for item in inventory)
    numerical = _numerical_availability(inventory)
    required_results = numerical["replication"]["core"], numerical["measurement"]["scores"]
    source_recovery = _source_recovery(prepared)
    complete = all(records[stage]["status"] in {"complete", "available"} for stage in STAGES)
    status = (
        "no_verified_xbrl_panel"
        if master["rows"] == 0
        else "no_defined_empirical_results"
        if complete and not any(required_results)
        else "results_pending"
        if not complete
        else "source_recovery_pending"
        if not source_recovery["complete"]
        else "incomplete_empirical_results"
        if not all(required_results)
        else "complete"
    )
    stage_audits = {
        stage: {
            key: value
            for key, value in records[stage].items()
            if key in {"status", "sha256", "estimator_availability", "tasks"}
        }
        for stage in STAGES
    }
    write_json(
        destination / "claims-audit.json",
        {
            "master": master,
            "status": status,
            "stages": stage_audits,
            "source_statuses": prepared["availability"],
            "source_reasons": prepared.get("availability_reasons", {}),
            "source_recovery": source_recovery,
            "defined_numerical_rows": defined_results,
            "defined_rows_by_task": numerical,
            "claims": {
                "common_population_clock_and_mask": True,
                "sec_source_recovery_complete": source_recovery["complete"],
                "new_empirical_findings_available": status == "complete",
                "terminal_crsp_adjustments_independently_certified": False,
                "complete_issuer_capitalization_independently_certified": False,
                "historically_available_pretrained_weights": False,
            },
            "historical_current_survivor_results": "archived; not evidence for this experiment",
        },
    )
    parts = [
        r"\section{Matched CRSP--SEC empirical design}\label{sec:chronology}",
        (
            "The frozen archive contains monthly CRSP CIZ total returns for 2001--2025, "
            "compounded once to a common quarterly clock. Annual membership uses the preceding "
            "December's top 1,000 securities. Formation-selected classes are grouped by issuer "
            "and use preceding-month capitalization weights. These selected-class portfolios "
            "need not contain every share class. Terminal-adjustment completeness is not "
            "independently certified by the exported fields."
        ),
        (
            "Every procedure consumes one issuer-quarter roster and the same observed-return "
            "mask. No balanced lifetime sample or complete-case date deletion is imposed. "
            "SEC filing availability determines accounting information; pre-XBRL return "
            "history does not supply unavailable accounting observations."
        ),
        r"\subsection{Source availability and reconciliation}",
        (
            f"The feature-era population has {len(population):,} issuer-quarters; "
            f"the verified XBRL panel has {master['rows']:,}, including "
            f"{master['observed_issuer_quarters']:,} observed return outcomes. "
            "Unresolved identity, missing disclosure and recovery failures retain "
            "separate statuses."
        ),
        _table(sources),
        _table(components),
        r"\subsection{Replication and representation ladder}\label{sec:replication}",
        (
            "The descriptive core uses full-feature-era quarterly CAPM MM betas, median excess "
            "returns, and no second-stage intercept. The four original characteristic histories "
            "define pairwise-overlap Spearman correlations, with ranks recomputed on each "
            "intersection. An unidentified off-diagonal correlation receives neutral value zero. "
            "Original spatial weights use the unshrunk completed distance; identity shrinkage "
            "defines the positive-definite Gram. The matched spatial arm uses unit-chord "
            "distances from exactly that same repaired Gram, with a common geometry-only "
            "effective-neighbour target."
        ),
        (
            "The information ladder comprises original characteristic histories, standard scalar "
            "XBRL facts, and filing-level scalar facts including custom concepts and dimensions. "
            "Native missingness adapters and deterministic full-coverage column blocks are "
            "declared separately from support-imputed conventional controls. Unsupported model "
            "or context cells remain unavailable."
        ),
        r"\subsection{Risk estimation and uncertainty}\label{sec:geometry}",
        (
            "Forecasts use strictly preceding quarters, "
            f"with at most {spec.return_lookback_quarters} "
            "prior quarters of returns. "
            "Published FF5 plus momentum ridge proxies are distinct from structural "
            "latent exposures and from the full-sample descriptive MM betas. Gaussian scores "
            "integrate unobserved returns through covariance marginals. Conditional inference "
            f"uses {spec.bootstrap_draws:,} paired quarterly resamples, expected blocks "
            f"{', '.join(map(str, spec.bootstrap_blocks))} quarters. The generated-beta core "
            f"requests {spec.generated_beta_draws:,} MM reestimates; failed draws "
            "are recorded rather than replaced by selected converged draws."
        ),
        r"\subsection{Current numerical status}",
        (
            f"Saved-result status: \\texttt{{{_escape(status)}}}. "
            f"Full SEC-source recovery: \\texttt{{{_escape(source_recovery['status'])}}}. "
            "Earlier current-survivor results are archived and supply no finding for this study. "
            "Estimator availability and interval completion counts qualify each numerical table."
        ),
    ]
    parts.extend(result_parts)
    target = Path("src/latex/build/crsp-study.tex")
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_bytes(target, ("\n\n".join(parts) + "\n").encode())
    write_json(
        destination / "manifest.json",
        {
            "master": master,
            "status": status,
            "source_recovery": source_recovery,
            "defined_rows_by_task": numerical,
            "saved_results": inventory,
            "tex_sha256": file_hash(target),
            "claims_sha256": file_hash(destination / "claims-audit.json"),
        },
    )
