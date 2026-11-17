"""Prepare once, extract frozen states once, and estimate the retained financial study."""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import asdict, fields
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.data import write_json
from free_foundations.fernandez.characteristics import history_view
from free_foundations.panel.characteristics import ROOT, SOURCE, audit_disclosures, build
from free_foundations.panel.decoding import FACTORS, FOLDS, RANKS, Targets, reliability, targets
from free_foundations.panel.design import (
    CALIBRATION_SIZES,
    FOUNDATION_MODELS,
    FOUNDATION_READOUTS,
    PREPARED,
    PRINCIPAL,
    STATES,
    STUDY,
    SUPPORT_SIZES,
    VALIDATION,
)
from free_foundations.panel.evaluation import (
    CALIBRATION,
    EVALUATION,
    Panel,
    comparison,
    daily_frame,
    update,
)
from free_foundations.panel.inference import BLOCKS, REPLICATES, confidence_set, contrasts, paired
from free_foundations.panel.networks import (
    MODEL_CACHE,
    MODEL_SOURCE,
    classical,
    context,
    distances,
    labels,
    record_context,
)
from free_foundations.panel.observations import Annual, annual_data, price_audit
from free_foundations.panel.validation import SALTS, diagnostic_distances, diagnostic_pairs
from free_foundations.representations.cache import digest_file, identity
from free_foundations.representations.representations import representation_states
from free_foundations.representations.setup import ensure_checkpoints

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
YEARS = (*CALIBRATION, *EVALUATION)
MANIFEST = ROOT / "representation-manifest.json"


def prepared(year: int) -> tuple[Annual, Targets]:
    """Restore annual return windows and shared factor coordinates without refitting."""
    with np.load(PREPARED / f"{year}.npz", allow_pickle=False) as payload:
        values = {field.name: payload[field.name] for field in fields(Annual)}
        values["tickers"] = tuple(map(str, values["tickers"]))
        values["dates"] = tuple(map(str, values["dates"]))
        annual = Annual(**values)
        calibration = Targets(
            reference={rank: payload[f"target_{rank}"] for rank in RANKS},
            covariance=payload["covariance_exposures"],
        )
    return annual, calibration


def prepare() -> None:
    """Audit frozen disclosures and prepare the common annual financial inputs."""
    four, _ = build()
    write_json(ROOT / "disclosure-audit.json", audit_disclosures())
    price_audit(pd.read_parquet(SOURCE / "prices.parquet")).to_csv(
        ROOT / "price-audit.csv", index=False
    )
    PREPARED.mkdir(parents=True, exist_ok=True)
    audit: list[dict[str, object]] = []
    for year in YEARS:
        annual = annual_data(
            four,
            year,
            characteristics=STUDY.characteristics,
            histories=STUDY.cohort_histories,
            output=PREPARED,
        )
        calibration = targets(annual.prior, annual.reference)
        payload = asdict(annual) | {
            f"target_{rank}": value for rank, value in calibration.reference.items()
        }
        payload["covariance_exposures"] = calibration.covariance
        np.savez_compressed(PREPARED / f"{year}.npz", allow_pickle=False, **payload)
        audit.extend(
            {"year": year, **row}
            for rank in RANKS
            for row in reliability(annual.prior, annual.reference, rank)
        )
        LOGGER.info("Prepared %s: %s firms", year, len(annual.tickers))
    pd.DataFrame(audit).to_csv(PREPARED / "target-audit.csv", index=False)


def extraction_sources() -> dict[str, str]:
    """Identify actual representation code, including conventional controls."""
    package = Path(__file__).resolve().parents[1]
    paths = [
        *sorted((package / "representations").glob("*.py")),
        *(
            package / name
            for name in ("encoding.py", "contracts.py", "pooling.py", "registry.py", "runtime.py")
        ),
    ]
    return {str(path.relative_to(package.parents[5])): digest_file(path) for path in paths}


def encode() -> None:
    """Extract the fixed feature inventory; financial estimation never loads models."""
    checkpoints = ensure_checkpoints(
        MODEL_CACHE.parent, ("tabpfn_full", "tabfm", "kumo", "limix"), write_catalogue=False
    )
    four = pd.read_parquet(ROOT / "cache/four.parquet")
    broad = pd.read_parquet(ROOT / "cache/broad.parquet")
    view = history_view(four[list(STUDY.characteristics)], STUDY.history)
    core = labels(four, broad)
    STATES.mkdir(parents=True, exist_ok=True)
    sources = extraction_sources()
    lock = digest_file(Path("src/python/uv.lock"))
    inventory: dict[str, object] = {}
    for year in YEARS:
        annual, _ = prepared(year)
        for support in (256, *SUPPORT_SIZES):
            data = context(view, core, annual.tickers, year, rows=support)
            models = FOUNDATION_MODELS if support == 256 else FOUNDATION_MODELS[:4]
            expected = set(FOUNDATION_READOUTS if support == 256 else PRINCIPAL)
            path = STATES / f"{year}-{support}.npz"
            sidecar = path.with_suffix(".json")
            contract = {
                "year": year,
                "support_rows": support,
                "context_digest": data.digest,
                "tickers": list(annual.tickers),
                "representations": sorted(expected),
                "source_sha256": sources,
                "lock_sha256": lock,
                "model_contracts": {
                    model: identity(data, model, checkpoints[model.partition("_random")[0]])
                    for model in models
                },
            }
            label = "histories" if support == 256 else f"histories@support{support}"
            record_context(STATES / "contexts" / f"{year}-{label}.json", data)
            if path.exists() and sidecar.exists():
                previous = json.loads(sidecar.read_text())
                if previous.get("contract") == contract and previous.get("sha256") == digest_file(
                    path
                ):
                    load_states(year, support)
                    inventory[str(path)] = previous
                    continue
            states = representation_states(
                data, cache=MODEL_CACHE, source=MODEL_SOURCE, models=models
            )
            if set(states) != expected:
                message = (
                    f"Incomplete representation inventory: {year}, {support}, "
                    f"{set(states) ^ expected}"
                )
                raise ValueError(message)
            np.savez_compressed(path, allow_pickle=False, **states)
            record = {
                "contract": contract,
                "sha256": digest_file(path),
                "shapes": {name: list(values.shape) for name, values in states.items()},
            }
            write_json(sidecar, record)
            load_states(year, support)
            inventory[str(path)] = record
            label = "histories" if support == 256 else f"histories@support{support}"
            record_context(STATES / "contexts" / f"{year}-{label}.json", data)
            LOGGER.info("Extracted %s, context %s: %s representations", year, support, len(states))
    write_json(
        MANIFEST,
        {
            "states": inventory,
            "models": FOUNDATION_MODELS,
            "source_sha256": sources,
            "lock_sha256": lock,
            "checkpoint_catalogue_sha256": digest_file(Path("research/model-checkpoints.json")),
        },
    )


def load_states(year: int, support: int = 256) -> dict[str, FloatArray]:
    """Verify frozen feature payloads without importing an inference runtime."""
    path = STATES / f"{year}-{support}.npz"
    record = json.loads(path.with_suffix(".json").read_text())
    expected_inventory = sorted(FOUNDATION_READOUTS if support == 256 else PRINCIPAL)
    contract = record["contract"]
    if (
        contract["year"] != year
        or contract["support_rows"] != support
        or contract["representations"] != expected_inventory
    ):
        message = f"Unexpected representation contract: {path}"
        raise ValueError(message)
    if record["sha256"] != digest_file(path):
        message = f"Representation checksum mismatch: {path}"
        raise ValueError(message)
    with np.load(path, allow_pickle=False) as payload:
        expected = record["contract"]["representations"]
        if sorted(payload.files) != expected:
            message = f"Representation inventory mismatch: {path}"
            raise ValueError(message)
        states = {name: payload[name] for name in payload.files}
    for name, values in states.items():
        if (
            values.ndim != 2
            or values.shape[1] == 0
            or not np.isfinite(values).all()
            or list(values.shape) != record["shapes"][name]
            or values.shape[0] != len(record["contract"]["tickers"])
        ):
            message = f"Invalid feature payload: {path}, {name}"
            raise ValueError(message)
    return states


def validate_extraction(extraction: dict[str, Any]) -> None:
    """Bind every canonical state and context to its manifest and current financial cohort."""
    expected = {
        str(STATES / f"{year}-{support}.npz") for year in YEARS for support in (256, *SUPPORT_SIZES)
    }
    if set(extraction["states"]) != expected:
        message = "Incomplete canonical extraction manifest"
        raise ValueError(message)
    if (
        extraction["models"] != list(FOUNDATION_MODELS)
        or extraction["source_sha256"] != extraction_sources()
        or extraction["lock_sha256"] != digest_file(Path("src/python/uv.lock"))
        or extraction["checkpoint_catalogue_sha256"]
        != digest_file(Path("research/model-checkpoints.json"))
    ):
        message = "Extraction source, dependency or checkpoint identity changed"
        raise ValueError(message)
    four = pd.read_parquet(ROOT / "cache/four.parquet")
    broad = pd.read_parquet(ROOT / "cache/broad.parquet")
    view = history_view(four[list(STUDY.characteristics)], STUDY.history)
    core = labels(four, broad)
    for year in YEARS:
        annual, _ = prepared(year)
        for support in (256, *SUPPORT_SIZES):
            path = STATES / f"{year}-{support}.npz"
            record = extraction["states"][str(path)]
            sidecar = json.loads(path.with_suffix(".json").read_text())
            if sidecar != record or digest_file(path) != record["sha256"]:
                message = f"Feature or sidecar differs from extraction manifest: {path}"
                raise ValueError(message)
            data = context(view, core, annual.tickers, year, rows=support)
            contract = record["contract"]
            label = "histories" if support == 256 else f"histories@support{support}"
            stored = json.loads((STATES / "contexts" / f"{year}-{label}.json").read_text())
            expected_context = {
                "tickers": list(annual.tickers),
                "support_ids": list(data.support_ids),
                "features": list(data.features),
            }
            if (
                contract["context_digest"] != data.digest
                or stored["digest"] != data.digest
                or contract["tickers"] != expected_context["tickers"]
                or any(stored[key] != value for key, value in expected_context.items())
            ):
                message = f"Feature context differs from prepared financial inputs: {path}"
                raise ValueError(message)
            models = FOUNDATION_MODELS if support == 256 else FOUNDATION_MODELS[:4]
            if set(contract["model_contracts"]) != set(models):
                message = f"Incomplete model contracts: {path}"
                raise ValueError(message)
            for model in models:
                model_context = contract["model_contracts"][model]
                if model_context["context_digest"] != data.digest or any(
                    model_context[key] != value for key, value in expected_context.items()
                ):
                    message = (
                        f"Model context differs from prepared financial inputs: {path}, {model}"
                    )
                    raise ValueError(message)
            load_states(year, support)


def financial_sources() -> dict[str, str]:
    """Record the financial implementation separately from frozen representation extraction."""
    package = Path(__file__).resolve().parents[1]
    sources = [
        *sorted((package / "panel").glob("*.py")),
        package / "fernandez/kernels.py",
        package / "fernandez/models.py",
        package / "representations/distance.py",
        package / "data.py",
    ]
    return {str(path.relative_to(package.parents[5])): digest_file(path) for path in sources}


def configuration() -> dict[str, object]:
    """One effective specification, shared by calculation and serialization."""
    return {
        "design": STUDY.name,
        "characteristics": STUDY.characteristics,
        "history_years": STUDY.history,
        "cohort_history_years": STUDY.cohort_histories,
        "models": FOUNDATION_MODELS,
        "representations": FOUNDATION_READOUTS,
        "support_sizes": (*SUPPORT_SIZES, 256),
        "calibration_sizes": CALIBRATION_SIZES,
        "calibration": [2016, 2019],
        "evaluation": [2020, 2025],
        "prior_return_years": 3,
        "minimum_prior_returns": 500,
        "exclude_first_return_each_year": True,
        "support_cap": 256,
        "decoded": {"rank": FACTORS, "folds": FOLDS, "audited_ranks": RANKS},
        "kernels": {
            "matched": "zero diagonal, matched to joint effective neighbors",
            "exp": "original characteristic benchmarks only",
        },
        "innovations": ["diagonal", "correlation"],
        "sample_size_innovations": ["diagonal"],
        "bootstrap": {"expected_blocks": BLOCKS, "replicates": REPLICATES, "seed": 42},
        "mcs": {"size": 0.10, "block": 21, "replicates": 1000, "family": "principal"},
    }


def main() -> None:  # noqa: PLR0915 -- one explicit financial estimation workflow.
    """Estimate principal and diagnostic procedures from the same frozen inputs."""
    extraction = json.loads(MANIFEST.read_text())
    validate_extraction(extraction)
    output = STUDY.output
    output.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)
    for name in ("observations", "contexts"):
        source = PREPARED / name if name == "observations" else STATES / name
        shutil.copytree(source, output / name, dirs_exist_ok=True)
    shutil.copytree(PREPARED / "observations", VALIDATION / "observations", dirs_exist_ok=True)
    four = pd.read_parquet(ROOT / "cache/four.parquet")
    principal, diagnostic = Panel(), Panel()
    quality: list[dict[str, object]] = []
    diagnostic_quality: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []
    firm_days = 0
    for year in YEARS:
        annual, calibration = prepared(year)
        states = load_states(year)
        built = classical(four, year, annual.tickers, STUDY.characteristics, STUDY.history)
        built |= {
            "reference_exposures": pair_distance(calibration.reference[FACTORS]),
            "covariance_exposures": pair_distance(calibration.covariance),
        }
        for support in (256, *SUPPORT_SIZES):
            selected = states if support == 256 else load_states(year, support)
            built |= distances(selected, calibration, annual.tickers, year, support, quality)
        diagnostic_built, rows, null = diagnostic_distances(
            states, calibration.reference[FACTORS], annual.tickers, year
        )
        diagnostic_built["fernandez_joint"] = built["fernandez_joint"]
        diagnostic_quality.extend(rows)
        checks.extend(null)
        LOGGER.info(
            "Financial estimation %s: %s principal, %s diagnostic distances",
            year,
            len(built),
            len(diagnostic_built),
        )
        update(principal, year, annual, built)
        update(diagnostic, year, annual, diagnostic_built)
        if year in EVALUATION:
            firm_days += annual.raw_realized.size
    daily, diagnostic_daily = daily_frame(principal), daily_frame(diagnostic)
    if not daily.index.equals(diagnostic_daily.index):
        message = "Diagnostic dates differ from principal dates"
        raise ValueError(message)
    daily.to_parquet(output / "daily-scores.parquet")
    comparison(principal, daily, firm_days).to_csv(output / "comparison.csv", index=False)
    pd.DataFrame(principal.annual).to_csv(output / "annual-scores.csv", index=False)
    pd.DataFrame(principal.geometry).to_csv(output / "geometry.csv", index=False)
    pd.DataFrame(quality).to_csv(output / "decoding.csv", index=False)
    shutil.copyfile(PREPARED / "target-audit.csv", output / "target-audit.csv")
    LOGGER.info("Paired inference for %s procedures on %s dates", len(daily.columns), len(daily))
    paired(daily).to_csv(output / "bootstrap.csv", index=False)
    contrasts(daily).to_csv(output / "contrasts.csv", index=False)
    confidence_set(daily).to_csv(output / "mcs.csv", index=False)
    diagnostic_daily.to_parquet(VALIDATION / "daily-scores.parquet")
    pd.DataFrame(diagnostic.annual).to_csv(VALIDATION / "annual-scores.csv", index=False)
    pd.DataFrame(
        {
            "column": diagnostic_daily.columns,
            "score": diagnostic_daily.sum().to_numpy(),
            "firm_days": firm_days,
            "dates": len(daily),
        }
    ).to_csv(VALIDATION / "scores.csv", index=False)
    pd.DataFrame(diagnostic_quality).to_csv(VALIDATION / "decoding.csv", index=False)
    pd.DataFrame(checks).to_csv(VALIDATION / "null-checks.csv", index=False)
    contrasts(diagnostic_daily, diagnostic_pairs(set(diagnostic_daily.columns))).to_csv(
        VALIDATION / "contrasts.csv", index=False
    )
    pairs = [
        (
            "calibrated vs native direct",
            f"histories@decoded__{name}|matched|{arm}",
            f"histories__direct|matched|{arm}",
        )
        for name in PRINCIPAL[3:]
        for arm in ("diagonal", "correlation")
    ]
    contrasts(daily, pairs).to_csv(VALIDATION / "principal-contrasts.csv", index=False)
    overlap = []
    for arm in ("diagonal", "correlation"):
        for name in PRINCIPAL:
            left, right = (
                f"fold0@decoded__{name}|matched|{arm}",
                f"histories@decoded__{name}|matched|{arm}",
            )
            error = float(np.abs(diagnostic_daily[left] - daily[right]).max())
            np.testing.assert_allclose(diagnostic_daily[left], daily[right], atol=1e-5, rtol=0)
            overlap.append({"current": left, "previous": right, "max_daily_error": error})
        for suffix in ("", "43", "44"):
            np.testing.assert_allclose(
                diagnostic_daily[f"fold0@decoded__intercept_only|matched|{arm}"],
                daily[f"histories@decoded__kumo_random{suffix}__late|matched|{arm}"],
                atol=1e-5,
                rtol=0,
            )
    write_json(
        VALIDATION / "validation.json",
        {"overlap": overlap, "firm_days": firm_days, "dates": len(daily), "partitions": SALTS},
    )
    write_json(
        VALIDATION / "configuration.json",
        {
            "rank": FACTORS,
            "folds": FOLDS,
            "encoder_support": 256,
            "protocol_sha256": digest_file(VALIDATION / "README.md"),
            "calibration": [2016, 2019],
            "evaluation": [2020, 2025],
            "bootstrap_blocks": BLOCKS,
            "bootstrap_replicates": REPLICATES,
            "bootstrap_seed": 42,
            "partitions": SALTS,
        },
    )
    spec = configuration()
    spec["scored_columns"] = list(daily.columns)
    write_json(output / "configuration.json", spec)
    shutil.copyfile("research/model-checkpoints.json", output / "checkpoints.json")
    names = (
        "daily-scores.parquet",
        "annual-scores.csv",
        "comparison.csv",
        "decoding.csv",
        "target-audit.csv",
        "geometry.csv",
        "bootstrap.csv",
        "contrasts.csv",
        "mcs.csv",
        "configuration.json",
        "checkpoints.json",
    )
    retained = [
        *(output / name for name in names),
        *sorted((output / "observations").glob("*.json")),
        *sorted((output / "contexts").glob("*.json")),
    ]
    write_json(
        output / "manifest.json",
        {
            "sha256": {str(p): digest_file(p) for p in retained},
            "representation_manifest_sha256": digest_file(MANIFEST),
            "source_sha256": financial_sources(),
            "input_sha256": {
                str(path): digest_file(path)
                for path in [
                    *(PREPARED / f"{year}.npz" for year in YEARS),
                    ROOT / "cache/four.parquet",
                    ROOT / "cache/broad.parquet",
                    Path("research/model-checkpoints.json"),
                    Path("src/python/uv.lock"),
                ]
            },
            "configuration": spec,
        },
    )
    LOGGER.info("Completed retained study: %s scored procedures", len(daily.columns))
    from free_foundations.panel import geometry_run  # noqa: PLC0415 -- consume completed scores.

    geometry_run.main()


def pair_distance(values: FloatArray) -> FloatArray:
    """Expose a Euclidean exposure distance without a model runtime."""
    from free_foundations.representations.distance import pairwise_distance  # noqa: PLC0415

    return pairwise_distance(values, metric="euclidean")
