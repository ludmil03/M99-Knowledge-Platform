from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "admin-platform/app/routers/r37_add_products_flow.py"
BRIDGE = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"
WORKSPACE = ROOT / "admin-platform/app/templates/add_products/workspace.html"

def test_explicit_prepare_then_explicit_draft():
    r = ROUTER.read_text(encoding="utf-8")
    w = WORKSPACE.read_text(encoding="utf-8")
    assert '/add-products/r37/prepare' in w
    assert '@router.post("/prepare"' in r
    assert '@router.post("/create-draft"' in r
    assert "resolve_identity_then_create_draft" in r

def test_identity_blocks_ambiguous_and_unresolved():
    b = BRIDGE.read_text(encoding="utf-8")
    assert 'identity["state"] not in {"NEW", "EXISTING"}' in b
    assert '"created": False' in b

def test_only_first_live_target_m99eu():
    b = BRIDGE.read_text(encoding="utf-8")
    assert 'ALLOWED_R37_TARGETS = ("m99eu",)' in b

def test_no_publish_write_in_r37_router():
    r = ROUTER.read_text(encoding="utf-8").lower()
    assert "publish" not in r
    assert "prestashop" not in r
    assert "delete" not in r

def test_canonical_preview_rehydrates_from_unified_supplier_connector():
    b = BRIDGE.read_text(encoding="utf-8")
    r = ROUTER.read_text(encoding="utf-8")
    assert "hydrate_product(source, product_url)" in b
    assert "prepare_canonical_preview" in r

def test_supplier_availability_not_promoted_to_owned_stock():
    b = BRIDGE.read_text(encoding="utf-8")
    assert "inventory" not in b.lower()
    assert "stock" not in b.lower()
