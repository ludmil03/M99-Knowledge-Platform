from __future__ import annotations
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Mapping
from app.services.unified_product_intake import UnifiedIntakePlan, IntakeItem

class IdentityState(StrEnum):
    NEW="NEW"
    EXISTING="EXISTING"
    AMBIGUOUS="AMBIGUOUS"
    UNRESOLVED="UNRESOLVED"

@dataclass(frozen=True)
class IdentityDecision:
    source_ref: str
    state: IdentityState
    m99_id: str | None = None
    evidence: str = ""

def apply_identity_decisions(plan: UnifiedIntakePlan, decisions: Mapping[str, IdentityDecision]) -> UnifiedIntakePlan:
    items=[]; blockers=list(plan.blockers)
    for item in plan.items:
        d=decisions.get(item.source_ref)
        if d is None:
            items.append(replace(item, identity_state=IdentityState.UNRESOLVED.value))
            blockers.append("IDENTITY_UNRESOLVED:"+item.source_ref); continue
        if d.source_ref != item.source_ref:
            raise ValueError("IDENTITY_SOURCE_REF_MISMATCH")
        if d.state == IdentityState.EXISTING and not d.m99_id:
            raise ValueError("EXISTING_REQUIRES_M99_ID")
        if d.state == IdentityState.NEW and d.m99_id:
            raise ValueError("NEW_MUST_NOT_PREALLOCATE_M99_ID")
        items.append(replace(item, identity_state=d.state.value))
        if d.state in (IdentityState.AMBIGUOUS,IdentityState.UNRESOLVED):
            blockers.append("IDENTITY_"+d.state.value+":"+item.source_ref)
    blockers=tuple(dict.fromkeys(blockers))
    return replace(plan,items=tuple(items),blockers=blockers,can_continue=(not blockers),write_performed=False)
