from pathlib import Path
import json

def test_r7k31_policy_is_space_six_digits():
    p=json.loads(Path("config/identity/m99_identity_policy.json").read_text(encoding="utf-8"))
    assert p["format"]=="M99 000001"
    assert p["regex"]=="^M99 [0-9]{6}$"

def test_r7k31_superseding_decision_is_explicit():
    p=Path("DECISION_REGISTRY.yaml").read_text(encoding="utf-8")
    assert "id: ID-002A" in p
    assert "supersedes: ID-002" in p
    assert 'next_allocation_floor: "M99 100018"' in p

def test_r7k31_historical_test_no_longer_freezes_obsolete_allocator():
    p=Path("tests/test_v073_phase46_r7k2_palltex_bwolf_manufacturer_durable.py").read_text(encoding="utf-8")
    assert 'return f"M99-{high+1}"' not in p
    assert 'return f"M99 {high+1:06d}"' in p

def test_r7k31_allocator_matches_policy():
    p=Path("admin-platform/app/services/v073_phase46/canonical_identity_allocator.py").read_text(encoding="utf-8")
    assert 'NORMATIVE_M99_RE = re.compile(r"^M99 ([0-9]{6})$")' in p
    assert 'return f"M99 {high+1:06d}"' in p
    assert "RESERVED_CANONICAL_FLOOR = 100017" in p
