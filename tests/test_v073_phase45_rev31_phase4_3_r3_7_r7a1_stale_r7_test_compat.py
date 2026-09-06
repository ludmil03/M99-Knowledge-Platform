from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R7 = ROOT / "tests/test_v073_phase45_rev31_phase4_3_r3_7_r7_complete_identity_manufacturer_images.py"
RECON = ROOT / "admin-platform/app/services/v073_phase45/r37_identity_persistence_reconcile.py"

def test_stale_common_base_assertion_removed():
    r7 = R7.read_text(encoding="utf-8")
    assert 'assert "Base.metadata.tables.items()" in text' not in r7

def test_r7_and_r7a_now_agree_on_discovery_contract():
    recon = RECON.read_text(encoding="utf-8")
    assert "Base.metadata" not in recon
    assert "_discover_identity_tables" in recon
    assert "pkgutil.walk_packages" in recon
