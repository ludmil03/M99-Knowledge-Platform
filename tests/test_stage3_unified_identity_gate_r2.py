from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.unified_product_intake import build_unified_intake_plan
from app.services.unified_identity_gate import *
def base():
 p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
 return build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p],requested_targets=["m99.eu"])
def test_new_identity_can_continue_without_allocating_id():
 x=apply_identity_decisions(base(),{"06100764.36":IdentityDecision("06100764.36",IdentityState.NEW)})
 assert x.items[0].identity_state=="NEW" and x.can_continue and not x.write_performed
def test_existing_requires_canonical_id():
 with pytest.raises(ValueError,match="EXISTING_REQUIRES_M99_ID"):
  apply_identity_decisions(base(),{"06100764.36":IdentityDecision("06100764.36",IdentityState.EXISTING)})
def test_existing_with_id_can_continue():
 x=apply_identity_decisions(base(),{"06100764.36":IdentityDecision("06100764.36",IdentityState.EXISTING,"M99 100018")})
 assert x.can_continue and x.items[0].identity_state=="EXISTING"
def test_ambiguous_blocks():
 x=apply_identity_decisions(base(),{"06100764.36":IdentityDecision("06100764.36",IdentityState.AMBIGUOUS)})
 assert not x.can_continue and "IDENTITY_AMBIGUOUS:06100764.36" in x.blockers
def test_missing_decision_becomes_unresolved_and_blocks():
 x=apply_identity_decisions(base(),{})
 assert not x.can_continue and x.items[0].identity_state=="UNRESOLVED"
def test_new_cannot_preallocate_id():
 with pytest.raises(ValueError,match="NEW_MUST_NOT_PREALLOCATE"):
  apply_identity_decisions(base(),{"06100764.36":IdentityDecision("06100764.36",IdentityState.NEW,"M99 100019")})
