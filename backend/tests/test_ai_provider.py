from dataclasses import replace

import pytest

from app.config import settings
from app.schemas import IntentClassification
from app.services.ai_provider import AIProviderError, DisabledProvider, GeminiProvider, OpenAIProvider, provider_from_config


def test_provider_factory_and_missing_keys_fail_closed():
    assert isinstance(provider_from_config(replace(settings, llm_provider="disabled")), DisabledProvider)
    with pytest.raises(AIProviderError):
        OpenAIProvider(replace(settings, openai_api_key="")).structured(system="x", user="y", schema=IntentClassification)
    with pytest.raises(AIProviderError):
        GeminiProvider(replace(settings, gemini_api_key="")).structured(system="x", user="y", schema=IntentClassification)
