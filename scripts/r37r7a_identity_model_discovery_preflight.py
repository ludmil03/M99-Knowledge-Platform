from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
sys.path.insert(0,str(ADMIN))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.v073_phase45.r37_identity_persistence_reconcile import _import_identity_modules,_discover_identity_tables,inspect_complete_identity_schema
print("[IMPORTED IDENTITY MODULES]")
for x in _import_identity_modules(): print(" -",x)
print("[DISCOVERED IDENTITY TABLES]")
for t in _discover_identity_tables(): print(" -",t.name)
with Session(create_engine(settings.database_url)) as db:
    x=inspect_complete_identity_schema(db)
    print("[DB]",x.database_path); print("[REQUIRED]",list(x.required_tables))
    print("[PRESENT]",list(x.present_tables)); print("[MISSING]",list(x.missing_tables)); print("[READY]",x.ready)
