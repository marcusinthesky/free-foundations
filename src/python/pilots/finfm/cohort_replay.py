"""Replay the December 2015 cohort against the frozen prepared tables."""

import json
from pathlib import Path

import pandas as pd

from free_foundations.artifacts.hashes import file_hash
from free_foundations.study.sources.crsp import _issuer_monthly, _membership, _quarterly, _source
from free_foundations.study.spec import StudySpec, frame_digest

sources = Path("data/raw/crsp-sec")
prepared = Path("data/processed/crsp-sec/panel")
manifest = json.loads((prepared / "manifest.json").read_text())
frozen = json.loads((sources / "manifest.json").read_text())
raw = sources / "crsp.csv"
assert file_hash(raw) == manifest["source_crsp_sha256"] == frozen["crsp_sha256"]
for name in ("membership", "cohorts", "panel", "population", "characteristics", "factors"):
    filename = f"{name}.parquet"
    assert file_hash(prepared / filename) == manifest["files"][filename]

spec = StudySpec.read()
source = _source(raw, spec)
membership = _membership(source, spec)
assert frame_digest(membership) == frame_digest(pd.read_parquet(prepared / "membership.parquet"))
formation = membership.loc[membership["formation_year"].eq(2015)]
monthly = _issuer_monthly(source, formation, spec, cohort=True)
quarterly = _quarterly(monthly)
quarterly.insert(0, "formation_year", 2015)

cohorts = pd.read_parquet(prepared / "cohorts.parquet")
assert frame_digest(cohorts) == manifest["cohorts_sha256"]
saved = cohorts.loc[cohorts["formation_year"].eq(2015)].reset_index(drop=True)
assert frame_digest(quarterly) == frame_digest(saved)
print(
    json.dumps(
        {
            "formation": 2015,
            "securities": len(formation),
            "issuers": int(formation["permco"].nunique()),
            "quarters": len(quarterly),
            "observed": int(quarterly["observed"].sum()),
            "cohort_2015_frame_sha256": frame_digest(quarterly),
        },
        indent=2,
    )
)
