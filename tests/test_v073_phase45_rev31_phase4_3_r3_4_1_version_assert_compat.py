from pathlib import Path

from app.routers import unified_add_products as router_module


def _template_text():
    return (
        Path(router_module.__file__).resolve().parents[1]
        / "templates"
        / "add_products"
        / "workspace.html"
    ).read_text(encoding="utf-8")


def test_phase43_revision_marker_family_is_present():
    text = _template_text()
    assert "Rev31 Phase 4.3 R3." in text


def test_selected_source_navigation_contract_is_still_preserved():
    text = _template_text()
    assert "/add-products?source_uuid={{ selected_source.source_uuid }}" in text


def test_prior_selected_source_test_does_not_pin_exact_old_revision():
    test_file = (
        Path(__file__).resolve().parent
        / "test_v073_phase45_rev31_phase4_3_r3_3_selected_source_state.py"
    )
    text = test_file.read_text(encoding="utf-8")
    assert 'assert "Rev31 Phase 4.3 R3." in text' in text
    assert 'assert "Rev31 Phase 4.3 R3.3" in text' not in text
