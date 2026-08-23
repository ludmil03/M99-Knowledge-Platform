from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Phase4Base

def explicit_database_url() -> str:
    value = os.getenv("M99_ADMIN_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("M99_ADMIN_DATABASE_URL is required; no implicit production DB fallback.")
    return value

def make_engine(database_url: str):
    kwargs = {"connect_args":{"check_same_thread":False}} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, **kwargs)

def make_session_factory(database_url: str):
    return sessionmaker(bind=make_engine(database_url), autoflush=False, expire_on_commit=False)

def create_test_schema(database_url: str):
    Phase4Base.metadata.create_all(make_engine(database_url))
