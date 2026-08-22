from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Phase3Base


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
    Phase3Base.metadata.create_all(make_engine(database_url))
