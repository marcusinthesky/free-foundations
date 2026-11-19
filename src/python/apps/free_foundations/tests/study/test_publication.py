"""The research stages run end to end on a small prepared panel and render a report."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import yaml

from free_foundations.study import alignment, comovement, publication, replication, run
from free_foundations.study.networks import knn_weights, representation_distance
from free_foundations.study.spec import frame_digest, panel_contract
from tests._strategies import compact_spec

if TYPE_CHECKING:
    from pathlib import Path

CHARACTERISTICS = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")
ISSUERS = 40


def _prepared(root: Path) -> tuple[Path, Path]:
    """A verified prepared panel: 40 issuers, two years, SAR returns on a hidden graph."""
    rng = np.random.default_rng(11)
    spec = compact_spec(
        "2008-01-01",
        "2010-12-31",
        window_quarters=8,
        characteristic_history_years=3,
        generated_beta_draws=9,
        likelihood_draws=99,
        mantel_draws=49,
        neighbours=4,
        neighbour_sensitivities=(6,),
        formation_years=(2008,),
        primary_formation=2008,
    )
    params = root / "params.yaml"
    params.write_text(yaml.safe_dump({"study": spec.payload()}))
    issuers = [f"PERMCO:{100 + index}" for index in range(ISSUERS)]
    traits = rng.normal(size=(ISSUERS, 2))
    hidden = knn_weights(representation_distance(traits), 4)
    beta = rng.normal(1.0, 0.3, ISSUERS)
    quarters = pd.date_range("2009-03-31", periods=8, freq="QE")
    market = rng.normal(0.02, 0.08, len(quarters))
    returns = np.array(
        [
            np.linalg.solve(
                np.eye(ISSUERS) - 0.4 * hidden, 0.01 + beta * m + rng.normal(0, 0.05, ISSUERS)
            )
            for m in market
        ]
    )
    returns[2, 0] = np.nan  # One missing quarter stays missing.
    panel = pd.DataFrame(
        [
            {
                "issuer_id": issuer,
                "permco": 100 + index,
                "quarter": quarter,
                "total_return": returns[t, index],
                "observed": bool(np.isfinite(returns[t, index])),
                "sic": ["3571", "3572", "6021", "2834"][index % 4],
            }
            for t, quarter in enumerate(quarters)
            for index, issuer in enumerate(issuers)
        ]
    )
    history = pd.date_range("2006-03-31", "2010-12-31", freq="QE")
    characteristics = pd.DataFrame(
        [
            {
                "issuer_id": issuer,
                "quarter": quarter,
                "characteristic": name,
                "value": float(traits[index, k % 2] * (1 + quarter.year % 3) + rng.normal(0, 0.1)),
            }
            for index, issuer in enumerate(issuers)
            for quarter in history
            for k, name in enumerate(CHARACTERISTICS)
        ]
    )
    cohorts = panel.assign(formation_year=2008)
    factors = pd.DataFrame({"quarter": quarters, "RF": 0.005, "Mkt-RF": market})
    membership = pd.DataFrame(
        [
            {"formation_year": year, "permco": 100 + index, "market_cap_usd": 1e9 * (index + 1)}
            for year in (2008, 2009)
            for index in range(ISSUERS)
        ]
    )
    prepared = root / "panel"
    prepared.mkdir()
    for name, frame in {
        "panel": panel,
        "characteristics": characteristics,
        "factors": factors,
        "cohorts": cohorts,
        "membership": membership,
    }.items():
        frame.to_parquet(prepared / f"{name}.parquet", index=False)
    manifest = {
        "master": panel_contract(panel, spec),
        "cohorts_sha256": frame_digest(cohorts),
        "analytical_issuer_quarters": len(panel),
        "population_issuer_quarters": len(panel),
        "source_recovery": {"unresolved_linkage_issuer_quarters": 0},
        "files": run._inventory(prepared),  # noqa: SLF001 -- the real frozen inventory.
    }
    (prepared / "manifest.json").write_text(json.dumps(manifest))
    return prepared, params


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "label"),
    [
        ("fernandez:joint|exp", "Fernández: Joint (RMS)"),
        (
            "fernandez:market_to_book|exp@contemporaneous",
            "Fernández: Market-to-book, window-end histories",
        ),
        ("fernandez:joint|knn10", "Fernández: Joint (RMS), 10-NN"),
        ("fernandez:direct|knn10", "Direct features (Fernández histories), 10-NN"),
        ("fernandez:tabpfn_full|knn5", "TabPFN 3.5 (Fernández histories), 5-NN"),
        ("standard_xbrl:limix|knn20", "LimiX-2 (CompanyFacts XBRL), 20-NN"),
        ("industry|sic2", "Industry (SIC-2)"),
        ("null|knn10", "Permutation null, 10-NN"),
    ],
)
def test_network_labels_separate_her_characteristics_from_the_fernandez_rung(
    name: str, label: str
) -> None:
    # Arrange: names from the saved replication network table.

    # Act
    result = publication.network_label(name)

    # Assert: a model on her rung is not read as one of her characteristics.
    assert result == label


@pytest.mark.integration
@pytest.mark.slow
def test_research_stages_and_report_run_on_a_small_prepared_panel(tmp_path: Path) -> None:
    # Arrange
    prepared, params = _prepared(tmp_path)
    results = tmp_path / "research"

    # Act
    replication.run(prepared, None, results / "replication", params)
    comovement.run(prepared, None, results / "comovement", params)
    alignment.run(prepared, None, results / "alignment", params)
    publication.render(
        prepared,
        replication=results / "replication",
        comovement=results / "comovement",
        alignment=results / "alignment",
        output=results / "publication",
        tex=tmp_path / "latex/build/crsp-study.tex",
        params=params,
    )

    # Assert: every layer has estimates, the hidden spatial lag is detected on the
    # matched graph family, and the report cites saved values through macros.
    estimates = pd.read_parquet(results / "replication/estimates.parquet")
    failed = estimates.loc[estimates["status"].ne("available")]
    # Only intercept lag models fail, where a near-uniform W leaves rho unidentified.
    assert (
        not estimates.loc[~estimates["with_intercept"].astype(bool), "status"].ne("available").any()
    )
    assert failed["estimator"].str.startswith("lag").all()
    intervals = pd.read_parquet(results / "replication/intervals.parquet")
    assert 0 < intervals["draws"].max() <= 9
    panels = pd.read_parquet(results / "comovement/estimates.parquet")
    assert {"lag", "error"} <= set(panels["process"])
    assert panels.loc[panels["status"].eq("available"), "spatial"].notna().all()
    mantel = pd.read_parquet(results / "alignment/mantel.parquet")
    assert "fernandez:joint" in set(mantel["network"])
    text = (tmp_path / "latex/build/crsp-study.tex").read_text()
    assert "\\newcommand{\\ffPrimaryIssuers}{40}" in text
    assert "tab:fernandez-without" in text
    metrics = json.loads((results / "publication/metrics.json").read_text())
    assert metrics["primary_issuers"] == ISSUERS
