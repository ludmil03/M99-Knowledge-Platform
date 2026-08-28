from __future__ import annotations

import argparse
import importlib
from pathlib import Path
import shutil
import sys

from sqlalchemy import inspect

# This helper lives under repository /scripts, while the application package
# lives under /admin-platform/app. When Python executes a script by path it
# places the script directory on sys.path, not the repository's admin-platform
# directory. Resolve it from the script location and add it explicitly.
REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN_PLATFORM_ROOT = REPO_ROOT / "admin-platform"
if not (ADMIN_PLATFORM_ROOT / "app").is_dir():
    raise RuntimeError(f"admin-platform/app not found from helper location: {ADMIN_PLATFORM_ROOT}")
admin_platform_str = str(ADMIN_PLATFORM_ROOT)
if admin_platform_str not in sys.path:
    sys.path.insert(0, admin_platform_str)

from app.services.v073_phase45.source_registry_persistence import bootstrap_schema, list_tables


def get_session(db_module_name: str):
    module = importlib.import_module(db_module_name)
    get_db = getattr(module, "get_db")
    gen = get_db()
    try:
        session = next(gen)
    except TypeError:
        session = gen
        gen = None
    return session, gen


def sqlite_path_from_bind(bind) -> Path:
    url = bind.url
    if url.get_backend_name() != "sqlite":
        raise RuntimeError(f"Only local SQLite Admin DB is accepted for this bootstrap, got: {url.get_backend_name()}")
    db = url.database
    if not db or db == ":memory:":
        raise RuntimeError("Admin DB is not a persistent SQLite file.")
    p = Path(db)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-module", required=True)
    ap.add_argument("--mode", choices=["locate", "apply", "verify"], required=True)
    args = ap.parse_args()

    session, gen = get_session(args.db_module)
    try:
        bind = session.get_bind()
        db_path = sqlite_path_from_bind(bind)
        if args.mode == "locate":
            print(str(db_path))
            return 0

        expected = set(list_tables())
        if args.mode == "apply":
            bootstrap_schema(bind)

        actual = set(inspect(bind).get_table_names())
        missing = sorted(expected - actual)
        if missing:
            raise RuntimeError("Missing Rev31 tables after schema operation: " + ", ".join(missing))
        print("REV31_TABLES_OK=" + ",".join(sorted(expected)))
        print("ADMIN_DB=" + str(db_path))
        return 0
    finally:
        try:
            session.close()
        except Exception:
            pass
        if gen is not None:
            try:
                gen.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
