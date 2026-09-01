from pathlib import Path

from app.ingestion.adapters import BISLIMSAdapter, BISProductManualAdapter, BISQCOAdapter, BISStandardAdapter
from app.ingestion.parser import ClauseAwareParser
from app.ingestion.pipeline import FIXTURE_PATH, load_fixture


def test_standard_and_qco_fixture_parsing():
    fixture = load_fixture()
    standards = BISStandardAdapter().normalize(BISStandardAdapter().parse(fixture))
    qcos = BISQCOAdapter().normalize(BISQCOAdapter().parse(fixture))
    assert BISStandardAdapter().validate(standards) == []
    assert standards[0]["number"] == "IS 302 (Part 2/Sec 15)"
    assert standards[0]["source_record"]["content_hash"]
    assert BISQCOAdapter().validate(qcos) == []
    assert {row["enterprise_category"] for row in qcos[0]["applicability"]} == {"GENERAL", "SMALL", "MICRO"}


def test_product_manual_clause_boundaries_and_metadata():
    fixture = load_fixture()
    manual = BISProductManualAdapter().normalize(BISProductManualAdapter().parse(fixture))[0]
    chunks = ClauseAwareParser().parse_pages(manual["pages"])
    assert manual["manual_identifier"] == "PM/IS 302-2-15/1/February 2024"
    assert [chunk.clause for chunk in chunks] == ["1", "2(a)", "A.1", "A.2", "A.3(a)", "A.4", "A.5"]
    assert chunks[4].page == 4
    assert all(chunk.content_hash for chunk in chunks)


def test_lims_parser_preserves_scope_and_validity():
    fixture = load_fixture()
    records = BISLIMSAdapter().normalize(BISLIMSAdapter().parse(fixture))
    assert BISLIMSAdapter().validate(records) == []
    assert records[0]["valid_until"] == "2028-10-05"
    assert records[1]["scope_exclusions"] == ["19.11.4.1-19.11.4.7 EMI/EMC tests"]


def test_fixture_is_captured_under_backend_tests():
    assert FIXTURE_PATH.is_file()
    assert "tests/fixtures/official" in FIXTURE_PATH.as_posix()
