"""Single provider boundary for controlled, schema-validated AI calls."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from ..config import Settings, settings

logger = logging.getLogger("manakai")
T = TypeVar("T", bound=BaseModel)


class AIProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    name = "unknown"

    @abstractmethod
    def structured(self, *, system: str, user: str, schema: type[T]) -> T:
        raise NotImplementedError


class DisabledProvider(AIProvider):
    name = "disabled"

    def structured(self, *, system: str, user: str, schema: type[T]) -> T:
        raise AIProviderError("AI provider is not configured")


class HTTPStructuredProvider(AIProvider):
    def __init__(self, config: Settings):
        self.config = config

    def _request(self, *, system: str, user: str, schema: type[T]) -> T:
        raise NotImplementedError

    def structured(self, *, system: str, user: str, schema: type[T]) -> T:
        last_error: Exception | None = None
        for attempt in range(self.config.ai_max_retries + 1):
            try:
                return self._request(system=system, user=user, schema=schema)
            except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                logger.warning("ai_provider_attempt_failed provider=%s attempt=%s", self.name, attempt + 1)
        raise AIProviderError(f"{self.name} failed to return schema-valid output") from last_error


class OpenAIProvider(HTTPStructuredProvider):
    name = "openai"

    def _request(self, *, system: str, user: str, schema: type[T]) -> T:
        if not self.config.openai_api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured")
        payload = {
            "model": self.config.llm_model or "gpt-5-mini",
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": user}]},
            ],
            "text": {"format": {"type": "json_schema", "name": schema.__name__, "strict": False, "schema": schema.model_json_schema()}},
            "max_output_tokens": self.config.ai_max_output_tokens,
        }
        response = httpx.post(
            "https://api.openai.com/v1/responses", json=payload,
            headers={"Authorization": f"Bearer {self.config.openai_api_key}"}, timeout=self.config.ai_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        usage = body.get("usage", {})
        logger.info("answer_generated provider=openai input_tokens=%s output_tokens=%s", usage.get("input_tokens"), usage.get("output_tokens"))
        text = next(part["text"] for item in body["output"] if item.get("type") == "message" for part in item.get("content", []) if part.get("type") == "output_text")
        return schema.model_validate_json(text)


class GeminiProvider(HTTPStructuredProvider):
    name = "gemini"

    def _request(self, *, system: str, user: str, schema: type[T]) -> T:
        if not self.config.gemini_api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured")
        model = self.config.llm_model or "gemini-3.6-flash"
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "responseFormat": {"text": {"mimeType": "application/json", "schema": schema.model_json_schema()}},
                "maxOutputTokens": self.config.ai_max_output_tokens,
            },
        }
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            json=payload, headers={"x-goog-api-key": self.config.gemini_api_key}, timeout=self.config.ai_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        usage = body.get("usageMetadata", {})
        logger.info("answer_generated provider=gemini input_tokens=%s output_tokens=%s", usage.get("promptTokenCount"), usage.get("candidatesTokenCount"))
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return schema.model_validate_json(text)


def provider_from_config(config: Settings = settings) -> AIProvider:
    if config.llm_provider == "openai":
        return OpenAIProvider(config)
    if config.llm_provider == "gemini":
        return GeminiProvider(config)
    return DisabledProvider()
