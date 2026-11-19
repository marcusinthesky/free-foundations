"""Shared labels and display formats for manuscript exhibits."""

import numpy as np

CHARACTERISTIC_LABELS = {
    "market_cap_assets": "Market cap / assets",
    "market_to_book": "Market-to-book",
    "dividend_yield": "Dividend yield",
    "debt_maturity": "Debt maturity",
    "joint": "Joint (RMS)",
}
MODEL_LABELS = {
    "direct": "Direct features",
    "tabpfn_full": "TabPFN 3.5",
    "tabfm": "TabFM 1.1",
    "kumo": "Kumo-Tabular",
    "limix": "LimiX-2",
}
RUNG_LABELS = {"fernandez": "Fernández histories", "standard_xbrl": "CompanyFacts XBRL"}
ESTIMATOR_LABELS = {
    "ols": "OLS",
    "lag_iv": "Spatial lag (2SLS)",
    "lag_ml": "Spatial lag (ML)",
    "error_ml": "Spatial error (ML)",
}


def network_label(name: str) -> str:
    """Human-readable network names used in every table."""
    base, _, construction = name.partition("|")
    prefix, _, suffix = base.partition(":")
    # The Fernández rung shares the "fernandez:" prefix with her characteristic networks.
    if prefix == "fernandez" and suffix in CHARACTERISTIC_LABELS:
        label = f"Fernández: {CHARACTERISTIC_LABELS[suffix]}"
    elif ":" in base:
        label = f"{MODEL_LABELS.get(suffix, suffix)} ({RUNG_LABELS.get(prefix, prefix)})"
    else:
        label = {"size": "Size", "industry": "Industry (SIC-2)", "null": "Permutation null"}.get(
            base, base
        )
    if construction.startswith("knn"):
        label += f", {construction[3:]}-NN"
    if construction.endswith("@contemporaneous"):
        label += ", window-end histories"
    return label


def _escape(value: object) -> str:
    replacements = {
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "á": r"\'a",
        "é": r"\'e",
        "\u2013": "--",
    }
    return "".join(replacements.get(character, character) for character in str(value))


def _number(value: object, digits: int = 3) -> str:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "--"
    return f"{number:.{digits}f}" if np.isfinite(number) else "--"


def _interval(low: object, high: object, digits: int = 3) -> str:
    if _number(low) == "--" or _number(high) == "--":
        return "--"
    return f"[{_number(low, digits)}, {_number(high, digits)}]"
