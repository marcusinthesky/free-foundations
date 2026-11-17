"""SEC evidence fixtures exercise parsing, resumability and unresolved identities."""

import gzip
import json
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import pytest

from free_foundations.study import sec


def test_global_pacing_shares_five_per_second_clock_without_real_sleep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stamps = iter([100.0, 100.0, 100.05, 100.2])
    delays: list[float] = []
    monkeypatch.setattr(sec.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(sec.time, "time", lambda: next(stamps))
    monkeypatch.setattr(sec.time, "sleep", delays.append)
    sec._pace()  # noqa: SLF001 -- verify the shared on-disk request ceiling.
    sec._pace()  # noqa: SLF001 -- second caller must wait for the first caller's timestamp.
    assert delays == [pytest.approx(0.15)]
    clock = tmp_path / f"free-foundations-sec-{sec.os.getuid()}/request-pace"
    assert float(clock.read_text()) == 100.2


def test_original_xbrl_keeps_custom_dimensions_units_and_native_nil() -> None:
    content = b"""<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:us-gaap="http://fasb.org/us-gaap/2024"
      xmlns:acme="https://example.com/acme/2024" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <xbrli:context id="q"><xbrli:entity><xbrli:identifier scheme="https://www.sec.gov/CIK">42</xbrli:identifier>
      <xbrli:segment><xbrldi:explicitMember dimension="acme:StockAxis">acme:ClassA
      </xbrldi:explicitMember>
      </xbrli:segment>
      </xbrli:entity><xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period></xbrli:context>
      <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
      <us-gaap:Assets contextRef="q" unitRef="usd" decimals="-3">100000</us-gaap:Assets>
      <acme:ReportedPolicy contextRef="q">Class A policy</acme:ReportedPolicy>
      <acme:MissingAmount contextRef="q" unitRef="usd" xsi:nil="true" />
      </xbrli:xbrl>"""
    rows = sec.parse_xbrl(content, cik=42, accession="a", filed="2024-02-01")
    assert len(rows) == 3
    amounts = {row["tag"]: row for row in rows}
    assert amounts["Assets"]["value"] == 100000
    assert amounts["Assets"]["unit"] == "USD"
    assert json.loads(amounts["Assets"]["dimensions"]) == {"acme:StockAxis": "acme:ClassA"}
    assert amounts["ReportedPolicy"]["value_type"] == "categorical"
    assert amounts["MissingAmount"]["value"] is None
    assert amounts["MissingAmount"]["status"] == "native_missing"
    assert all(row["accession"] == "a" and row["source_sha256"] for row in rows)


def test_inline_html_scaling_continuation_and_excluded_text() -> None:
    content = b"""<!DOCTYPE html><html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
      xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:acme="https://example.com/acme">
      <head><meta charset="utf-8"></head><body><ix:resources>
      <xbrli:context id="i"><xbrli:entity><xbrli:identifier>42</xbrli:identifier></xbrli:entity>
      <xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period></xbrli:context>
      <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
      </ix:resources><ix:nonFraction name="acme:Cash" contextRef="i" unitRef="usd"
      scale="3" sign="-">1,250</ix:nonFraction>
      <ix:nonNumeric name="acme:Policy" contextRef="i" continuedAt="tail">First
      <ix:exclude>footnote must disappear</ix:exclude></ix:nonNumeric>
      <ix:continuation id="tail">second part</ix:continuation></body></html>"""
    rows = sec.parse_xbrl(content, cik=42)
    assert rows[0]["value"] == -1250000
    assert "second part" in rows[1]["value"]
    assert "footnote" not in rows[1]["value"]


def test_current_ticker_is_only_a_candidate_and_dei_has_no_extrapolation() -> None:
    monthly = pd.DataFrame(
        {
            "permno": [1, 1],
            "permco": [2, 2],
            "ticker": ["ABC", "ABC"],
            "date": ["2022-01-31", "2023-12-29"],
        }
    )
    candidates = {"0": {"ticker": "ABC", "cik_str": 42}}
    facts = pd.DataFrame(
        [
            {
                "tag": "TradingSymbol",
                "concept": "dei:TradingSymbol",
                "value": "ABC",
                "cik": 42,
                "end": "2023-12-31",
                "source_url": "https://www.sec.gov/Archives/x",
                "accession": "a",
            }
        ]
    )
    result = sec.build_crosswalk(monthly, candidates, facts)
    assert set(result["status"]) == {"candidate_only", "verified_observation"}
    verified = result.loc[result["status"].eq("verified_observation")].iloc[0]
    assert verified["effective_from"] == verified["effective_to"] == "2023-12-31"


def test_offline_bootstrap_preserves_old_cache_and_never_uses_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy = tmp_path / "legacy"
    (legacy / "facts").mkdir(parents=True)
    source = legacy / "facts/0000000042.json.gz"
    with gzip.open(source, "wt") as handle:
        json.dump(
            {
                "cik": 42,
                "facts": {
                    "us-gaap": {
                        "Assets": {
                            "units": {
                                "USD": [
                                    {
                                        "val": 100,
                                        "end": "2023-12-31",
                                        "filed": "2024-02-01",
                                        "accn": "a",
                                    },
                                ]
                            }
                        }
                    }
                },
            },
            handle,
        )
    before = source.read_bytes()
    (legacy / "sec-tickers.json").write_text(json.dumps({"0": {"ticker": "ABC", "cik_str": 42}}))

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Offline initialization made a network request.")

    monkeypatch.setattr(httpx, "get", forbidden)
    monthly = pd.DataFrame(
        {"permno": [1], "permco": [2], "ticker": ["ABC"], "date": ["2024-03-28"]}
    )
    result = sec.acquire_sources(monthly, tmp_path / "new", None, legacy, offline=True)
    assert result["status"] == "pending_network"
    assert result["native_facts"] == 1
    assert source.read_bytes() == before
    assert (tmp_path / "new/sec/companyfacts/0000000042.json.gz").is_file()
    assert not result["identity_available"]


def test_http_failure_is_retryable_and_distinct_from_absence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = [httpx.Response(403), httpx.Response(200, content=b'{"ok":true}')]

    def no_sleep(_delay: float) -> None:
        return None

    def respond(*_args: object, **_kwargs: object) -> httpx.Response:
        return responses.pop(0)

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Cache hit used network.")

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(sec.time, "sleep", no_sleep)
    monkeypatch.setattr(httpx, "get", respond)
    client = sec.SECClient("Researcher researcher@example.edu")
    target = tmp_path / "response.json"
    assert client.json("https://data.sec.gov/test", target) == {"ok": True}
    assert client.records[-1]["status"] == "acquired"
    assert target.is_file()
    monkeypatch.setattr(httpx, "get", forbidden)
    assert client.json("https://data.sec.gov/test", target) == {"ok": True}


def test_three_denied_endpoints_block_only_their_host(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def respond(url: str, **_kwargs: object) -> httpx.Response:
        calls.append(url)
        return httpx.Response(403 if "www.sec.gov" in url else 200, content=b"{}")

    def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(sec.time, "sleep", no_sleep)
    monkeypatch.setattr(httpx, "get", respond)
    client = sec.SECClient("Researcher researcher@example.edu")
    for index in range(4):
        client.fetch(f"https://www.sec.gov/Archives/{index}", tmp_path / f"{index}.xml")
    assert len(calls) == 12
    assert client.records[-1]["status"] == "blocked_host"
    assert client.json("https://data.sec.gov/allowed", tmp_path / "allowed.json") == {}


def _monthly() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "permno": [1, 1, 3, 3],
            "permco": [2, 2, 4, 4],
            "ticker": ["ABC", "ABC", "DEF", "DEF"],
            "date": ["2001-01-31", "2024-12-31", "2001-01-31", "2024-12-31"],
        }
    )


def _submissions(cik: int) -> dict[str, Any]:
    if cik == 126:
        return {"filings": {"recent": {"accessionNumber": []}, "files": []}}
    records = [
        {
            "accessionNumber": f"{cik:010}-24-000001",
            "filingDate": "2024-02-01",
            "form": "10-K",
            "primaryDocument": "filing.htm",
            "isXBRL": 1,
            "isInlineXBRL": 0,
        }
    ]
    if cik == 42:
        records.append(
            records[0]
            | {
                "accessionNumber": f"{cik:010}-24-000002",
                "isXBRL": 0,
                "isInlineXBRL": 0,
            }
        )
    arrays = {name: [record[name] for record in records] for name in records[0]}
    return {
        "filings": {"recent": arrays, "files": [{"name": "historical42.json"}] if cik == 42 else []}
    }


def _response(url: str) -> httpx.Response:  # noqa: PLR0911 -- fixture endpoint router.
    if url.endswith("company_tickers.json"):
        return httpx.Response(
            200, json={"0": {"ticker": "ABC", "cik_str": 42}, "1": {"ticker": "DEF", "cik_str": 84}}
        )
    if "companyfacts/CIK" in url:
        cik = int(url.rsplit("CIK", 1)[1].split(".", maxsplit=1)[0])
        return httpx.Response(
            200,
            json={
                "cik": cik,
                "facts": {
                    "us-gaap": {
                        "Assets": {
                            "units": {
                                "USD": [{"val": 100, "filed": "2024-02-01", "end": "2023-12-31"}]
                            }
                        }
                    }
                },
            },
        )
    if "submissions/CIK" in url:
        cik = int(url.rsplit("CIK", 1)[1].split(".", maxsplit=1)[0])
        return httpx.Response(200, json=_submissions(cik))
    if url.endswith("historical42.json"):
        return httpx.Response(
            200,
            json={
                "accessionNumber": ["0000000042-08-000001"],
                "form": ["10-K"],
                "filingDate": ["2008-02-01"],
                "primaryDocument": ["old.htm"],
                "isXBRL": [1],
                "isInlineXBRL": [0],
            },
        )
    if url.endswith("index.json"):
        return httpx.Response(
            200,
            json={
                "directory": {
                    "item": [
                        {"name": name}
                        for name in (
                            "filing.htm",
                            "issuer-20231231.xml",
                            "issuer-20231231.xsd",
                            "FilingSummary.xml",
                            "issuer_cal.xml",
                            "issuer_pre.xml",
                            "issuer_def.xml",
                            "issuer_lab.xml",
                            "R1.xml",
                        )
                    ]
                }
            },
        )
    if url.endswith("filing.htm"):
        return httpx.Response(200, content=b"<html><body>Primary filing</body></html>")
    if url.endswith("issuer-20231231.xml"):
        return httpx.Response(
            200,
            content=b"""<x:xbrl xmlns:x="http://www.xbrl.org/2003/instance"
            xmlns:us-gaap="http://fasb.org/us-gaap/2024"><x:context id="c"><x:entity>
            <x:identifier>42</x:identifier></x:entity><x:period><x:instant>2023-12-31</x:instant>
            </x:period></x:context><x:unit id="usd"><x:measure>USD</x:measure></x:unit>
            <us-gaap:Assets contextRef="c" unitRef="usd">100</us-gaap:Assets></x:xbrl>""",
        )
    pytest.fail(f"Unexpected SEC fixture URL: {url}")


def test_global_metadata_precedes_originals_and_skips_non_xbrl_era_documents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "sec"
    historical = root / "metadata/historical-linkage"
    historical.mkdir(parents=True)
    pd.DataFrame({"cik": [126], "status": ["candidate_only"]}).to_csv(
        historical / "candidates.csv", index=False
    )
    calls = []

    def respond(url: str, **_kwargs: object) -> httpx.Response:
        calls.append(url)
        if "/Archives/" in url:
            checkpoint = json.loads((root / "acquisition.json").read_text())
            assert checkpoint["phase"] == "metadata"
            assert checkpoint["metadata_complete"]
            assert checkpoint["candidate_ciks"] == 3
            assert len(list((root / "metadata/company-index").glob("*.json"))) == 3
        return _response(url)

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(httpx, "get", respond)
    result = sec.acquire_sources(_monthly(), root, "Researcher researcher@example.edu")
    assert result["phase"] == "originals"
    assert result["status"] == "initialized"
    first_original = next(index for index, url in enumerate(calls) if "/Archives/" in url)
    assert all("data.sec.gov" not in url for url in calls[first_original:])
    assert any(url.endswith("historical42.json") for url in calls[:first_original])
    assert not any("-08-" in url or "000000004224000002" in url for url in calls)
    assert not any(
        url.endswith((".xsd", "FilingSummary.xml", "_cal.xml", "_lab.xml", "R1.xml"))
        for url in calls
    )
    assert result["filing_statuses"]["before_xbrl_feature_era"] == 1
    assert result["filing_statuses"]["reported_non_xbrl"] == 1
    assert result["filing_statuses"]["parsed"] == 2
    assert (root / "metadata/progress/metadata/CIK0000000126.json").is_file()


def test_empty_original_parse_cannot_complete_source_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def respond(url: str, **_kwargs: object) -> httpx.Response:
        if url.endswith("issuer-20231231.xml"):
            return httpx.Response(200, content=b'<xbrl xmlns="http://www.xbrl.org/2003/instance"/>')
        return _response(url)

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(httpx, "get", respond)
    root = tmp_path / "sec"
    result = sec.acquire_sources(_monthly(), root, "Researcher researcher@example.edu")
    assert result["phase"] == "originals"
    assert result["status"] == "pending_parse"
    assert result["filing_statuses"]["no_native_facts"] == 2
    statuses = list((root / "filings").glob("*/*/parse-status.json"))
    assert len(statuses) == 2
    for filename in statuses:
        status = json.loads(filename.read_text())
        assert not status["complete"]
        assert status["parser_version"] == sec.PARSER_VERSION
        assert len(status["parser_implementation_sha256"]) == 64


def test_old_positive_parse_refreshes_cached_custom_html_narrative_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "sec"
    accession = "0000000042-24-000001"
    folder = root / "filings/0000000042" / accession
    folder.mkdir(parents=True)
    (folder / "index.json").write_text(
        json.dumps({"directory": {"item": [{"name": "filing.htm"}]}})
    )
    (folder / "filing.htm").write_bytes(
        b"""<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
        xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:acme="https://acme.example/2024">
        <ix:resources><xbrli:context id="c"><xbrli:entity><xbrli:identifier>42</xbrli:identifier>
        </xbrli:entity><xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period>
        </xbrli:context></ix:resources><ix:nonNumeric name="acme:Policy" contextRef="c">
        <p>A narrative paragraph.</p></ix:nonNumeric></html>"""
    )
    (folder / "facts.json").write_text(
        json.dumps(
            [
                {
                    "concept": "acme:Policy",
                    "value": "A narrative paragraph.",
                    "value_type": "categorical",
                }
            ]
        )
    )
    (folder / "parse-status.json").write_text(json.dumps({"complete": True, "native_facts": 1}))

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Refreshing a legacy parse requested already-cached SEC documents.")

    monkeypatch.setattr(httpx, "get", forbidden)
    filing = {"cik": 42, "accession": accession, "primaryDocument": "filing.htm", "form": "10-K"}
    with sec.SECClient(None, offline=True) as client:
        result = sec._original_filing(client, root, filing)  # noqa: SLF001 -- exercise semantic cache-version upgrade.
        again = sec._original_filing(client, root, filing)  # noqa: SLF001 -- current-version positive cache is reusable.
    assert result["status"] == "parsed"
    assert again["status"] == "cached"
    rows = json.loads(gzip.decompress((folder / "facts.json.gz").read_bytes()))
    assert rows[0]["value_type"] == "narrative"
    status = json.loads((folder / "parse-status.json").read_text())
    assert status["complete"]
    assert status["parser_version"] == sec.PARSER_VERSION


def test_metadata_only_materializes_coverage_and_resumes_without_metadata_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def respond(url: str, **_kwargs: object) -> httpx.Response:
        calls.append(url)
        return _response(url)

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(httpx, "get", respond)
    root = tmp_path / "sec"
    result = sec.acquire_sources(
        _monthly(), root, "Researcher researcher@example.edu", metadata_only=True
    )
    assert result["status"] == "metadata_ready"
    assert result["metadata_complete"]
    assert result["originals_pending"] == 2
    assert not any("/Archives/" in url for url in calls)
    assert (root / "crosswalk.csv").is_file()
    assert (root / "metadata/filings.json").is_file()
    calls.clear()
    resumed = sec.acquire_sources(_monthly(), root, "Researcher researcher@example.edu")
    assert calls
    assert all("/Archives/" in url for url in calls)
    assert resumed["status"] == "initialized"


def test_metadata_checkpoint_survives_interruption_before_original_downloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def respond(url: str, **_kwargs: object) -> httpx.Response:
        if "/Archives/" in url:
            raise KeyboardInterrupt
        return _response(url)

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(httpx, "get", respond)
    root = tmp_path / "sec"
    with pytest.raises(KeyboardInterrupt):
        sec.acquire_sources(_monthly(), root, "Researcher researcher@example.edu")
    checkpoint = json.loads((root / "acquisition.json").read_text())
    assert checkpoint["phase"] == "metadata"
    assert checkpoint["metadata_complete"]
    assert (root / "metadata/metadata-phase.json").is_file()


def test_persistent_http_client_reuses_pool_and_closes_on_context_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_client = httpx.Client
    clients = []
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    def factory(*, timeout: float, follow_redirects: bool) -> httpx.Client:
        client = original_client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            transport=httpx.MockTransport(handle),
        )
        clients.append(client)
        return client

    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(httpx, "Client", factory)
    with sec.SECClient("Researcher researcher@example.edu") as client:
        assert client.json("https://data.sec.gov/one", tmp_path / "one.json") == {"ok": True}
        assert client.json("https://data.sec.gov/two", tmp_path / "two.json") == {"ok": True}
        assert len(clients) == 1
        assert not clients[0].is_closed
    assert clients[0].is_closed
    assert len(requests) == 2
    assert all(
        request.headers["User-Agent"] == "Researcher researcher@example.edu" for request in requests
    )


def test_document_selection_keeps_only_primary_html_and_possible_instance_xml() -> None:
    index = {
        "directory": {
            "item": [
                {"name": name}
                for name in (
                    "main.htm",
                    "other-exhibit.htm",
                    "instance.xml",
                    "taxonomy.xsd",
                    "FilingSummary.xml",
                    "R12.xml",
                    "a_cal.xml",
                    "a-def.xml",
                    "a_labels.xml",
                    "../escape.xml",
                )
            ]
        }
    }
    assert sec.filing_documents(index, "main.htm") == ["main.htm", "instance.xml"]
