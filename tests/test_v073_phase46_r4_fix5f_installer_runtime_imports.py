from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN = REPO_ROOT / "admin-platform"
ROUTER = ADMIN / "app" / "routers" / "phase46_r3_content_intelligence.py"
SVC = ADMIN / "app" / "services" / "v073_phase46" / "content_manufacturer_intelligence.py"

def test_installed_confirm_context_contract():
    s=ROUTER.read_text(encoding="utf-8")
    assert 'publish_review_url=""' in s
    assert "publish_review_url=publish_review_url" in s
    assert "Confirmed data was produced, but the review UI failed safely:" in s

def test_installed_quality_contract():
    s=SVC.read_text(encoding="utf-8")
    assert "if similarity>=0.75:" in s
    assert '"meta_short_threshold":0.75' in s

def test_paths_match_real_repository_layout():
    assert REPO_ROOT.name == "M99-Knowledge-Platform"
    assert ADMIN.name == "admin-platform"
    assert ROUTER.exists()
    assert SVC.exists()
