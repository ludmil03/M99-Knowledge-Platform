from __future__ import annotations
from dataclasses import dataclass
import json, re
from sqlalchemy import select
from app.persistence.v073_phase4.database import make_session_factory
from app.persistence.v073_phase4.models import IdentityExternalMapping, IdentityResolution, new_id

RESOLUTION_STATES={"NEW","EXISTING","AMBIGUOUS","UNRESOLVED"}
WEIGHTS={"EAN_GTIN":100,"MANUFACTURER_REFERENCE":95,"SUPPLIER_REFERENCE":85}

@dataclass(frozen=True)
class IncomingIdentity:
    source_type: str
    source_id: str|None
    source_record_key: str
    source_snapshot_id: str|None=None
    supplier_reference: str|None=None
    manufacturer_reference: str|None=None
    ean_gtin: str|None=None
    name: str|None=None
    brand_name: str|None=None

def norm(v):
    if not v: return None
    x=re.sub(r"\s+"," ",v).strip()
    return x or None

def candidates(i):
    out=[]
    if norm(i.ean_gtin): out.append(("EAN_GTIN",norm(i.ean_gtin)))
    if norm(i.manufacturer_reference): out.append(("MANUFACTURER_REFERENCE",norm(i.manufacturer_reference)))
    if norm(i.supplier_reference): out.append(("SUPPLIER_REFERENCE",norm(i.supplier_reference)))
    return out

def register_verified_mapping(database_url, *, m99_product_id, mapping_type, external_value, organization_id=None, source_id=None):
    if mapping_type not in WEIGHTS: raise ValueError("Unsupported mapping type")
    external_value=norm(external_value)
    if not external_value: raise ValueError("External value required")
    f=make_session_factory(database_url)
    with f.begin() as s:
        row=s.scalar(select(IdentityExternalMapping).where(
            IdentityExternalMapping.mapping_type==mapping_type,
            IdentityExternalMapping.external_value==external_value))
        if row and row.m99_product_id != m99_product_id:
            raise ValueError("External identity already mapped to another M99 product")
        if not row:
            row=IdentityExternalMapping(id=new_id("mapping"),m99_product_id=m99_product_id,
                mapping_type=mapping_type,external_value=external_value,
                organization_id=organization_id,source_id=source_id,verified=True)
            s.add(row)
        else:
            row.verified=True
        s.flush()
        return {"m99_product_id":row.m99_product_id,"mapping_type":row.mapping_type,"external_value":row.external_value}

def resolve_identity(database_url, incoming:IncomingIdentity):
    matched={}
    f=make_session_factory(database_url)
    with f() as s:
        for typ,val in candidates(incoming):
            row=s.scalar(select(IdentityExternalMapping).where(
                IdentityExternalMapping.mapping_type==typ,
                IdentityExternalMapping.external_value==val,
                IdentityExternalMapping.verified.is_(True)))
            if row:
                matched.setdefault(row.m99_product_id,[]).append((typ,WEIGHTS[typ]))
    if len(matched)==1:
        pid,reasons=next(iter(matched.items())); state="EXISTING"; review=False; conf=max(x[1] for x in reasons); conflicts=[]
    elif len(matched)>1:
        pid=None; reasons=[]; state="AMBIGUOUS"; review=True; conf=0; conflicts=sorted(matched)
    elif candidates(incoming):
        pid=None; reasons=[]; state="NEW"; review=False; conf=0; conflicts=[]
    else:
        pid=None; reasons=[]; state="UNRESOLVED"; review=True; conf=0; conflicts=["NO_STABLE_EXTERNAL_IDENTIFIER"]
    with f.begin() as s:
        r=IdentityResolution(id=new_id("identity"),source_type=incoming.source_type,source_id=incoming.source_id,
            source_record_key=incoming.source_record_key,source_snapshot_id=incoming.source_snapshot_id,
            supplier_reference=norm(incoming.supplier_reference),manufacturer_reference=norm(incoming.manufacturer_reference),
            ean_gtin=norm(incoming.ean_gtin),normalized_name=norm(incoming.name),brand_name=norm(incoming.brand_name),
            resolution_state=state,matched_m99_product_id=pid,confidence=conf,
            match_reasons_json=json.dumps(reasons),conflict_reasons_json=json.dumps(conflicts),
            requires_human_review=review)
        s.add(r); s.flush(); rid=r.id
    return {"resolution_id":rid,"state":state,"matched_m99_product_id":pid,"confidence":conf,
            "requires_human_review":review,"match_reasons":[x[0] for x in reasons],"conflicts":conflicts}
