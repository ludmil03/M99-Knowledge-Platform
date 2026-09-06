from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.entities import Supplier
from app.services.v073_phase45.r37_import_bridge import _supplier_domain_candidates

engine=create_engine(settings.database_url)
with Session(engine) as db:
    rows=list(db.scalars(select(Supplier)))
    matches=[s for s in rows if "calenda.bg" in _supplier_domain_candidates(s)]
    print(f"[READ ONLY] total Supplier rows={len(rows)}")
    print(f"[READ ONLY] calenda.bg operational matches={len(matches)}")
    for s in matches:
        print(f"  MATCH id={s.id} name={s.name!r} active={s.active} browser_enabled={s.browser_enabled}")
    if len(matches)==0:
        print("[READY FOR EXPLICIT ACTION] No operational Calenda Supplier exists.")
    elif len(matches)==1:
        print("[NO CREATE NEEDED] One operational Calenda Supplier already exists.")
    else:
        print("[BLOCKED] Multiple Calenda Supplier rows exist; do not provision.")
