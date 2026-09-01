from app.schemas import ProductAnalyseRequest, SourceKind
from app.services.compliance import analyse_product


def test_emergency_lamp_vertical_slice_is_deterministic():
    profile = analyse_product(ProductAnalyseRequest(description="portable rechargeable LED emergency lamp"))
    assert profile.applicable_standards[0].number == "IS 10322 (Part 5/Sec 8)"
    assert profile.mandatory_status == "UNVERIFIED"
    assert profile.next_steps[2].status == "attention"
    assert all(citation.source_kind == SourceKind.DEMO for citation in profile.evidence)


def test_kettle_uses_distinct_candidate():
    profile = analyse_product(ProductAnalyseRequest(description="electric kettle for household use"))
    assert profile.applicable_standards[0].id == "is-302-2-15"


def test_profile_identifies_missing_attributes():
    profile = analyse_product(ProductAnalyseRequest(description="motorcycle helmet"))
    assert "rated voltage" in profile.product.missing_attributes
