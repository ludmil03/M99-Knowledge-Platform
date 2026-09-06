from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import importlib, pkgutil, shutil
from sqlalchemy import inspect
from sqlalchemy.orm import Session

IDENTITY_PREFIX = "m99_v073_identity_"

@dataclass(frozen=True)
class IdentitySchemaReconciliation:
    database_path: str
    required_tables: tuple[str, ...]
    present_tables: tuple[str, ...]
    missing_tables: tuple[str, ...]
    ready: bool

def _import_identity_modules():
    package = importlib.import_module("app.services.v073_phase4")
    imported = [package.__name__]
    if hasattr(package, "__path__"):
        for mod in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if "identity" in mod.name.lower():
                importlib.import_module(mod.name)
                imported.append(mod.name)
    resolver = importlib.import_module("app.services.v073_phase4.identity_resolver")
    imported.append(resolver.__name__)
    return tuple(sorted(set(imported)))

def _discover_identity_tables():
    tables = {}
    for module_name in _import_identity_modules():
        module = importlib.import_module(module_name)
        for obj in vars(module).values():
            table = getattr(obj, "__table__", None)
            if table is not None and getattr(table, "name", "").startswith(IDENTITY_PREFIX):
                tables[table.name] = table
            metadata = getattr(obj, "metadata", None)
            mt = getattr(metadata, "tables", None)
            if mt:
                for name, candidate in mt.items():
                    if name.startswith(IDENTITY_PREFIX):
                        tables[name] = candidate
    if not tables:
        resolver = importlib.import_module("app.services.v073_phase4.identity_resolver")
        candidates = sorted(name for name, obj in vars(resolver).items()
                            if hasattr(obj, "__table__") or hasattr(obj, "metadata"))
        raise RuntimeError("No Identity persistence Table objects discovered from existing Identity modules. "
                           f"Candidate symbols={candidates}")
    return tuple(tables[name] for name in sorted(tables))

def inspect_complete_identity_schema(db: Session):
    bind = db.get_bind()
    db_path = getattr(bind.url, "database", None)
    if not db_path:
        raise RuntimeError("R3.7R7A requires file-backed SQLite Admin DB.")
    required = tuple(t.name for t in _discover_identity_tables())
    present = tuple(sorted(n for n in inspect(bind).get_table_names() if n.startswith(IDENTITY_PREFIX)))
    missing = tuple(n for n in required if n not in set(present))
    return IdentitySchemaReconciliation(str(Path(db_path).resolve()), required, present, missing, not missing)

def _backup(db: Session):
    db_path = Path(getattr(db.get_bind().url, "database")).resolve()
    if not db_path.exists():
        raise RuntimeError(f"Admin DB not found: {db_path}")
    folder = db_path.parent/"backups"; folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dst = folder/f"{db_path.stem}_before_r37r7a_identity_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, dst)
    return dst

def reconcile_complete_identity_schema(db: Session):
    before = inspect_complete_identity_schema(db)
    if before.ready:
        return None, before
    backup = _backup(db)
    try:
        wanted = set(before.missing_tables)
        for table in _discover_identity_tables():
            if table.name in wanted:
                table.create(bind=db.get_bind(), checkfirst=True)
    except Exception:
        db.rollback(); shutil.copy2(backup, Path(before.database_path)); raise
    after = inspect_complete_identity_schema(db)
    if not after.ready:
        shutil.copy2(backup, Path(before.database_path))
        raise RuntimeError(f"Identity schema verification failed; restored backup. Missing={after.missing_tables}")
    return backup, after
