from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "admin-platform/app/services/v073_phase45/r37_import_bridge.py"

def test_append_only_audit():
    x=BRIDGE.read_text(encoding="utf-8")
    assert "r37_operational_supplier_provisioning.jsonl" in x
    assert '.open("a", encoding="utf-8")' in x
    assert '"actor_user_id"' in x
    assert '"approved_source_uuid"' in x
    assert '"operational_supplier_id"' in x

def test_outcomes():
    x=BRIDGE.read_text(encoding="utf-8")
    assert 'outcome="CREATED"' in x
    assert 'outcome="ALREADY_EXISTS"' in x
