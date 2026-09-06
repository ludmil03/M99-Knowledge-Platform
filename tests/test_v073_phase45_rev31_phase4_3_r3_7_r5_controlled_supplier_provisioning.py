from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"
ROUTER = ROOT / "admin-platform/app/routers/r37_add_products_flow.py"
PREP = ROOT / "admin-platform/app/templates/add_products/r37_prepare.html"

def test_superadmin_only():
    x=BRIDGE.read_text(encoding="utf-8")
    assert 'if not getattr(user, "is_superuser", False):' in x
    assert "Super Admin permission is required." in x

def test_explicit_post_route():
    x=ROUTER.read_text(encoding="utf-8")
    assert '@router.post("/provision-operational-supplier"' in x

def test_ui_only_when_missing_bridge_and_superadmin():
    x=PREP.read_text(encoding="utf-8")
    assert "not bridge.bridge_ready and user.is_superuser" in x

def test_duplicate_protection():
    x=BRIDGE.read_text(encoding="utf-8")
    assert "Operational Supplier already exists; no duplicate created." in x
    assert "Provisioning uniqueness check failed" in x

def test_source_governance_not_mutated():
    x=BRIDGE.read_text(encoding="utf-8")
    assert "source.domain =" not in x
    assert "source.base_url =" not in x
    assert "source.active =" not in x

def test_no_channel_publish_or_stock_write():
    x=BRIDGE.read_text(encoding="utf-8").lower()
    assert "prestashop" not in x
    assert "publish" not in x
    assert "inventorymapping" not in x
