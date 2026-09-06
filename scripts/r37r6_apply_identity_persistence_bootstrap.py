from pathlib import Path
import sys

ADMIN = Path(__file__).resolve().parents[1] / 'admin-platform'
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.v073_phase45.r37_identity_persistence_bootstrap import (
    inspect_identity_persistence,
    bootstrap_identity_persistence_sqlite,
)

engine = create_engine(settings.database_url)
with Session(engine) as db:
    before = inspect_identity_persistence(db)
    print(f"[BEFORE] Ready={before.ready} Missing={list(before.missing_tables)}")
    if before.ready:
        print("[NOOP] Identity persistence already READY. No DB change required.")
    else:
        backup, after = bootstrap_identity_persistence_sqlite(db)
        print(f"[BACKUP] {backup}")
        print(f"[AFTER] Ready={after.ready} Missing={list(after.missing_tables)}")
        if not after.ready:
            raise SystemExit(2)
        print("[PASS] Identity persistence bootstrap applied and verified.")
