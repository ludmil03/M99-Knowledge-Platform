from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.wizard_preflight_contract import build_wizard_preflight

def product():
    return PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
      supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")

def test_ready_target_can_continue_but_never_writes():
    r=build_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["m99.eu"])
    assert r.can_continue is True and r.write_performed is False
    assert r.ready_targets==("m99.eu",)

def test_unknown_target_blocked():
    r=build_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["unknown.example"])
    assert r.can_continue is False and r.blocked_targets==("unknown.example",)

def test_toplinka_current_foundation_is_blocked_not_silently_enabled():
    r=build_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[product()],requested_targets=["toplinka.com"])
    assert r.can_continue is False and r.write_performed is False
    assert "toplinka.com" in r.blocked_targets

def test_empty_evidence_cannot_continue_even_with_ready_target():
    r=build_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[],requested_targets=["m99.eu"])
    assert r.can_continue is False

def test_mixed_targets_intersection():
    r=build_wizard_preflight(supplier_key="BULTEX99",hydrated_products=[product()],
      requested_targets=["m99.eu","alviro.ro","toplinka.com","m99.eu"])
    assert r.requested_targets==("m99.eu","alviro.ro","toplinka.com")
    assert r.ready_targets==("m99.eu",)
    assert set(r.blocked_targets)=={"alviro.ro","toplinka.com"}
