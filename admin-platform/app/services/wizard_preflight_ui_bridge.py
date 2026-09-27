from __future__ import annotations
from typing import Any, Iterable
from app.services.wizard_unified_preflight import build_unified_wizard_preflight

def build_wizard_preflight_view(*, supplier_key: str, hydrated_products: list[Any],
                                requested_targets: Iterable[str]) -> dict[str, object]:
    result = build_unified_wizard_preflight(
        supplier_key=supplier_key,
        hydrated_products=hydrated_products,
        requested_targets=requested_targets,
    )
    targets = result["targets"]
    evidence = result["evidence"]
    return {
        "supplier_key": result["supplier_key"],
        "product_count": evidence["count"],
        "requested_targets": list(targets["requested_targets"]),
        "authorized_targets": list(targets["authorized_targets"]),
        "ready_targets": list(targets["ready_targets"]),
        "blocked_targets": list(targets["blocked_targets"]),
        "blockers": list(result["blockers"]),
        "ready_for_preflight": bool(result["ready_for_preflight"]),
        "publish_enabled": False,
        "write_performed": False,
    }
