from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "scripts/r37r6_identity_persistence_preflight.py",
    ROOT / "scripts/r37r6_apply_identity_persistence_bootstrap.py",
)

def test_r37r6_scripts_add_admin_platform_to_sys_path():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "Path(__file__).resolve().parents[1] / 'admin-platform'" in text
        assert "sys.path.insert(0, str(ADMIN))" in text
        assert "from app.core.config import settings" in text
