"""Narrative archives and categorical scalars have separate, explicit input semantics."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pandas as pd
import pytest

from free_foundations.study.panel.features import _normalized_facts, build_features
from free_foundations.study.sources.sec import companyfact_rows, parse_xbrl
from free_foundations.study.spec import StudySpec

if TYPE_CHECKING:
    from pathlib import Path


def test_parser_archives_textblocks_declared_text_types_and_html_without_length_rules() -> None:
    content = b"""<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:acme="https://example.com/acme" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <xbrli:context id="i"><xbrli:entity><xbrli:identifier>42</xbrli:identifier></xbrli:entity>
      <xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period></xbrli:context>
      <acme:NoteTextBlock contextRef="i">A note.</acme:NoteTextBlock>
      <acme:TypedDisclosure contextRef="i" xsi:type="acme:textBlockItemType">
      Plain narrative.</acme:TypedDisclosure>
      <acme:EscapedDisclosure contextRef="i">&lt;p&gt;Narrative HTML&lt;/p&gt;
      </acme:EscapedDisclosure>
      <acme:BlockDisclosure contextRef="i"><div>A formatted note.</div></acme:BlockDisclosure>
      <acme:Policy contextRef="i">Research &amp; Development</acme:Policy>
      <acme:Threshold contextRef="i">Less than &lt;= 10</acme:Threshold>
      <acme:DetailedCategory contextRef="i">CATEGORY_VALUE</acme:DetailedCategory>
      </xbrli:xbrl>""".replace(b"CATEGORY_VALUE", b"A" * 2000)
    rows = parse_xbrl(content, cik=42)
    kinds = {row["tag"]: row["value_type"] for row in rows}
    assert kinds == {
        "NoteTextBlock": "narrative",
        "TypedDisclosure": "narrative",
        "EscapedDisclosure": "narrative",
        "BlockDisclosure": "narrative",
        "Policy": "categorical",
        "Threshold": "categorical",
        "DetailedCategory": "categorical",
    }
    assert next(row["value"] for row in rows if row["tag"] == "Policy") == "Research & Development"
    assert len(next(row["value"] for row in rows if row["tag"] == "DetailedCategory")) == 2000


def test_cached_abbott_textblocks_are_archived_but_never_count_as_scalar_inputs(
    tmp_path: Path,
) -> None:
    # Concept names and excerpt match Abbott's 2022-09-30 original SEC filing,
    # accession 0001628280-22-027550; old parser outputs labelled these categorical.
    root = tmp_path / "sec"
    folder = root / "filings/0000000042/a"
    folder.mkdir(parents=True)
    base = {
        "cik": 42,
        "namespace": "us-gaap",
        "unit": "",
        "value_type": "categorical",
        "start": "2022-01-01",
        "end": "2022-09-30",
        "filed": "2022-11-01",
        "accepted": "2022-11-01T16:30:00",
        "accession": "a",
        "dimensions": "{}",
        "source_kind": "original_filing",
        "source_url": "https://www.sec.gov/Archives/a",
        "status": "observed",
    }
    tag = "OrganizationConsolidationAndPresentationOfFinancialStatementsDisclosureTextBlock"
    narrative = (
        "Note 1 — Basis of PresentationThe accompanying unaudited, "
        "condensed consolidated financial statements"
    )
    facts = [
        base | {"concept": f"us-gaap:{tag}", "tag": tag, "value": narrative, "raw_value": narrative}
    ]
    (folder / "facts.json").write_text(json.dumps(facts))
    pd.DataFrame(
        [
            {
                "permco": 2,
                "cik": 42,
                "effective_from": "2009-01-01",
                "effective_to": "2025-12-31",
                "status": "verified_interval",
                "evidence_url": "https://www.sec.gov/Archives/a",
                "accession": "a",
            }
        ]
    ).to_csv(root / "crosswalk.csv", index=False)
    quarterly = pd.DataFrame(
        {"issuer_id": ["PERMCO:2"], "permco": [2], "quarter": [pd.Timestamp("2023-03-31")]}
    )
    monthly = pd.DataFrame({"date": ["2022-12-30"]})
    result = build_features(quarterly, monthly, root, StudySpec())
    assert result["facts"]["value"].tolist() == [narrative]
    assert result["facts"]["value_type"].tolist() == ["narrative"]
    assert result["broad"].empty
    assert not bool(result["availability"].iloc[0]["xbrl_available"])
    assert result["availability"].iloc[0]["native_scalar_count"] == 0


def test_companyfacts_pure_nil_matches_observed_numeric_or_boolean_type() -> None:
    def observation(*, value: object) -> dict[str, object]:
        return {"val": value, "end": "2023-12-31", "filed": "2024-02-01"}

    rows = companyfact_rows(
        {
            "cik": 42,
            "facts": {
                "custom": {
                    "Ratio": {"units": {"pure": [observation(value=None), observation(value=1.5)]}},
                    "Flag": {"units": {"pure": [observation(value=None), observation(value=True)]}},
                    "NilRatio": {"units": {"pure": [observation(value=None)]}},
                }
            },
        }
    )
    actual = pd.DataFrame(rows)
    assert actual.loc[actual["tag"].eq("Ratio"), "value_type"].tolist() == ["numeric", "numeric"]
    assert actual.loc[actual["tag"].eq("Flag"), "value_type"].tolist() == [
        "categorical",
        "categorical",
    ]
    assert actual.loc[actual["tag"].eq("NilRatio"), "value_type"].tolist() == ["numeric"]
    # Repair pre-existing cached parser output using the same concept/unit evidence.
    actual.loc[actual["value"].isna(), "value_type"] = "categorical"
    normalized = _normalized_facts(actual)
    assert normalized["value_type"].tolist() == pd.DataFrame(rows)["value_type"].tolist()


def test_conflicting_observed_companyfact_types_raise_instead_of_flipping_type() -> None:
    with pytest.raises(ValueError, match="mixes observed scalar types"):
        companyfact_rows(
            {"facts": {"custom": {"Mixed": {"units": {"pure": [{"val": True}, {"val": 1.5}]}}}}}
        )


def test_cached_declared_textblock_type_is_respected_even_without_tag_suffix() -> None:
    frame = pd.DataFrame(
        [
            {
                "concept": "custom:Note",
                "value": "A note.",
                "value_type": "categorical",
                "xbrl_type": "textBlockItemType",
                "end": "2023-12-31",
                "start": "",
                "status": "observed",
            }
        ]
    )
    normalized = _normalized_facts(frame)
    assert normalized["value_type"].tolist() == ["narrative"]
    assert normalized["value"].tolist() == ["A note."]


def test_excluded_footnote_html_does_not_turn_a_short_scalar_into_narrative() -> None:
    content = b"""<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
      xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:acme="https://example.com/acme">
      <ix:resources><xbrli:context id="i"><xbrli:entity><xbrli:identifier>42</xbrli:identifier>
      </xbrli:entity><xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period>
      </xbrli:context></ix:resources>
      <ix:nonNumeric name="acme:Policy" contextRef="i" escape="true">Research &amp; Development
      <ix:exclude><p>Footnote only</p></ix:exclude></ix:nonNumeric></html>"""
    rows = parse_xbrl(content, cik=42)
    assert len(rows) == 1
    assert rows[0]["value_type"] == "categorical"
    assert rows[0]["value"] == "Research & Development"
