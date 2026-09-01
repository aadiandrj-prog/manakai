from dataclasses import dataclass
import os


def _csv(name: str, default: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://manakai:manakai@localhost:5432/manakai",
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "disabled")
    cors_origins: tuple[str, ...] = _csv("CORS_ORIGINS", "http://localhost:3000")
    sql_echo: bool = os.getenv("SQL_ECHO", "false").lower() == "true"


settings = Settings()
