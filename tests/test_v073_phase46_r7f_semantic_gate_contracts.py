
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
SVC=(ROOT/"admin-platform/app/services/v073_phase46/canonical_live_pilot.py").read_text(encoding="utf-8")

def _pairs():
    tree=ast.parse(SVC)
    return [(ast.unparse(n.test),ast.unparse(n)) for n in ast.walk(tree) if isinstance(n,ast.If)]

def test_integrated_enable_gate_is_semantic():
    pairs=_pairs()
    assert "effective_m99eu_credentials()" in SVC
    assert any(c=="not enabled" and "CanonicalPilotError" in b for c,b in pairs)

def test_api_key_gate_is_semantic():
    pairs=_pairs()
    assert any("re.fullmatch" in c and "api_key" in c and "CanonicalPilotError" in b for c,b in pairs)

def test_live_write_safety_gates_remain():
    for frag in (
        'getattr(user,"is_superuser",False)',
        'str(getattr(job,"status","")).upper()!="DRAFT"',
        '"m99eu" not in requested or "m99eu" not in authorized',
        'str(confirmation or "").strip()!=CONFIRMATION',
        "validate_preview(preview)",
        "_find_existing",
        "_readback",
        'tag("active","0")',
        'tag("available_for_order","0")',
        'tag("visibility","none")',
    ):
        assert frag in SVC
