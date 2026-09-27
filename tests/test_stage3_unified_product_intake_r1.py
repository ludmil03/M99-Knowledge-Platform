from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.unified_product_intake import build_unified_intake_plan
def p():
 return PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
def test_golden_bultex_intake():
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p()],requested_targets=["m99.eu"])
 assert x.supplier_key=="BULTEX99" and len(x.items)==1 and x.items[0].identity_state=="PENDING_IDENTITY"
 assert x.ready_targets==("m99.eu",) and x.can_continue and not x.write_performed
def test_toplinka_remains_blocked_from_ready():
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p()],requested_targets=["toplinka.com"])
 assert x.authorized_targets==("toplinka.com",) and x.ready_targets==() and "NO_READY_TARGET" in x.blockers
def test_empty_evidence_blocks():
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[],requested_targets=["m99.eu"])
 assert not x.can_continue and "NO_PRODUCT_EVIDENCE" in x.blockers
def test_unknown_supplier_fails_closed():
 with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
  build_unified_intake_plan(supplier_key="FEYA",hydrated_products=[object()],requested_targets=["m99.eu"])
