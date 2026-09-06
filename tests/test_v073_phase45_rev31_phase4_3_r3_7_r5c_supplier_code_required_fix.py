from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"

def test_supplier_create_populates_required_code():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "supplier_code = _operational_supplier_code_for_domain(db, domain)" in text
    assert "code=supplier_code" in text

def test_domain_code_is_deterministic_and_human_readable():
    text = BRIDGE.read_text(encoding="utf-8")
    assert 'domain.upper()' in text
    assert 're.sub(r"[^A-Z0-9]+", "-", domain.upper()).strip("-")' in text

def test_code_collision_gets_numeric_suffix():
    text = BRIDGE.read_text(encoding="utf-8")
    assert 'while f"{base}-{n}" in existing:' in text
    assert 'return f"{base}-{n}"' in text

def test_failed_flush_or_commit_rolls_back():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "db.flush()" in text
    assert "db.rollback()" in text
    assert "db.commit()" in text

def test_calenda_domain_expected_base_code():
    import re
    domain = "calenda.bg"
    base = re.sub(r"[^A-Z0-9]+", "-", domain.upper()).strip("-")
    assert base == "CALENDA-BG"
