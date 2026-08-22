from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Phase2Base


def make_engine(database_url: str):
    kwargs = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, future=True, **kwargs)


def make_session_factory(database_url: str):
    return sessionmaker(
        bind=make_engine(database_url),
        autoflush=False,
        expire_on_commit=False,
    )


def create_temporary_or_explicit_schema(database_url: str) -> None:
    """Create Phase 2 tables only for an explicit DB URL.

    This function is used by tests and future approved bootstrap/migration tools.
    The installer never calls it against the user's production Admin DB.
    """
    Phase2Base.metadata.create_all(make_engine(database_url))
