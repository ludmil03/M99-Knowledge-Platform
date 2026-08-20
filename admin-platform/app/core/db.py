from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def normalize_database_url(url: str) -> str:
    """
    Resolve relative SQLite database paths against admin-platform root
    and create the parent directory before SQLAlchemy opens the DB.
    Other database URLs are returned unchanged.
    """
    if not url.startswith("sqlite:///"):
        return url

    raw = url[len("sqlite:///"):]
    if raw == ":memory:":
        return url

    db_path = Path(raw)
    if not db_path.is_absolute():
        db_path = (PROJECT_ROOT / db_path).resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Windows-safe SQLAlchemy SQLite URL uses forward slashes.
    return "sqlite:///" + db_path.as_posix()

DATABASE_URL = normalize_database_url(settings.database_url)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
