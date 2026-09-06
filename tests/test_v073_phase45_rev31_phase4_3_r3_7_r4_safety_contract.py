from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"
PREP = ROOT / "admin-platform/app/templates/add_products/r37_prepare.html"

def test_operational_bridge_lookup_itself_remains_read_only():
    text = BRIDGE.read_text(encoding="utf-8")
    start = text.index("def operational_supplier_bridge(")
    end = text.index("\ndef _r37_operational_audit_path(", start)
    lookup = text[start:end].lower()
    assert "supplier(" not in lookup
    assert ".add(" not in lookup
    assert ".delete(" not in lookup
    assert ".commit(" not in lookup

def test_bridge_ready_requires_exactly_one_match():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "if len(matches) == 1:" in text
    assert "if len(matches) > 1:" in text
    assert "will not choose silently" in text

def test_prepare_button_still_depends_on_bridge_ready():
    text = PREP.read_text(encoding="utf-8")
    assert "{% if bridge.bridge_ready %}" in text
    assert "Потвърди Identity и създай DRAFT" in text

def test_no_channel_publish_or_stock_write_added():
    text = BRIDGE.read_text(encoding="utf-8").lower()
    assert "prestashop" not in text
    assert "publish" not in text
    assert "inventorymapping" not in text
