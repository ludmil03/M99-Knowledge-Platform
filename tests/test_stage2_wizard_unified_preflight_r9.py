from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.wizard_unified_preflight import build_unified_wizard_preflight

def p():
    return PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
        supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")

def test_bultex_ready_target_no_write():
    r=build_unified_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[p()],requested_targets=["m99.eu"])
    assert r["ready_for_preflight"] is True and r["write_performed"] is False
    assert r["targets"]["ready_targets"]==["m99.eu"]

def test_toplinka_visible_authorized_but_blocks_until_ready():
    r=build_unified_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[p()],requested_targets=["toplinka.com"])
    assert r["targets"]["authorized_targets"]==["toplinka.com"]
    assert r["targets"]["ready_targets"]==[]
    assert "NO_READY_TARGET" in r["blockers"]

def test_empty_evidence_blocks():
    r=build_unified_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[],requested_targets=["m99.eu"])
    assert r["ready_for_preflight"] is False and "NO_PRODUCT_EVIDENCE" in r["blockers"]

def test_unknown_supplier_still_fails_closed():
    import pytest
    with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
        build_unified_wizard_preflight(supplier_key="FEYA",hydrated_products=[object()],requested_targets=["m99.eu"])
