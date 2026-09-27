from __future__ import annotations
from dataclasses import dataclass
from app.services.unified_product_intake import UnifiedIntakePlan
from app.services.content_readiness_gate import ContentReadiness
from app.services.price_vat_gate import PriceVatDecision

@dataclass(frozen=True)
class UnifiedQAResult:
    blockers:tuple[str,...]
    ready_for_targets:bool
    publish_enabled:bool=False
    write_performed:bool=False

def evaluate_unified_qa(*, intake:UnifiedIntakePlan, content:ContentReadiness,
                        price_vat:PriceVatDecision)->UnifiedQAResult:
    blockers=list(intake.blockers)
    blockers.extend(content.blockers)
    blockers.extend(price_vat.blockers)
    if not intake.can_continue: blockers.append("INTAKE_NOT_READY")
    if not content.ready: blockers.append("CONTENT_NOT_READY")
    if not price_vat.ready: blockers.append("PRICE_VAT_NOT_READY")
    for item in intake.items:
        if item.identity_state not in ("NEW","EXISTING"):
            blockers.append("IDENTITY_NOT_READY:"+item.source_ref)
    blockers=tuple(dict.fromkeys(blockers))
    return UnifiedQAResult(blockers=blockers,ready_for_targets=not blockers,
                           publish_enabled=False,write_performed=False)
