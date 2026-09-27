from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable
from app.services.supplier_evidence_runtime import normalize_supplier_evidence
from app.services.channel_registry_bridge import resolve_governed_target_scope

@dataclass(frozen=True)
class IntakeItem:
    source_ref: str
    identity_state: str
    evidence: Any

@dataclass(frozen=True)
class UnifiedIntakePlan:
    supplier_key: str
    items: tuple[IntakeItem, ...]
    requested_targets: tuple[str, ...]
    authorized_targets: tuple[str, ...]
    ready_targets: tuple[str, ...]
    blocked_targets: tuple[str, ...]
    blockers: tuple[str, ...]
    can_continue: bool
    write_performed: bool = False

def build_unified_intake_plan(*, supplier_key: str, hydrated_products: Iterable[Any],
                              requested_targets: Iterable[str]) -> UnifiedIntakePlan:
    items=[]
    blockers=[]
    for hydrated in hydrated_products:
        evidence=normalize_supplier_evidence(supplier_key, hydrated)
        identity=evidence.identity_facts
        source_ref=str((identity.get("supplier_sku") or identity.get("product_id") or identity.get("name")).value)
        items.append(IntakeItem(source_ref=source_ref, identity_state="PENDING_IDENTITY", evidence=evidence))
    scope=resolve_governed_target_scope(requested_targets)
    if not items: blockers.append("NO_PRODUCT_EVIDENCE")
    if not scope["ready_targets"]: blockers.append("NO_READY_TARGET")
    return UnifiedIntakePlan(
        supplier_key=str(supplier_key or "").strip().upper(), items=tuple(items),
        requested_targets=tuple(scope["requested_targets"]),
        authorized_targets=tuple(scope["authorized_targets"]),
        ready_targets=tuple(scope["ready_targets"]),
        blocked_targets=tuple(scope["blocked_targets"]),
        blockers=tuple(blockers), can_continue=not blockers, write_performed=False)
