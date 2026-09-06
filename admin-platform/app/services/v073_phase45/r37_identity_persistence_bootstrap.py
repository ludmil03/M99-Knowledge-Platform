from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sqlite3
from datetime import datetime, timezone

from sqlalchemy import inspect
from sqlalchemy.orm import Session


IDENTITY_TABLES = (
    "m99_v073_identity_external_mappings",
)


@dataclass(frozen=True)
class IdentityBootstrapPlan:
    database_path: str
    missing_tables: tuple[str, ...]
    ready: bool
    message: str


def inspect_identity_persistence(db: Session) -> IdentityBootstrapPlan:
    bind = db.get_bind()
    db_path = getattr(bind.url, "database", None)
    if not db_path:
        return IdentityBootstrapPlan(
            database_path="",
            missing_tables=IDENTITY_TABLES,
            ready=False,
            message="Identity persistence requires a file-backed SQLite Admin DB.",
        )

    inspector = inspect(bind)
    present = set(inspector.get_table_names())
    missing = tuple(name for name in IDENTITY_TABLES if name not in present)

    return IdentityBootstrapPlan(
        database_path=str(Path(db_path).resolve()),
        missing_tables=missing,
        ready=(len(missing) == 0),
        message=(
            "Identity persistence schema is READY."
            if not missing
            else "Identity persistence schema is missing required tables."
        ),
    )


def backup_admin_db(db: Session) -> Path:
    bind = db.get_bind()
    db_path = getattr(bind.url, "database", None)
    if not db_path:
        raise RuntimeError("Cannot back up non-file SQLite database.")

    src = Path(db_path).resolve()
    if not src.exists():
        raise RuntimeError(f"Admin DB does not exist: {src}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = src.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    dst = backup_dir / f"{src.stem}_before_r37r6_identity_{stamp}{src.suffix}"
    shutil.copy2(src, dst)
    return dst


def bootstrap_identity_persistence_sqlite(db: Session) -> tuple[Path, IdentityBootstrapPlan]:
    """
    Explicit one-time bootstrap for the existing Admin SQLite DB.

    Safety:
    - caller must decide when to run this;
    - backup is created first;
    - uses CREATE TABLE IF NOT EXISTS;
    - creates only the missing Identity persistence table/indexes;
    - does not create product rows, DRAFT jobs, channel writes, or stock writes.
    """
    plan = inspect_identity_persistence(db)
    if plan.ready:
        return Path(plan.database_path), plan

    backup = backup_admin_db(db)

    conn = sqlite3.connect(plan.database_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS m99_v073_identity_external_mappings (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                m99_product_id INTEGER,
                mapping_type VARCHAR(64) NOT NULL,
                external_value VARCHAR(255) NOT NULL,
                organization_id INTEGER,
                source_id INTEGER,
                verified BOOLEAN NOT NULL DEFAULT 0,
                verified_at DATETIME
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS ix_m99_v073_identity_external_mappings_type_value_verified
            ON m99_v073_identity_external_mappings (mapping_type, external_value, verified)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS ix_m99_v073_identity_external_mappings_product
            ON m99_v073_identity_external_mappings (m99_product_id)
        """)
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        shutil.copy2(backup, Path(plan.database_path))
        raise
    else:
        conn.close()

    refreshed = inspect_identity_persistence(db)
    if not refreshed.ready:
        shutil.copy2(backup, Path(plan.database_path))
        raise RuntimeError(
            "Identity persistence verification failed after bootstrap; original DB restored."
        )

    return backup, refreshed
