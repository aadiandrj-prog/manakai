from app.schemas import RegulatoryAnswerPackage, SupportedLanguage
from app.services.answer_validation import GeneratedAnswer, GeneratedAnswerValidator


def test_unknown_evidence_id_is_rejected():
    package = RegulatoryAnswerPackage(intent="STANDARD_QA", language=SupportedLanguage.ENGLISH, evidence=[])
    valid, reason = GeneratedAnswerValidator().validate(GeneratedAnswer(answer="Unsupported", evidence_ids=["E99"]), package)
    assert valid is False
    assert "unknown evidence" in reason.lower()
