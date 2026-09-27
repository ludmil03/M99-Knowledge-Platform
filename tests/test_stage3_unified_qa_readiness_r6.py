from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.unified_product_intake import build_unified_intake_plan
from app.services.unified_identity_gate import *
from app.services.canonical_draft_gate import build_canonical_drafts
from app.services.content_readiness_gate import *
from app.services.price_vat_gate import evaluate_price_vat
from app.services.unified_qa_readiness import evaluate_unified_qa
def ready_parts():
 p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
 i=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p],requested_targets=["m99.eu"])
 i=apply_identity_decisions(i,{"06100764.36":IdentityDecision("06100764.36",IdentityState.NEW)})
 d=build_canonical_drafts(i)[0]
 c=LanguageContent("UNO LOW","short","long technical evidence","meta","description")
 content=evaluate_content_readiness(d,{k:c for k in CANONICAL_LANGUAGES})
 price=evaluate_price_vat(supplier_gross=Decimal("58.90"),margin_percent=Decimal("1.31"),vat_rate=Decimal("20"),vat_proven=True)
 return i,content,price
def test_golden_pipeline_ready_but_publish_stays_disabled():
 i,c,p=ready_parts();q=evaluate_unified_qa(intake=i,content=c,price_vat=p)
 assert q.ready_for_targets and not q.blockers and not q.publish_enabled and not q.write_performed
def test_content_blocker_propagates_fail_closed():
 i,c,p=ready_parts();bad=evaluate_content_readiness(c.draft,{"bg":c.content["bg"]})
 q=evaluate_unified_qa(intake=i,content=bad,price_vat=p)
 assert not q.ready_for_targets and "CONTENT_NOT_READY" in q.blockers
def test_vat_blocker_propagates_fail_closed():
 i,c,p=ready_parts();bad=evaluate_price_vat(supplier_gross=Decimal("58.90"),margin_percent=Decimal("1.31"),vat_rate=None,vat_proven=False)
 q=evaluate_unified_qa(intake=i,content=c,price_vat=bad)
 assert not q.ready_for_targets and "VAT_NOT_PROVEN" in q.blockers
def test_publish_is_never_enabled_by_stage3_qa():
 i,c,p=ready_parts()
 assert evaluate_unified_qa(intake=i,content=c,price_vat=p).publish_enabled is False
