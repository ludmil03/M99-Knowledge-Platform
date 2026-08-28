from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_phase3_payload_files_exist():
    expected=[
        "admin-platform/app/routers/rev31_source_category_governance.py",
        "admin-platform/app/templates/rev31_governance/base.html",
        "admin-platform/app/templates/rev31_governance/dashboard.html",
        "admin-platform/app/templates/rev31_governance/sources.html",
        "admin-platform/app/templates/rev31_governance/categories.html",
        "admin-platform/app/templates/rev31_governance/approvals.html",
    ]
    for rel in expected:
        assert (ROOT/rel).exists(), rel

def test_router_contract_and_no_external_write():
    text=(ROOT/"admin-platform/app/routers/rev31_source_category_governance.py").read_text(encoding="utf-8")
    assert 'prefix="/rev31-governance"' in text
    assert "propose_source(" in text
    assert "propose_category(" in text
    assert "approve_source(" in text
    assert "approve_category(" in text
    assert "is_superadmin" in text
    lowered=text.lower()
    for bad in ("requests.post(", "requests.put(", "requests.delete(", "httpx.post(", "httpx.put(", "httpx.delete("):
        assert bad not in lowered

def test_templates_preserve_governance_messages():
    src=(ROOT/"admin-platform/app/templates/rev31_governance/sources.html").read_text(encoding="utf-8")
    app=(ROOT/"admin-platform/app/templates/rev31_governance/approvals.html").read_text(encoding="utf-8")
    assert "Super Admin" in src
    assert "Approval Queue" in app


def test_governance_standalone_shell_has_return_paths():
    text=(ROOT/"admin-platform/app/templates/rev31_governance/base.html").read_text(encoding="utf-8")
    assert '{% extends "base.html" %}' not in text
    assert 'href="/">Dashboard</a>' in text
    assert 'href="/suppliers">Suppliers / Browse</a>' in text
    assert "⊕" not in text
    assert "▦" not in text
