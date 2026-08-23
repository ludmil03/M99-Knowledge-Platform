from datetime import datetime, timezone
from sqlalchemy import select
from app.persistence.v073_phase4.database import make_session_factory
from app.persistence.v073_phase4.models import IdentityResolution

def list_identity_review_queue(database_url):
    f=make_session_factory(database_url)
    with f() as s:
        rows=s.scalars(select(IdentityResolution).where(IdentityResolution.requires_human_review.is_(True)).order_by(IdentityResolution.created_at)).all()
        return [{"resolution_id":r.id,"source_type":r.source_type,"source_record_key":r.source_record_key,
                 "supplier_reference":r.supplier_reference,"manufacturer_reference":r.manufacturer_reference,
                 "ean_gtin":r.ean_gtin,"name":r.normalized_name,"brand_name":r.brand_name,
                 "state":r.resolution_state,"confidence":r.confidence} for r in rows]

def decide_identity_review(database_url, *, resolution_id, reviewer, decision, matched_m99_product_id=None):
    if decision not in {"LINK_EXISTING","CONFIRM_NEW","KEEP_UNRESOLVED"}: raise ValueError("Invalid decision")
    f=make_session_factory(database_url)
    with f.begin() as s:
        r=s.get(IdentityResolution,resolution_id)
        if not r: raise ValueError("Resolution not found")
        if decision=="LINK_EXISTING" and not matched_m99_product_id: raise ValueError("M99 product ID required")
        r.reviewed_by=reviewer; r.reviewed_at=datetime.now(timezone.utc); r.review_decision=decision; r.requires_human_review=False
        if decision=="LINK_EXISTING":
            r.resolution_state="EXISTING"; r.matched_m99_product_id=matched_m99_product_id; r.confidence=100
        elif decision=="CONFIRM_NEW":
            r.resolution_state="NEW"; r.matched_m99_product_id=None
        else:
            r.resolution_state="UNRESOLVED"; r.matched_m99_product_id=None
        return {"resolution_id":r.id,"state":r.resolution_state,"matched_m99_product_id":r.matched_m99_product_id}
