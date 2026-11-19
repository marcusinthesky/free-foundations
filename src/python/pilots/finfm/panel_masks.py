"""Verify the quarterly mask and frozen-state row mapping without fitting a model."""

import hashlib
import json
from pathlib import Path

import pandas as pd

from free_foundations.artifacts.hashes import file_hash

processed = Path("data/processed/crsp-sec")
saved = Path("data/research/crsp-sec/experiments/comovement/summary")
panel_file = processed / "panel/panel.parquet"
panel_manifest = json.loads((processed / "panel/manifest.json").read_text())
state_manifest = json.loads((processed / "representations/manifest.json").read_text())
assert file_hash(panel_file) == panel_manifest["files"]["panel.parquet"]

panel = pd.read_parquet(panel_file, columns=["quarter", "issuer_id", "observed", "total_return"])
betas = pd.read_parquet(saved / "betas.parquet").set_index("ticker")["mm_beta"]
ledger = pd.read_parquet(saved / "ledger.parquet").dropna(subset=["quarter"]).set_index("quarter")
calendar = pd.to_datetime(json.loads((saved / "manifest.json").read_text())["calendar"])
assert len(calendar) == len(ledger) == 60
formed = {
    pd.Timestamp(state["quarter"]): state
    for state in state_manifest["states"]
    if state["rung"] == "fernandez"
}

records = []
for quarter in calendar:
    formation = pd.Timestamp(year=quarter.year, month=3, day=31)
    state = formed[formation]
    assert {"direct", "tabpfn_full"} <= set(state["models"])
    annual_ids = set(panel.loc[panel["quarter"].eq(formation), "issuer_id"])
    assert annual_ids == set(state["issuer_ids"])
    rows = panel.loc[panel["quarter"].eq(quarter)].sort_values("issuer_id")
    keep = rows["observed"] & rows["issuer_id"].map(betas).notna() & rows["issuer_id"].isin(annual_ids)
    selected = rows.loc[keep]
    ids = selected["issuer_id"].tolist()
    assert len(ids) == len(set(ids)) == ledger.loc[quarter, "issuers"]
    assert selected["total_return"].notna().all()
    records.append(
        {
            "quarter": quarter.date().isoformat(),
            "issuers": len(ids),
            "ordered_mask_sha256": hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
        }
    )

assert sum(row["issuers"] for row in records) == 54906
print(json.dumps(records, indent=2))
