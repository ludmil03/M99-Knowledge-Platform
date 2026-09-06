from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT/"admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.v073_phase45.r37_identity_persistence_reconcile import inspect_complete_identity_schema, reconcile_complete_identity_schema
engine = create_engine(settings.database_url)
with Session(engine) as db:
    before = inspect_complete_identity_schema(db)
    print("[IDENTITY ORM REQUIRED]", list(before.required_tables))
    print("[IDENTITY DB PRESENT]", list(before.present_tables))
    print("[IDENTITY MISSING]", list(before.missing_tables))
    backup, after = reconcile_complete_identity_schema(db)
    print("[BACKUP]", backup if backup else "NOOP - already ready")
    print("[IDENTITY READY AFTER]", after.ready)
    print("[IDENTITY MISSING AFTER]", list(after.missing_tables))
    if not after.ready:
        raise SystemExit(2)
