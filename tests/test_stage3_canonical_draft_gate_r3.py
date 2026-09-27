from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.unified_product_intake import build_unified_intake_plan
from app.services.unified_identity_gate import *
from app.services.canonical_draft_gate import build_canonical_drafts
def base(state=IdentityState.NEW,mid=None):
 p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p],requested_targets=["m99.eu"])
 return apply_identity_decisions(x,{"06100764.36":IdentityDecision("06100764.36",state,mid)})
def test_new_builds_draft_without_allocating_m99_id():
 d=build_canonical_drafts(base())[0]
 assert d.name=="UNO LOW" and d.lifecycle=="draft" and d.existing_m99_id is None
def test_existing_reuses_explicit_id():
 d=build_canonical_drafts(base(IdentityState.EXISTING,"M99 100018"),{"06100764.36":"M99 100018"})[0]
 assert d.existing_m99_id=="M99 100018"
def test_blocked_intake_cannot_become_canonical():
 p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p],requested_targets=["toplinka.com"])
 with pytest.raises(ValueError,match="INTAKE_PLAN_BLOCKED"):build_canonical_drafts(x)
