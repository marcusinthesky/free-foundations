# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = ["secretspec==0.14.0", "wrds==3.4.0"]
# ///
"""Review which WRDS libraries and study-relevant tables this account can read.

Credentials resolve per command through the ``wrds`` secretspec profile and are
never printed or written. Only library names, table names and row-free probes
(``LIMIT 0``) are recorded, so no licensed data leaves WRDS.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from secretspec import SecretSpec, SecretSpecError

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "dvc.yaml").is_file())
# Tables that could replace or extend the CRSP extract and SEC CompanyFacts.
PROBES = {
    "crsp_monthly_ciz": "crsp.msf_v2",
    "crsp_daily_ciz": "crsp.dsf_v2",
    "crsp_monthly_legacy": "crsp.msf",
    "crsp_daily_legacy": "crsp.dsf",
    "crsp_delisting_legacy": "crsp.msedelist",
    "crsp_security_history_ciz": "crsp.stksecurityinfohist",
    "crsp_annual_monthly_ciz": "crsp_a_stock.msf_v2",
    "crsp_annual_daily_ciz": "crsp_a_stock.dsf_v2",
    "ccm_link_history": "crsp.ccmxpf_lnkhist",
    "ccm_link_history_annual": "crsp_a_ccm.ccmxpf_lnkhist",
    "compustat_annual": "comp.funda",
    "compustat_quarterly": "comp.fundq",
    "compustat_company": "comp.company",
    "compustat_security_monthly": "comp.secm",
    "compustat_annual_na": "comp_na_daily_all.funda",
    "compustat_snapshot_annual": "comp_snapshot.wrds_csa_unrestated",
    "fama_french_monthly": "ff.factors_monthly",
    "ibes_summary": "ibes.statsum_epsus",
    "wrds_sec_link": "wrdssec.wciklink_gvkey",
    "wrds_sec_filings": "wrdssec.wrds_forms",
}


def credentials() -> tuple[str, str]:
    """Resolve the WRDS profile without exposing either value."""
    try:
        with (
            SecretSpec.builder()
            .with_path(str(ROOT / "secretspec.toml"))
            .with_profile("wrds")
            .with_reason("Review WRDS library access for the Free Foundations study")
            .load() as resolved
        ):
            return (
                resolved.secrets["WRDS_USERNAME"].get,
                resolved.secrets["WRDS_PASSWORD"].get,
            )
    except SecretSpecError as error:
        sys.exit(f"SecretSpec could not resolve the wrds profile: {type(error).__name__}")


def main() -> None:
    """Connect once, list readable libraries and probe study tables with LIMIT 0."""
    import wrds  # noqa: PLC0415 -- the connection library is only needed here.

    username, password = credentials()
    connection = wrds.Connection(wrds_username=username, wrds_password=password, autoconnect=True)
    try:
        libraries = sorted(connection.list_libraries())
        probes = {}
        for name, table in PROBES.items():
            try:
                connection.raw_sql(f"SELECT * FROM {table} LIMIT 0")  # noqa: S608 -- fixed names.
            except Exception as error:  # noqa: BLE001 -- record the access outcome.
                probes[name] = {"table": table, "readable": False, "error": type(error).__name__}
            else:
                probes[name] = {"table": table, "readable": True}
    finally:
        connection.close()
    report = {"libraries": libraries, "probes": probes}
    destination = ROOT / ".context/tmp/wrds-access.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
