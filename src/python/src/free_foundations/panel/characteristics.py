"""Annual disclosures and annual-priority characteristic recovery from cached filings."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from free_foundations.data import write_json
from free_foundations.fernandez.characteristics import (
    CHARACTERISTICS,
    debt_maturity_with_audit,
    snapshot_with_audit,
)
from free_foundations.filings import broad_facts, broad_facts_with_rejections, validated_dates
from free_foundations.universe.sources import company_facts

LOGGER = logging.getLogger(__name__)
SOURCE = Path("research/universe/cache")
ROOT = Path("research/panel")
MULTICLASS = {"GOOG", "GOOGL", "BRK-B", "BRK-A", "FOX", "FOXA", "NWS", "NWSA"}
YEARS = tuple(range(2009, 2026))
POLICY = "annual-priority-quarterly-snapshot-and-aligned-debt-v2"
FIRST_THREE = CHARACTERISTICS[:3]


def cache_contract() -> dict[str, object]:
    """Reject old annual-only caches and caches built by different selection code."""
    source_paths = (
        Path(__file__),
        Path(broad_facts.__code__.co_filename),
        Path(snapshot_with_audit.__code__.co_filename),
    )
    inputs = (
        SOURCE.parent / "universe.csv",
        *sorted(SOURCE.glob("market-*.parquet")),
        *sorted((SOURCE / "facts").glob("*.json.gz")),
        ROOT / "cache/market-tail.parquet",
    )
    frozen_digest = hashlib.sha256()
    for path in inputs:
        frozen_digest.update(path.name.encode())
        if path.is_file():
            with path.open("rb") as handle:
                frozen_digest.update(hashlib.file_digest(handle, "sha256").digest())
        else:
            frozen_digest.update(b"missing")
    return {
        "policy": POLICY,
        "years": list(YEARS),
        "maximum_age_days": 550,
        "multiclass_exclusions": sorted(MULTICLASS),
        "universe_tickers": (
            list(pd.read_csv(SOURCE.parent / "universe.csv")["ticker"].astype(str))
            if (SOURCE.parent / "universe.csv").is_file()
            else []
        ),
        "frozen_source_sha256": frozen_digest.hexdigest(),
        "source_sha256": {
            str(path.relative_to(Path(__file__).parents[1])): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in source_paths
        },
    }


def matches_contract(path: Path, contract: dict[str, object]) -> bool:
    """Treat missing, malformed, or differently versioned metadata as a cache miss."""
    try:
        return json.loads(path.read_text()) == contract
    except (FileNotFoundError, ValueError):
        return False


def cached_issuer(ticker: str, contract: dict[str, object]) -> bool:
    """Require every current issuer artifact and its matching source contract."""
    pieces = ROOT / "cache/characteristics"
    names = [f"{ticker}{suffix}.parquet" for suffix in ("", ".audit", ".recovery", ".rejected")]
    return all((pieces / name).is_file() for name in names) and matches_contract(
        pieces / f"{ticker}.json", contract
    )


def cache_ready(contract: dict[str, object], tickers: list[str]) -> bool:
    """Reassemble incomplete or inconsistent aggregate caches from issuer evidence."""
    cache = ROOT / "cache"
    if not all(
        (cache / name).is_file()
        for name in ("four.parquet", "broad.parquet", "characteristic-audit.parquet")
    ) or not matches_contract(cache / "characteristic-contract.json", contract):
        return False
    if not all(cached_issuer(ticker, contract) for ticker in tickers):
        return False
    four = pd.read_parquet(cache / "four.parquet")
    metadata = pd.read_parquet(cache / "characteristic-audit.parquet")[list(CHARACTERISTICS)]
    issuer_ratios = (
        pd.concat(
            [
                pd.read_parquet(
                    cache / "characteristics" / f"{ticker}.parquet",
                    columns=["year", "ticker", *CHARACTERISTICS],
                )
                for ticker in tickers
            ],
            ignore_index=True,
        )
        .set_index(["year", "ticker"])
        .sort_index()
    )
    metadata = metadata.astype(float).replace([np.inf, -np.inf], np.nan)
    issuer_ratios = issuer_ratios.astype(float).replace([np.inf, -np.inf], np.nan)
    return four.equals(metadata) and four.equals(issuer_ratios)


def disclosure_facts_with_rejections(
    payload: dict[str, Any], *, quarterly_instants: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add validated DEI shares and preserve rejected source rows from both namespaces."""
    facts, rejected = broad_facts_with_rejections(payload, quarterly_instants=quarterly_instants)
    shares = payload["facts"].get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
    frame = pd.DataFrame(shares.get("units", {}).get("shares", []))
    if frame.empty:
        return facts, rejected
    frame = frame.reindex(
        columns=list(dict.fromkeys([*frame.columns, "form", "start", "end", "filed"]))
    )
    forms = {"10-K", "10-K/A"}
    if quarterly_instants:
        forms |= {"10-Q", "10-Q/A"}
    frame = frame.loc[frame["form"].isin(forms)].copy()
    frame["tag"] = "EntityCommonStockSharesOutstanding"
    frame["unit"] = "shares"
    frame["concept"] = "dei:EntityCommonStockSharesOutstanding|shares|instant"
    frame["kind"] = "instant"
    frame, rejected_shares = validated_dates(frame, instant_only=True)
    rejected_shares["namespace"] = "dei"
    return concat_records([facts, frame]), concat_records([rejected, rejected_shares])


def disclosure_facts(payload: dict[str, Any], *, quarterly_instants: bool = False) -> pd.DataFrame:
    """Return valid annual or expanded facts, including DEI shares."""
    return disclosure_facts_with_rejections(payload, quarterly_instants=quarterly_instants)[0]


def concat_records(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Avoid empty-frame dtype inference while preserving the all-empty schema."""
    populated = [frame for frame in frames if not frame.empty]
    return pd.concat(populated, ignore_index=True) if populated else frames[0].iloc[:0].copy()


def known_facts(facts: pd.DataFrame, year: int) -> pd.DataFrame:
    """Keep only recent periods actually disclosed by that year's end."""
    cutoff = pd.Timestamp(year, 12, 31)
    return facts.loc[
        (facts["filed"] <= cutoff) & facts["end"].between(cutoff - pd.Timedelta(days=550), cutoff)
    ].copy()


def complete_first_three(values: dict[str, float | str]) -> bool:
    """A quarterly fallback is eligible only as one complete aligned snapshot."""
    return all(np.isfinite(float(values.get(name, np.nan))) for name in FIRST_THREE)


def aligned_debt_recovery(
    strict: dict[str, float | str], evidence: pd.DataFrame, expanded: pd.DataFrame
) -> tuple[dict[str, float | str], pd.DataFrame, bool]:
    """Complete missing debt from observed facts at the unchanged annual balance date."""
    if np.isfinite(float(strict.get("debt_maturity", np.nan))):
        return strict, evidence, False
    period = pd.Timestamp(strict["period_end"])
    aligned = expanded.loc[expanded["kind"].eq("instant") & expanded["end"].eq(period)]
    maturity, debt_evidence = debt_maturity_with_audit(aligned, period)
    if not np.isfinite(maturity) or not debt_evidence["form"].isin(["10-Q", "10-Q/A"]).any():
        return strict, evidence, False
    retained = evidence.loc[~evidence["component"].isin(["debt_noncurrent", "debt_total"])]
    completed = {
        **strict,
        "debt_maturity": maturity,
        "aligned_quarterly_debt_latest_filed": str(debt_evidence["filed"].max().date()),
    }
    return completed, concat_records([retained, debt_evidence]), True


def annual_snapshot(
    annual: pd.DataFrame,
    expanded: pd.DataFrame,
    prices: pd.DataFrame,
    ticker: str,
    year: int,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    """Preserve complete annual ratios; recover all ratios together if incomplete.

    The broad feature inventory and its audit remain annual-only. A separate
    component audit identifies the actual facts used for the selected ratios.
    """
    known = known_facts(annual, year)
    selected = known.sort_values(["end", "filed", "accn"]).drop_duplicates("concept", keep="last")
    selected = selected.assign(year=year, ticker=ticker)
    strict: dict[str, float | str] = {}
    evidence = pd.DataFrame()
    policy = "excluded_multiclass" if ticker in MULTICLASS else "annual_incomplete"
    annual_complete = False
    candidate_complete = False
    aligned_debt_completed = False
    if ticker not in MULTICLASS and not prices.empty:
        strict, evidence = snapshot_with_audit(known.loc[known["kind"].eq("instant")], prices)
        annual_complete = complete_first_three(strict)
        if annual_complete:
            policy = "annual"
            strict, evidence, aligned_debt_completed = aligned_debt_recovery(
                strict, evidence, known_facts(expanded, year)
            )
        else:
            candidate = known_facts(expanded, year)
            recovered, recovery_evidence = snapshot_with_audit(
                candidate.loc[candidate["kind"].eq("instant")], prices
            )
            candidate_complete = complete_first_three(recovered)
            if candidate_complete:
                strict, evidence = recovered, recovery_evidence
                policy = "quarterly_recovery"
    # Keep an explicit schema even when no ratio components could be selected.
    evidence = evidence.reindex(
        columns=[
            *dict.fromkeys(
                [
                    "component",
                    "coefficient",
                    "tag",
                    "unit",
                    "val",
                    "end",
                    "filed",
                    "accn",
                    "form",
                    "concept",
                    "kind",
                    *evidence.columns,
                ]
            )
        ]
    ).assign(
        year=year,
        ticker=ticker,
        source_policy=policy,
        aligned_quarterly_debt_recovery=aligned_debt_completed,
    )
    row = {
        "year": year,
        "ticker": ticker,
        **dict.fromkeys(CHARACTERISTICS, np.nan),
        **strict,
        "source_policy": policy,
        "aligned_quarterly_debt_recovery": aligned_debt_completed,
        "annual_complete_first_three": annual_complete,
        "quarterly_candidate_complete_first_three": candidate_complete,
        **dict(zip(selected["concept"], selected["val"], strict=True)),
    }
    return row, selected, evidence


def markets() -> pd.DataFrame:
    """Reverse all splits through retrieval, including splits after the return sample."""
    cached = sorted(SOURCE.glob("market-*.parquet"))
    raw = pd.concat([pd.read_parquet(path) for path in cached], axis=1)
    tail = ROOT / "cache/market-tail.parquet"
    if not tail.exists():
        message = f"Missing frozen Yahoo snapshot: {tail}. Restore market_metadata with DVC."
        raise FileNotFoundError(message)
    return pd.concat([raw, pd.read_parquet(tail)]).sort_index()


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Save annual inputs and recovered ratios with separate filing audit trails."""
    cache = ROOT / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    contract = cache_contract()
    contract_path = cache / "characteristic-contract.json"
    universe = pd.read_csv(SOURCE.parent / "universe.csv")
    if cache_ready(contract, list(universe["ticker"].astype(str))):
        four = pd.read_parquet(cache / "four.parquet")
        write_recovery_summary(four, contract)
        return four, pd.read_parquet(cache / "broad.parquet")
    market = markets()
    pieces = cache / "characteristics"
    pieces.mkdir(exist_ok=True)
    for number, issuer in enumerate(universe.to_dict("records"), 1):
        ticker = issuer["ticker"]
        path = pieces / f"{ticker}.parquet"
        audit_path = pieces / f"{ticker}.audit.parquet"
        recovery_path = pieces / f"{ticker}.recovery.parquet"
        rejected_path = pieces / f"{ticker}.rejected.parquet"
        issuer_contract_path = pieces / f"{ticker}.json"
        if cached_issuer(str(ticker), contract):
            continue
        payload = company_facts(SOURCE, issuer["cik"], cached_only=True)
        facts = disclosure_facts(payload)
        expanded, rejected = disclosure_facts_with_rejections(payload, quarterly_instants=True)
        prices = pd.DataFrame(market.xs(ticker, level=1, axis=1)).dropna(subset=["Close"]).copy()
        splits = prices["Stock Splits"].fillna(0).replace(0, 1)
        prices["historical_close"] = (
            prices["Close"] * splits.iloc[::-1].cumprod().iloc[::-1] / splits
        )
        prices["trailing_dividends"] = prices["Dividends"].rolling("365D").sum()
        rows: list[dict[str, Any]] = []
        audits: list[pd.DataFrame] = []
        recoveries: list[pd.DataFrame] = []
        for year in YEARS:
            row, selected, recovery = annual_snapshot(facts, expanded, prices, ticker, year)
            rows.append(row)
            audits.append(selected)
            recoveries.append(recovery)
        pd.DataFrame(rows).to_parquet(path, index=False)
        concat_records(audits).to_parquet(audit_path, index=False)
        concat_records(recoveries).to_parquet(recovery_path, index=False)
        rejected.assign(ticker=ticker).to_parquet(rejected_path, index=False)
        write_json(issuer_contract_path, contract)
        if number % 50 == 0:
            LOGGER.info("Full characteristics: %s / %s", number, len(universe))
    result = assemble(universe)
    write_json(contract_path, contract)
    write_recovery_summary(result[0], contract)
    return result


def assemble(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assemble issuer snapshots into one allocation, avoiding a wide-frame concat spike."""
    cache = ROOT / "cache"
    paths = [cache / "characteristics" / f"{ticker}.parquet" for ticker in universe["ticker"]]
    concepts = sorted(
        {
            name
            for path in paths
            for name in pq.read_schema(path).names
            if name.startswith("us-gaap:")
        }
    )
    positions = {name: number for number, name in enumerate(concepts)}
    lengths = [pq.read_metadata(path).num_rows for path in paths]
    values = np.full((sum(lengths), len(concepts)), np.nan)
    indices: list[tuple[int, str]] = []
    audits = []
    offset = 0
    for path, length in zip(paths, lengths, strict=True):
        frame = pd.read_parquet(path, use_threads=False)
        columns = [name for name in frame.columns if str(name) in positions]
        values[offset : offset + length, [positions[str(name)] for name in columns]] = frame[
            columns
        ].to_numpy(dtype=float)
        offset += length
        indices.extend(zip(frame["year"], frame["ticker"], strict=True))
        audits.append(frame[[name for name in frame if str(name) not in positions]])
    index = pd.MultiIndex.from_tuples(indices, names=["year", "ticker"])
    broad = pd.DataFrame(values, index=index, columns=concepts).sort_index()
    audit = pd.concat(audits, ignore_index=True).set_index(["year", "ticker"]).sort_index()
    audit.to_parquet(cache / "characteristic-audit.parquet")
    four = audit[list(CHARACTERISTICS)].astype(float).replace([np.inf, -np.inf], np.nan)
    four.to_parquet(cache / "four.parquet")
    broad.to_parquet(cache / "broad.parquet")
    four.notna().groupby("year").sum().to_csv(ROOT / "characteristic-coverage.csv")
    return four, broad


def audit_component_arithmetic(values: pd.DataFrame, row: pd.Series, path: Path) -> None:
    """Reconstruct component scalars and all four ratios from retained evidence."""
    scalars: dict[str, float] = {}
    for component, parts in values.groupby("component", sort=False):
        reported = parts["component_value"].to_numpy(dtype=float)
        scalar = reported[0]
        if not np.allclose(reported, scalar, equal_nan=True):
            message = f"Inconsistent component arithmetic: {path}"
            raise ValueError(message)
        if np.isfinite(scalar):
            terms = parts[["coefficient", "val"]].to_numpy(dtype=float)
            if not np.isfinite(terms).all():
                message = f"Finite ratio component has missing or invalid fact evidence: {path}"
                raise ValueError(message)
            reconstructed = float(terms[:, 0] @ terms[:, 1])
            if not np.isclose(scalar, reconstructed, rtol=1e-12, atol=1e-12):
                message = f"Selected fact values and ratio components disagree: {path}"
                raise ValueError(message)
        scalars[str(component)] = scalar
    cap = scalars.get("shares", np.nan) * float(row["market_historical_close"])
    assets = scalars.get("assets", np.nan)
    equity = scalars.get("equity", np.nan)
    long_debt = scalars.get("debt_noncurrent", np.nan)
    total_debt = scalars.get("debt_total", np.nan)
    expected = [
        cap / assets if assets > 0 else np.nan,
        cap / equity if equity > 0 else np.nan,
        float(row["trailing_dividends"]) / float(row["market_close"]),
        long_debt / total_debt if total_debt > 0 and 0 <= long_debt <= total_debt else np.nan,
    ]
    if not np.allclose(
        row[list(CHARACTERISTICS)].to_numpy(dtype=float),
        expected,
        rtol=1e-12,
        atol=1e-12,
        equal_nan=True,
    ):
        message = f"Selected ratio values and component audit disagree: {path}"
        raise ValueError(message)


def audit_ratio_components(wide: pd.DataFrame, path: Path) -> tuple[int, int]:
    """Validate selected ratio evidence separately from annual feature disclosures."""
    if "source_policy" not in wide:
        return 0, 0
    if not path.is_file():
        message = f"Missing characteristic component audit record: {path}"
        raise ValueError(message)
    frame = pd.read_parquet(path, use_threads=False)
    if frame.empty:
        if wide[list(FIRST_THREE)].notna().any(axis=None):
            message = f"Missing selected ratio components: {path}"
            raise ValueError(message)
        return 0, 0
    cutoff = pd.to_datetime(frame["year"].astype(str) + "-12-31")
    quarterly = frame["form"].isin(["10-Q", "10-Q/A"])
    aligned_debt = (
        frame["aligned_quarterly_debt_recovery"]
        & frame["source_policy"].eq("annual")
        & frame["component"].isin(["debt_noncurrent", "debt_total"])
    )
    valid = (
        frame["filed"].le(cutoff)
        & frame["end"].le(cutoff)
        & (cutoff - frame["end"]).dt.days.le(550)
        & frame["form"].isin(["10-K", "10-K/A", "10-Q", "10-Q/A"])
        & frame["kind"].eq("instant")
        & (~quarterly | frame["source_policy"].eq("quarterly_recovery") | aligned_debt)
    )
    if not valid.all():
        message = f"Invalid point-in-time ratio component selection: {path}"
        raise ValueError(message)
    expected_keys = wide.loc[wide[list(CHARACTERISTICS)].notna().any(axis=1), ["year", "ticker"]]
    observed_keys = frame[["year", "ticker"]].drop_duplicates()
    unmatched_keys = expected_keys.merge(observed_keys, how="left", indicator=True)
    if unmatched_keys["_merge"].ne("both").any():
        message = f"Missing selected ratio components: {path}"
        raise ValueError(message)
    metadata = wide[
        ["year", "ticker", "source_policy", "period_end", "aligned_quarterly_debt_recovery"]
    ]
    linked = frame.merge(
        metadata, on=["year", "ticker"], validate="many_to_one", suffixes=("", "_wide")
    )
    policies_match = (
        linked["source_policy"].eq(linked["source_policy_wide"])
        & linked["aligned_quarterly_debt_recovery"].eq(
            linked["aligned_quarterly_debt_recovery_wide"]
        )
    ).all()
    if len(linked) != len(frame) or not policies_match:
        message = f"Ratio component audit and selected snapshot disagree: {path}"
        raise ValueError(message)
    balance = linked["component"].ne("shares")
    if not linked.loc[balance, "end"].eq(pd.to_datetime(linked.loc[balance, "period_end"])).all():
        message = f"Misaligned balance-sheet ratio components: {path}"
        raise ValueError(message)
    # The selected facts may differ from the latest-per-concept annual feature
    # inventory. Reconstruct each scalar from its own original fact evidence.
    for (year, ticker), values in linked.groupby(["year", "ticker"], sort=False):
        row = wide.loc[wide["year"].eq(int(str(year))) & wide["ticker"].eq(str(ticker))].iloc[0]
        audit_component_arithmetic(values, row, path)
    return len(frame), int(quarterly.sum())


def write_recovery_summary(four: pd.DataFrame, contract: dict[str, object]) -> None:
    """Publish current coverage and source-policy counts without a baked-in old sample."""
    cache = ROOT / "cache"
    audit = pd.read_parquet(cache / "characteristic-audit.parquet")
    evidence = concat_records(
        [
            pd.read_parquet(
                path,
                columns=[
                    "year",
                    "ticker",
                    "component",
                    "tag",
                    "form",
                    "aligned_quarterly_debt_recovery",
                ],
            )
            for path in [
                cache / "characteristics" / f"{ticker}.recovery.parquet"
                for ticker in four.index.get_level_values("ticker").unique()
            ]
        ]
    )
    rejected = concat_records(
        [
            pd.read_parquet(path, columns=["namespace", "rejection_reason"])
            for path in [
                cache / "characteristics" / f"{ticker}.rejected.parquet"
                for ticker in four.index.get_level_values("ticker").unique()
            ]
        ]
    )
    by_year: dict[str, object] = {}
    for year, values in four.groupby("year"):
        metadata = audit.xs(year, level="year")
        by_year[str(year)] = {
            "snapshots": len(values),
            "complete_first_three": int(values[list(FIRST_THREE)].notna().all(axis=1).sum()),
            "annual_complete_first_three": int(metadata["annual_complete_first_three"].sum()),
            "quarterly_recovered_snapshots": int(
                metadata["source_policy"].eq("quarterly_recovery").sum()
            ),
            "aligned_quarterly_debt_recovered_snapshots": int(
                metadata["aligned_quarterly_debt_recovery"].sum()
            ),
            "available_by_characteristic": {
                str(name): int(number) for name, number in values.notna().sum().items()
            },
            "missing_by_characteristic": {
                str(name): int(number) for name, number in values.isna().sum().items()
            },
        }
    tag_counts = (
        evidence.drop_duplicates(["year", "ticker", "component", "tag"])
        .groupby(["component", "tag"])
        .size()
    )
    write_json(
        ROOT / "source-recovery.json",
        {
            "version": 2,
            "contract": contract,
            "source_years": list(YEARS),
            "annual_forms": ["10-K", "10-K/A"],
            "fallback_forms": ["10-K", "10-K/A", "10-Q", "10-Q/A"],
            "quarterly_facts": "instant only; no quarterly duration facts",
            "preserve_complete_annual_first_three": True,
            "aligned_quarterly_debt_completion": (
                "only missing annual debt; exact selected annual balance date; "
                "all first-three ratios and their dates remain unchanged"
            ),
            "aligned_quarterly_debt_recovered_snapshots": int(
                audit["aligned_quarterly_debt_recovery"].sum()
            ),
            "aligned_quarterly_debt_component_facts": int(
                (
                    evidence["aligned_quarterly_debt_recovery"]
                    & evidence["form"].isin(["10-Q", "10-Q/A"])
                    & evidence["component"].isin(["debt_noncurrent", "debt_total"])
                ).sum()
            ),
            "fallback": (
                "whole snapshot only when the annual first three are incomplete "
                "and the fallback first three are complete"
            ),
            "broad_feature_inventory": "annual filings only; unchanged duration policy",
            "snapshot_rows": len(four),
            "selected_ratio_component_facts": len(evidence),
            "rejected_source_facts": len(rejected),
            "rejected_fact_audit": "cache/characteristics/{ticker}.rejected.parquet",
            "rejection_reason_counts": {
                str(reason): int(number)
                for reason, number in rejected["rejection_reason"]
                .astype("string")
                .str.split("|")
                .explode()
                .value_counts()
                .items()
            },
            "rejected_by_namespace": {
                str(namespace): int(number)
                for namespace, number in rejected["namespace"].value_counts().items()
            },
            "quarterly_ratio_component_facts": int(evidence["form"].isin(["10-Q", "10-Q/A"]).sum()),
            "source_policy_counts": {
                str(name): int(number)
                for name, number in audit["source_policy"].value_counts().items()
            },
            "selected_component_tag_snapshot_counts": {
                f"{component}|{tag}": int(number)
                for component, tag, number in tag_counts.to_frame("count")
                .reset_index()
                .itertuples(index=False, name=None)
            },
            "by_year": by_year,
        },
    )


def audit_rejected_facts(wide: pd.DataFrame, path: Path) -> int:
    """Check that every quarantined record has reproducible date-validation reasons."""
    if "source_policy" not in wide:
        return 0
    if not path.is_file():
        message = f"Missing rejected source-fact audit record: {path}"
        raise ValueError(message)
    rejected = pd.read_parquet(path, use_threads=False)
    if not rejected["namespace"].isin(["us-gaap", "dei"]).all():
        message = f"Unknown rejected source namespace: {path}"
        raise ValueError(message)
    for namespace, frame in rejected.groupby("namespace", sort=False):
        original = frame.assign(
            **{name: frame[f"raw_{name}"] for name in ("start", "end", "filed")}
        )
        accepted, checked = validated_dates(original, instant_only=namespace == "dei")
        if len(accepted) or not frame["rejection_reason"].eq(checked["rejection_reason"]).all():
            message = f"Rejected source facts do not match their validation reasons: {path}"
            raise ValueError(message)
    return len(rejected)


def wide_snapshot_paths() -> list[Path]:
    """Use the contracted active universe, with legacy-fixture discovery as fallback."""
    pieces = ROOT / "cache/characteristics"
    wide_paths = [
        path
        for path in pieces.glob("*.parquet")
        if not path.name.endswith((".audit.parquet", ".recovery.parquet", ".rejected.parquet"))
    ]
    contract_path = ROOT / "cache/characteristic-contract.json"
    if contract_path.is_file():
        tickers = json.loads(contract_path.read_text()).get("universe_tickers")
        if tickers is not None:
            wide_paths = [pieces / f"{ticker}.parquet" for ticker in tickers]
    return wide_paths


def audit_disclosures() -> dict[str, int]:
    """Validate filing timing and agreement between wide snapshots and their audit trail."""
    wide_paths = wide_snapshot_paths()
    if not wide_paths:
        message = "No frozen disclosure snapshots to audit. Restore the preparation inputs."
        raise FileNotFoundError(message)
    for wide_path in wide_paths:
        if not wide_path.with_name(wide_path.stem + ".audit.parquet").is_file():
            message = f"Missing filing audit record: {wide_path}"
            raise ValueError(message)
    selected_facts = 0
    populated_snapshots = 0
    issuers = 0
    annual_states = 0
    recovered_snapshots = 0
    ratio_component_facts = 0
    quarterly_ratio_component_facts = 0
    rejected_source_facts = 0
    aligned_debt_recovered_snapshots = 0
    for wide_path in sorted(wide_paths):
        path = wide_path.with_name(wide_path.stem + ".audit.parquet")
        frame = pd.read_parquet(
            path,
            columns=["year", "filed", "end", "concept", "ticker", "val"],
            use_threads=False,
        )
        cutoff = pd.to_datetime(frame["year"].astype(str) + "-12-31")
        valid = (
            (frame["filed"] <= cutoff)
            & (frame["end"] <= cutoff)
            & ((cutoff - frame["end"]).dt.days <= 550)
        )
        if not valid.all() or frame.duplicated(["year", "ticker", "concept"]).any():
            message = f"Invalid point-in-time fact selection: {path}"
            raise ValueError(message)
        wide = pd.read_parquet(path.with_name(path.name.replace(".audit", "")), use_threads=False)
        concepts = [name for name in wide if str(name).startswith(("us-gaap:", "dei:"))]
        keys = ["year", "ticker", "concept"]
        if wide.duplicated(["year", "ticker"]).any():
            message = f"Duplicate wide snapshots: {path}"
            raise ValueError(message)
        expected = wide.melt(
            id_vars=["year", "ticker"],
            value_vars=concepts,
            var_name="concept",
            value_name="snapshot",
        )
        # Wide tables have structural missing cells for concepts absent in a year.
        # Match every selected audit record (including selected missing values), and
        # reject populated wide cells without an audit key.
        actual = frame[[*keys, "val"]]
        joined = expected.merge(actual, on=keys, how="outer", validate="one_to_one", indicator=True)
        unmatched = (joined["_merge"].eq("left_only") & joined["snapshot"].notna()) | joined[
            "_merge"
        ].eq("right_only")
        both = joined["_merge"].eq("both")
        values_equal = (joined["snapshot"].isna() & joined["val"].isna()) | joined["snapshot"].eq(
            joined["val"]
        )
        if unmatched.any() or not values_equal[both].all():
            message = f"Wide characteristics and filing audit disagree in keys or values: {path}"
            raise ValueError(message)
        component_count, quarterly_count = audit_ratio_components(
            wide, path.with_name(path.name.replace(".audit", ".recovery"))
        )
        ratio_component_facts += component_count
        quarterly_ratio_component_facts += quarterly_count
        rejected_source_facts += audit_rejected_facts(
            wide, path.with_name(path.name.replace(".audit", ".rejected"))
        )
        annual_states += len(wide)
        if "source_policy" in wide:
            recovered_snapshots += int(wide["source_policy"].eq("quarterly_recovery").sum())
            aligned_debt_recovered_snapshots += int(wide["aligned_quarterly_debt_recovery"].sum())
        issuers += 1
        selected_facts += len(frame)
        populated_snapshots += int(frame["year"].nunique())
    return {
        "issuers": issuers,
        "annual_states": annual_states,
        "populated_snapshots": populated_snapshots,
        "candidate_us_gaap_concepts": len(pq.read_schema(ROOT / "cache/broad.parquet").names) - 2,
        "selected_facts": selected_facts,
        "future_filings": 0,
        "future_periods": 0,
        "duplicate_concepts_per_snapshot": 0,
        "maximum_age_days": 550,
        "quarterly_recovered_snapshots": recovered_snapshots,
        "aligned_quarterly_debt_recovered_snapshots": aligned_debt_recovered_snapshots,
        "ratio_component_facts": ratio_component_facts,
        "quarterly_ratio_component_facts": quarterly_ratio_component_facts,
        "rejected_source_facts": rejected_source_facts,
    }
