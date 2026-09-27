from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.wizard_preflight_ui_bridge import build_wizard_preflight_view

def product():
    return PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
        supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")

def test_ready_m99eu_is_visible_but_publish_stays_disabled():
    v=build_wizard_preflight_view(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["m99.eu"])
    assert v["ready_for_preflight"] is True
    assert v["ready_targets"]==["m99.eu"]
    assert v["publish_enabled"] is False and v["write_performed"] is False

def test_toplinka_visible_authorized_not_ready():
    v=build_wizard_preflight_view(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["toplinka.com"])
    assert v["authorized_targets"]==["toplinka.com"]
    assert v["ready_targets"]==[]
    assert v["blocked_targets"]==["toplinka.com"]
    assert "NO_READY_TARGET" in v["blockers"]
    assert v["publish_enabled"] is False

def test_unknown_target_is_blocked():
    v=build_wizard_preflight_view(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["unknown.example"])
    assert v["blocked_targets"]==["unknown.example"] and v["ready_for_preflight"] is False
