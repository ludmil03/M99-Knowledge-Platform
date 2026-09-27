from __future__ import annotations
from typing import Any, Iterable
from app.services.wizard_supplier_evidence_bridge import build_wizard_evidence_preview
from app.services.channel_registry_bridge import resolve_governed_target_scope

def build_unified_wizard_preflight(*, supplier_key: str, hydrated_products: list[Any],
                                   requested_targets: Iterable[str]) -> dict[str, object]:
    evidence = build_wizard_evidence_preview(supplier_key, hydrated_products)
    targets = resolve_governed_target_scope(requested_targets)
    blockers = []
    if not evidence["count"]:
        blockers.append("NO_PRODUCT_EVIDENCE")
    if not targets["ready_targets"]:
        blockers.append("NO_READY_TARGET")
    return {
        "supplier_key": str(supplier_key or "").strip().upper(),
        "evidence": evidence,
        "targets": targets,
        "blockers": blockers,
        "ready_for_preflight": not blockers,
        "write_performed": False,
    }
