from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "admin-platform/app/services/v073_phase45/calenda_public_connector.py"
R37 = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"

def test_gate_uses_exact_variant_availability():
    text = CAL.read_text(encoding="utf-8")
    assert 'variant_evidence["has_availability_evidence"]' in text
    assert '"AVAILABLE BY VARIANT"' in text
    assert '"OUT OF STOCK BY VARIANT"' in text

def test_no_inventory_or_channel_write_added():
    cal = CAL.read_text(encoding="utf-8").lower()
    bridge = R37.read_text(encoding="utf-8").lower()
    assert "inventorymapping" not in cal
    assert "prestashop" not in bridge
    assert "publish" not in bridge

def test_supplier_stock_separation_remains_explicit():
    text = CAL.read_text(encoding="utf-8")
    assert "M99-owned stock" in text
