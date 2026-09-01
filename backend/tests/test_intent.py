import pytest

from app.schemas import Intent
from app.services.intent import classify_intent


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("find a laboratory near Delhi", Intent.LAB_SEARCH),
        ("how do I verify my HUID", Intent.HALLMARKING_QUERY),
        ("explain clause 6.3", Intent.STANDARD_QA),
        ("is certification mandatory", Intent.CERTIFICATION_QUERY),
        ("I manufacture an emergency lamp", Intent.PRODUCT_COMPLIANCE),
        ("tell me about BIS", Intent.GENERAL_BIS_QUERY),
    ],
)
def test_intent_routing(query, expected):
    assert classify_intent(query) == expected
