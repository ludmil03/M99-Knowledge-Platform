from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from app.services.unified_product_intake import build_unified_intake_plan, UnifiedIntakePlan
from app.services.unified_identity_gate import IdentityDecision, apply_identity_decisions
from app.services.canonical_draft_gate import build_canonical_drafts, CanonicalDraft
from app.services.content_readiness_gate import LanguageContent, evaluate_content_readiness, ContentReadiness
from app.services.price_vat_gate import evaluate_price_vat, PriceVatDecision
from app.services.unified_qa_readiness import evaluate_unified_qa, UnifiedQAResult
from app.services.wizard_qa_bridge import build_wizard_qa_view, WizardQAView

@dataclass(frozen=True)
class ProductQualityInput:
    source_ref: str
    content: Mapping[str, LanguageContent]
    supplier_gross: Any
    margin_percent: Any
    vat_rate: Any
    vat_proven: bool

@dataclass(frozen=True)
class OrchestratedProduct:
    source_ref: str
    canonical: CanonicalDraft
    content: ContentReadiness
    price_vat: PriceVatDecision
    qa: UnifiedQAResult
    qa_view: WizardQAView

@dataclass(frozen=True)
class MilestoneAPlan:
    supplier_key: str
    intake: UnifiedIntakePlan
    products: tuple[OrchestratedProduct, ...]
    ready_targets: tuple[str, ...]
    blocked_targets: tuple[str, ...]
    blockers: tuple[str, ...]
    ready_for_operator_review: bool
    publish_enabled: bool = False
    write_performed: bool = False

def _dedupe(values: Iterable[str]) -> tuple[str,...]:
    return tuple(dict.fromkeys(str(x) for x in values if str(x)))

def build_milestone_a_plan(*, supplier_key: str, hydrated_products: list[Any],
                           requested_targets: Iterable[str],
                           identity_decisions: Mapping[str, IdentityDecision],
                           quality_inputs: Mapping[str, ProductQualityInput],
                           existing_ids: Mapping[str,str] | None = None) -> MilestoneAPlan:
    intake=build_unified_intake_plan(supplier_key=supplier_key,
        hydrated_products=hydrated_products, requested_targets=requested_targets)
    identified=apply_identity_decisions(intake, identity_decisions)
    if not identified.can_continue:
        return MilestoneAPlan(identified.supplier_key,identified,(),
            tuple(identified.ready_targets),tuple(identified.blocked_targets),
            _dedupe(identified.blockers),False)
    canon=build_canonical_drafts(identified,dict(existing_ids or {}))
    products=[]; blockers=[]
    for draft in canon:
        q=quality_inputs.get(draft.source_ref)
        if q is None:
            blockers.append("QUALITY_INPUT_MISSING:"+draft.source_ref); continue
        if q.source_ref != draft.source_ref:
            blockers.append("QUALITY_SOURCE_REF_MISMATCH:"+draft.source_ref); continue
        content=evaluate_content_readiness(draft,q.content)
        price=evaluate_price_vat(supplier_gross=q.supplier_gross,
            margin_percent=q.margin_percent,vat_rate=q.vat_rate,vat_proven=q.vat_proven)
        qa=evaluate_unified_qa(intake=identified, content=content, price_vat=price)
        view=build_wizard_qa_view(qa)
        products.append(OrchestratedProduct(draft.source_ref,draft,content,price,qa,view))
        blockers.extend(qa.blockers)
    if len(products)!=len(canon): blockers.append("PRODUCT_QUALITY_INCOMPLETE")
    blockers=_dedupe(blockers)
    ready=(not blockers and bool(products) and bool(identified.ready_targets)
           and all(x.qa.ready_for_targets for x in products))
    return MilestoneAPlan(identified.supplier_key,identified,tuple(products),
        tuple(identified.ready_targets),tuple(identified.blocked_targets),
        blockers,ready,False,False)
