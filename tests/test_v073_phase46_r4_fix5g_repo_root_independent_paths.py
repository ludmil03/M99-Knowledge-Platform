from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN = REPO_ROOT / "admin-platform"
ROUTER = ADMIN / "app" / "routers" / "phase46_r3_content_intelligence.py"
SVC = ADMIN / "app" / "services" / "v073_phase46" / "content_manufacturer_intelligence.py"

def test_admin_root_is_derived_from_real_repo_layout():
    assert REPO_ROOT.name == "M99-Knowledge-Platform"
    assert ADMIN == REPO_ROOT / "admin-platform"
    assert ROUTER.exists()
    assert SVC.exists()
