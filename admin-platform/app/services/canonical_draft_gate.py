from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.services.unified_product_intake import UnifiedIntakePlan
@dataclass(frozen=True)
class CanonicalDraft:
    source_ref:str
    identity_state:str
    existing_m99_id:str|None
    name:str
    lifecycle:str="draft"
    evidence:Any=None
def build_canonical_drafts(plan:UnifiedIntakePlan, existing_ids:dict[str,str]|None=None)->tuple[CanonicalDraft,...]:
    existing_ids=existing_ids or {}; out=[]
    if not plan.can_continue: raise ValueError("INTAKE_PLAN_BLOCKED")
    for item in plan.items:
        if item.identity_state not in ("NEW","EXISTING"): raise ValueError("IDENTITY_NOT_RESOLVED:"+item.source_ref)
        m99_id=existing_ids.get(item.source_ref)
        if item.identity_state=="EXISTING" and not m99_id: raise ValueError("EXISTING_REQUIRES_M99_ID")
        if item.identity_state=="NEW" and m99_id: raise ValueError("NEW_MUST_NOT_HAVE_M99_ID")
        fact=item.evidence.identity_facts.get("name")
        name=str(fact.value).strip() if fact else ""
        if not name: raise ValueError("CANONICAL_NAME_REQUIRED")
        out.append(CanonicalDraft(item.source_ref,item.identity_state,m99_id,name,"draft",item.evidence))
    return tuple(out)
