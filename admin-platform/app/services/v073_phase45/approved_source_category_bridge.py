from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.v073_phase45.source_registry_persistence import ApprovedSourceRecord, CanonicalCategoryRecord

@dataclass(frozen=True)
class ApprovedOperationalSource:
    source_uuid: str
    source_kind: str
    name: str
    domain: str
    base_url: str
    activation_status: str

@dataclass(frozen=True)
class ApprovedCanonicalCategory:
    category_uuid: str
    name: str
    parent_uuid: str | None
    active: bool

def normalize_domain(value: str) -> str:
    value=(value or "").strip().lower()
    for prefix in ("https://","http://"):
        if value.startswith(prefix):
            value=value[len(prefix):]
            break
    value=value.split("/",1)[0]
    if value.startswith("www."):
        value=value[4:]
    return value.rstrip(".")

def approved_operational_sources(db: Session, *, source_kind: str | None=None) -> list[ApprovedOperationalSource]:
    stmt=select(ApprovedSourceRecord)
    if source_kind:
        stmt=stmt.where(ApprovedSourceRecord.source_kind==source_kind.upper())
    rows=list(db.scalars(stmt.order_by(ApprovedSourceRecord.name.asc())))
    return [ApprovedOperationalSource(str(r.source_uuid),str(r.source_kind),str(r.name),str(r.domain),str(r.base_url),str(r.activation_status))
            for r in rows if str(r.activation_status).upper()=="ACTIVE"]

def approved_canonical_categories(db: Session) -> list[ApprovedCanonicalCategory]:
    rows=list(db.scalars(select(CanonicalCategoryRecord).where(CanonicalCategoryRecord.active.is_(True)).order_by(CanonicalCategoryRecord.name.asc())))
    return [ApprovedCanonicalCategory(str(r.category_uuid),str(r.name),str(r.parent_uuid) if r.parent_uuid else None,bool(r.active)) for r in rows]

def find_approved_source_by_domain(db: Session, domain_or_url: str, *, source_kind: str | None=None) -> ApprovedOperationalSource | None:
    wanted=normalize_domain(domain_or_url)
    for src in approved_operational_sources(db, source_kind=source_kind):
        if normalize_domain(src.domain)==wanted or normalize_domain(src.base_url)==wanted:
            return src
    return None

def require_approved_supplier(db: Session, domain_or_url: str) -> ApprovedOperationalSource:
    src=find_approved_source_by_domain(db,domain_or_url,source_kind="SUPPLIER")
    if src is None:
        raise ValueError(f"Supplier is not an approved ACTIVE source: {domain_or_url}")
    return src
