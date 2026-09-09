from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN = REPO_ROOT / "admin-platform"
ROUTER = ADMIN / "app" / "routers" / "phase46_r3_content_intelligence.py"
SVC = ADMIN / "app" / "services" / "v073_phase46" / "content_manufacturer_intelligence.py"

def test_real_layout_contract():
    assert Path(__file__).resolve().parent.name == "tests"
    assert REPO_ROOT.name == "M99-Knowledge-Platform"
    assert ADMIN.name == "admin-platform"
    assert ROUTER.exists()
    assert SVC.exists()
