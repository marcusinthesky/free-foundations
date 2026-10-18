"""Dependence-aware paired uncertainty for daily held-out log-density differences."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from arch.bootstrap import MCS, StationaryBootstrap, optimal_block_length

from free_foundations.panel.design import DESIGNS, SUPPORT_SIZES

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

BLOCKS = (21, 63)  # Declared: one and three trading months of expected block length.
REPLICATES = 9999


def resample_counts(
    days: int, block: int, replicates: int = REPLICATES, seed: int = 42
) -> FloatArray:
    """How often each day appears in each stationary-bootstrap replicate.

    Every comparison reuses the same replicates, so differences remain paired across
    approaches and their bootstrap sums are a single matrix product.
    """
    bootstrap = StationaryBootstrap(block, np.arange(days), seed=seed)
    counts = np.zeros((replicates, days))
    for row, (arguments, _) in enumerate(bootstrap.bootstrap(replicates)):
        counts[row] = np.bincount(arguments[0], minlength=days)
    return counts


def reference_for(column: str) -> dict[str, str]:
    """The joint Fernández benchmark and the uniform network within the same arm."""
    _, _, innovation = column.split("|")
    if innovation == "control":
        return {"joint": "fernandez_joint|exp|diagonal"}
    return {
        "joint": f"fernandez_joint|exp|{innovation}",
        "uniform": f"uniform_network|none|{innovation}",
    }


def paired(daily: pd.DataFrame) -> pd.DataFrame:
    """Summed daily differences with stationary-bootstrap percentile intervals."""
    columns = [column for column in map(str, daily.columns) if "__placebo" not in column]
    counts = {block: resample_counts(len(daily), block) for block in BLOCKS}
    rows = []
    for column in columns:
        for label, reference in reference_for(column).items():
            if reference not in daily or reference == column:
                continue
            difference = (daily[column] - daily[reference]).to_numpy(dtype=float)
            row: dict[str, str | float] = {
                "column": column,
                "versus": label,
                "reference": reference,
                "difference": float(difference.sum()),
                "politis_white_block": float(
                    optimal_block_length(difference)["stationary"].iloc[0]
                ),
            }
            for block, matrix in counts.items():
                sums = matrix @ difference
                row |= {
                    f"lower_{block}": float(np.percentile(sums, 2.5)),
                    f"upper_{block}": float(np.percentile(sums, 97.5)),
                    f"share_nonpositive_{block}": float(np.mean(sums <= 0)),
                }
            rows.append(row)
    return pd.DataFrame(rows)


# Declared matched-input contrasts: (label, left, right) within one rung, kernel and arm.
# "TabFM" is the early-concatenation state readout.
RUNG_CONTRASTS = (
    ("pretrained vs supervised", "tabfm__early_concat", "supervised_mlp16"),
    ("pretrained vs direct", "tabfm__early_concat", "direct"),
    ("pretrained vs Mahalanobis", "tabfm__early_concat", "mahalanobis_lw"),
    ("pretrained vs random autoencoder", "tabfm__early_concat", "random_autoencoder"),
    ("labels vs constant labels", "tabfm__early_concat", "tabfm__early_concat_labelnull"),
)
INPUT_CONTRASTS = ("direct", "tabfm__early_concat")
# Measurement contrasts on the history rung, for one readout per model family and the
# supervised control: support redraw, two shared targets against one, decoded exposures
# against native distance, and decoded states against decoded inputs.
MEASURED = ("tabfm__early_concat", "tabpfn_full__late", "exaone__late", "supervised_mlp16")
MEASUREMENT_CONTRASTS = (
    ("support redraw", "histories@redraw1__{}", "histories__{}"),
    ("support redraw", "histories@redraw2__{}", "histories__{}"),
    ("both targets vs one", "histories@shared_both__{}", "histories@shared_market_cap_assets__{}"),
    ("decoded vs native", "histories@decoded__{}", "histories__{}"),
    ("decoded vs decoded inputs", "histories@decoded__{}", "histories@decoded__direct"),
)
# Support-size contrasts: each pretrained readout against controls without pretraining,
# labels or trained weights, at every nested support size, native and decoded.
SUPPORT_CONTRASTS = (
    ("tabfm__early_concat", "direct"),
    ("tabfm__early_concat", "pca16"),
    ("tabfm__early_concat", "supervised_mlp16"),
    ("tabfm__early_concat", "tabfm__early_concat_labelnull"),
    ("tabpfn_full__late", "direct"),
    ("tabpfn_full__late", "pca16"),
    ("tabpfn_full__late", "supervised_mlp16"),
    ("tabpfn_full__late", "tabpfn_full_random__late"),
)
CONTRAST_ARMS = (("matched", "diagonal"), ("matched", "correlation"), ("median", "diagonal"))


def support_contrasts() -> list[tuple[str, str, str]]:
    """Declared support-size pairs; ``direct`` is query-only, so its 256-row column serves."""
    pairs: list[tuple[str, str, str]] = []
    for rows in (*SUPPORT_SIZES, 256):
        rung = "histories" if rows == 256 else f"histories@support{rows}"
        for kind, suffix in (("native", ""), ("decoded", "@decoded")):
            for left, right in SUPPORT_CONTRASTS:
                base = "histories" if right == "direct" else rung
                for kernel, innovation in CONTRAST_ARMS:
                    pairs.append(
                        (
                            f"support {rows} {kind}",
                            f"{rung}{suffix}__{left}|{kernel}|{innovation}",
                            f"{base}{suffix}__{right}|{kernel}|{innovation}",
                        )
                    )
    return pairs


def declared_contrasts(columns: set[str]) -> list[tuple[str, str, str]]:
    """Every declared contrast whose two columns were scored in this design."""
    pairs: list[tuple[str, str, str]] = []
    for kernel, innovation in CONTRAST_ARMS:

        def column(name: str, kernel: str = kernel, innovation: str = innovation) -> str:
            return f"{name}|{kernel}|{innovation}"

        for rung in ("histories", "broad", "metrics"):
            pairs += [
                (label, column(f"{rung}__{left}"), column(f"{rung}__{right}"))
                for label, left, right in RUNG_CONTRASTS
            ]
            pairs.append(
                ("topology", column(f"{rung}__direct"), f"uniform_network|none|{innovation}")
            )
        pairs += [
            (f"inputs ({name})", column(f"metrics__{name}"), column(f"histories__{name}"))
            for name in INPUT_CONTRASTS
        ]
        pairs += [
            (label, column(left.format(name)), column(right.format(name)))
            for name in MEASURED
            for label, left, right in MEASUREMENT_CONTRASTS
        ]
    if any("@support" in column for column in columns):
        pairs += support_contrasts()
    return [pair for pair in pairs if pair[1] in columns and pair[2] in columns]


def contrasts(daily: pd.DataFrame) -> pd.DataFrame:
    """Direct paired differences for the declared contrasts, with yearly totals.

    Intervals resample realized daily score differences in time blocks. They hold the
    fitted coefficients, networks and the searched specification fixed.
    """
    years = pd.to_datetime(daily.index).year
    counts = {block: resample_counts(len(daily), block) for block in BLOCKS}
    rows = []
    for label, left, right in declared_contrasts(set(map(str, daily.columns))):
        difference = (daily[left] - daily[right]).to_numpy(dtype=float)
        row: dict[str, str | float] = {
            "contrast": label,
            "left": left,
            "right": right,
            "difference": float(difference.sum()),
        }
        row |= {
            f"year_{year}": float(difference[years == year].sum()) for year in sorted(set(years))
        }
        for block, matrix in counts.items():
            sums = matrix @ difference
            row |= {
                f"lower_{block}": float(np.percentile(sums, 2.5)),
                f"upper_{block}": float(np.percentile(sums, 97.5)),
            }
        rows.append(row)
    return pd.DataFrame(rows)


def families(daily: pd.DataFrame) -> dict[str, list[str]]:
    """MCS families: networks within one kernel and innovation arm, with every control.

    Nonspatial covariance controls and the uniform and zero networks enter every family
    of their innovation arm, so a family's set is also a comparison with those benchmarks.
    The heterogeneous-variance controls join the diagonal families.
    """
    groups: dict[str, list[str]] = {}
    for column in map(str, daily.columns):
        name, kernel, innovation = column.split("|")
        if "__placebo" in name:
            continue
        arm = "diagonal" if innovation == "control" else innovation
        kernels = ("exp", "median", "matched") if kernel == "none" else (kernel,)
        for selected in kernels:
            groups.setdefault(f"{arm}|{selected}", []).append(column)
    return groups


def confidence_set(daily: pd.DataFrame, size: float = 0.10) -> pd.DataFrame:
    """Hansen-Lunde-Nason model confidence sets on daily negative log densities."""
    rows = []
    for family, columns in families(daily).items():
        losses = -daily[columns]
        procedure = MCS(
            losses,
            size=size,
            reps=1000,
            block_size=21,
            method="max",
            bootstrap="stationary",
            seed=42,
        )
        procedure.compute()
        included = set(procedure.included)
        pvalues = procedure.pvalues.iloc[:, 0].to_dict()
        rows.extend(
            {
                "family": family,
                "column": column,
                "p_value": float(pvalues[column]),
                "included": column in included,
            }
            for column in columns
        )
    return pd.DataFrame(rows)


def main() -> None:
    """Recompute paired intervals, contrasts and confidence sets from saved daily scores."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--designs", nargs="+", default=list(DESIGNS), choices=list(DESIGNS))
    for name in parser.parse_args().designs:
        output = DESIGNS[name].output
        daily = pd.read_parquet(output / "daily-scores.parquet")
        paired(daily).to_csv(output / "bootstrap.csv", index=False)
        contrasts(daily).to_csv(output / "contrasts.csv", index=False)
        confidence_set(daily).to_csv(output / "mcs.csv", index=False)


if __name__ == "__main__":
    main()
