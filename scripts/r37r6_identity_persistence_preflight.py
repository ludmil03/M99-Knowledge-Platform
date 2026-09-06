from pathlib import Path
import sys

ADMIN = Path(__file__).resolve().parents[1] / 'admin-platform'
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.v073_phase45.r37_identity_persistence_bootstrap import inspect_identity_persistence

engine = create_engine(settings.database_url)
with Session(engine) as db:
    plan = inspect_identity_persistence(db)
    print(f"[READ ONLY] Admin DB: {plan.database_path}")
    print(f"[READ ONLY] Missing identity tables: {list(plan.missing_tables)}")
    print(f"[READ ONLY] Ready: {plan.ready}")
    print(f"[READ ONLY] {plan.message}")
