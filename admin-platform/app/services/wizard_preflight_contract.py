from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable
from app.services.wizard_supplier_evidence_bridge import build_wizard_evidence_preview
from app.services.product_import_wizard import resolve_target_scope

@dataclass(frozen=True)
class WizardPreflight:
    supplier_key: str
    evidence: dict[str, object]
    requested_targets: tuple[str,...]
    authorized_targets: tuple[str,...]
    ready_targets: tuple[str,...]
    blocked_targets: tuple[str,...]
    can_continue: bool
    write_performed: bool = False

def build_wizard_preflight(*, supplier_key:str, hydrated_products:list[Any],
                           requested_targets:Iterable[str]) -> WizardPreflight:
    evidence=build_wizard_evidence_preview(supplier_key,hydrated_products)
    scope=resolve_target_scope(requested_targets)
    can_continue=bool(evidence["count"]) and bool(scope["ready_targets"])
    return WizardPreflight(
        supplier_key=str(supplier_key or "").strip().upper(),
        evidence=evidence,
        requested_targets=tuple(scope["requested_targets"]),
        authorized_targets=tuple(scope["authorized_targets"]),
        ready_targets=tuple(scope["ready_targets"]),
        blocked_targets=tuple(scope["blocked_targets"]),
        can_continue=can_continue,
        write_performed=False,
    )
