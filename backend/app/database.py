from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


def create_database_engine(database_url: str, *, echo: bool = False) -> Engine:
    url = make_url(database_url)
    options: dict = {"pool_pre_ping": True, "echo": echo}
    if url.get_backend_name() == "sqlite":
        options["connect_args"] = {"check_same_thread": False}
        if url.database in (None, "", ":memory:"):
            options["poolclass"] = StaticPool
    engine = create_engine(database_url, **options)
    if url.get_backend_name() == "sqlite":
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return engine


engine = create_database_engine(settings.database_url, echo=settings.sql_echo)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def database_is_ready(session: Session) -> bool:
    session.execute(text("SELECT 1"))
    return True
