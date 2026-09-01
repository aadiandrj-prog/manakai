import json
from pathlib import Path

from app.schemas import Intent, SupportedLanguage
from app.services.ai_interpretation import detect_language, interpret


def test_clean_english_extraction_preserves_explicit_values():
    result = interpret("I am planning to make 1.5kw cordless kettles for homes.")
    assert result.intent.intent == Intent.PRODUCT_COMPLIANCE
    assert result.product.rated_power_w == 1500
    assert result.product.rated_voltage_v is None
    assert result.product.intended_use == "household"
    assert result.product.additional_attributes["cordless"] is True


def test_language_detection_and_multilingual_equivalence():
    hinglish = interpret("230V ka ghar wala electric kettle manufacture kar raha hu, BIS ka kya requirement hai?")
    hindi = interpret("मैं घरेलू उपयोग के लिए 230 वोल्ट की इलेक्ट्रिक केतली बनाता हूँ।")
    assert hinglish.language == SupportedLanguage.HINGLISH
    assert hindi.language == SupportedLanguage.HINDI
    assert hinglish.product.rated_voltage_v == hindi.product.rated_voltage_v == 230
    assert hinglish.product.product_type == hindi.product.product_type == "electric_kettle"
    assert hinglish.product.intended_use == hindi.product.intended_use == "household"


def test_enterprise_category_is_not_inferred_from_ambiguous_small_product():
    result = interpret("Do BIS rules apply to my small kettle startup?")
    assert result.product.enterprise_category is None
    assert detect_language("ghar ka kettle") == SupportedLanguage.HINGLISH


def test_phase2c_benchmark_fixture_contains_all_release_cases():
    cases = json.loads((Path(__file__).parent / "fixtures" / "phase2c_benchmark.json").read_text())
    assert {item["id"] for item in cases} == {
        "clean_english", "missing_voltage", "hinglish", "hindi", "misinformation",
        "prompt_injection", "fake_standard", "historical", "future", "technical_qa", "unanswerable",
    }
