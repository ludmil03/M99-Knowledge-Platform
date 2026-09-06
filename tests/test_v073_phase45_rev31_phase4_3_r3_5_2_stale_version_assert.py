from pathlib import Path
from app.routers import unified_add_products as router_module


def _workspace():
    return (
        Path(router_module.__file__).resolve().parents[1]
        / "templates"
        / "add_products"
        / "workspace.html"
    ).read_text(encoding="utf-8")


def test_current_revision_is_r35():
    assert "Rev31 Phase 4.3 R3.5" in _workspace()


def test_r341_compat_test_no_longer_pins_obsolete_r34_marker():
    test_file = (
        Path(__file__).resolve().parent
        / "test_v073_phase45_rev31_phase4_3_r3_4_1_version_assert_compat.py"
    )
    text = test_file.read_text(encoding="utf-8")
    assert 'assert "Rev31 Phase 4.3 R3." in text' in text
    assert 'assert "Rev31 Phase 4.3 R3.4" in text' not in text
