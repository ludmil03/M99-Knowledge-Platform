from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Supplier
from app.services.v073_phase45.r37_import_bridge import _host, _supplier_domain_candidates

engine = create_engine(settings.database_url)
with Session(engine) as db:
    rows = list(db.scalars(select(Supplier).where(
        Supplier.active.is_(True),
        Supplier.browser_enabled.is_(True),
    )))
    print(f"[READ ONLY] eligible operational suppliers={len(rows)}")
    matches = []
    for s in rows:
        domains = sorted(_supplier_domain_candidates(s))
        print(f"  supplier_id={s.id} name={s.name!r} domains={domains}")
        if "calenda.bg" in domains:
            matches.append(s)
    print(f"[READ ONLY] calenda.bg matches={len(matches)}")
    for s in matches:
        print(f"  MATCH supplier_id={s.id} name={s.name!r}")
    if len(matches) == 1:
        print("[PASS] Exactly one existing operational Supplier can bridge Calenda safely.")
    elif len(matches) == 0:
        print("[BLOCKED] No existing operational Supplier matches calenda.bg.")
    else:
        print("[BLOCKED] Multiple operational Suppliers match calenda.bg; manual resolution required.")
