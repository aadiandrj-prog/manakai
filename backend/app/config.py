from dataclasses import dataclass
import os


def _csv(name: str, default: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


def sqlalchemy_database_url(database_url: str) -> str:
    """Select the installed Psycopg 3 driver for provider-style Postgres URLs."""
    for prefix in ("postgresql://", "postgres://"):
        if database_url.startswith(prefix):
            return "postgresql+psycopg://" + database_url.removeprefix(prefix)
    return database_url


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://manakai:manakai@localhost:5432/manakai",
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "disabled").lower()
    llm_model: str = os.getenv("LLM_MODEL", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ai_timeout_seconds: float = float(os.getenv("AI_TIMEOUT_SECONDS", "12"))
    ai_max_retries: int = int(os.getenv("AI_MAX_RETRIES", "1"))
    ai_max_output_tokens: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "700"))
    ai_daily_request_limit: int = int(os.getenv("AI_DAILY_REQUEST_LIMIT", "500"))
    ai_max_input_chars: int = int(os.getenv("AI_MAX_INPUT_CHARS", "12000"))
    ai_max_evidence_chars: int = int(os.getenv("AI_MAX_EVIDENCE_CHARS", "8000"))
    conversation_history_limit: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "12"))
    max_request_body_bytes: int = int(os.getenv("MAX_REQUEST_BODY_BYTES", "65536"))
    chat_rate_limit_requests: int = int(os.getenv("CHAT_RATE_LIMIT_REQUESTS", "30"))
    analysis_rate_limit_requests: int = int(os.getenv("ANALYSIS_RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    trust_proxy_headers: bool = os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true"
    openai_allowed_models: tuple[str, ...] = _csv("OPENAI_ALLOWED_MODELS", "gpt-5-mini,gpt-5.4-mini")
    gemini_allowed_models: tuple[str, ...] = _csv("GEMINI_ALLOWED_MODELS", "gemini-3.6-flash,gemini-3.7-flash")
    expected_schema_revision: str = os.getenv("EXPECTED_SCHEMA_REVISION", "f3c8a1d2e740")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "disabled")
    cors_origins: tuple[str, ...] = _csv("CORS_ORIGINS", "http://localhost:3000")
    sql_echo: bool = os.getenv("SQL_ECHO", "false").lower() == "true"


settings = Settings()
