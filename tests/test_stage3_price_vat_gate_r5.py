from decimal import Decimal
from app.services.price_vat_gate import *
def test_uno_low_persisted_policy_example():
 x=evaluate_price_vat(supplier_gross=Decimal("58.90"),margin_percent=Decimal("1.31"),vat_rate=Decimal("20"),vat_proven=True)
 assert x.target_gross==Decimal("58.13") and x.ready and not x.write_performed
def test_policy_boundaries_are_valid():
 assert evaluate_price_vat(supplier_gross=Decimal("100"),margin_percent=Decimal("1.00"),vat_rate=Decimal("20"),vat_proven=True).ready
 assert evaluate_price_vat(supplier_gross=Decimal("100"),margin_percent=Decimal("1.70"),vat_rate=Decimal("20"),vat_proven=True).ready
def test_margin_outside_policy_blocks():
 assert "MARGIN_OUTSIDE_POLICY" in evaluate_price_vat(supplier_gross=Decimal("100"),margin_percent=Decimal("1.71"),vat_rate=Decimal("20"),vat_proven=True).blockers
def test_unproven_vat_blocks():
 x=evaluate_price_vat(supplier_gross=Decimal("58.90"),margin_percent=Decimal("1.31"),vat_rate=None,vat_proven=False)
 assert not x.ready and "VAT_NOT_PROVEN" in x.blockers
def test_invalid_supplier_price_blocks():
 assert not evaluate_price_vat(supplier_gross=Decimal("0"),margin_percent=Decimal("1.31"),vat_rate=Decimal("20"),vat_proven=True).ready
