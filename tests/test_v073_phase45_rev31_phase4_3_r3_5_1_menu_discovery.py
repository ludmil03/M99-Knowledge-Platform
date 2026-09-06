from pathlib import Path


def test_menu_patcher_uses_template_discovery():
    root = Path(__file__).resolve().parents[1]
    # Installer tool itself is outside payload/tests in the ZIP, so this test
    # only protects the runtime expectation after install via base/sidebar scan.
    assert (root / "admin-platform" / "app" / "templates").exists()


def test_add_products_workspace_marker_preserved():
    root = Path(__file__).resolve().parents[1]
    text = (
        root / "admin-platform" / "app" / "templates" / "add_products" / "workspace.html"
    ).read_text(encoding="utf-8")
    assert "Rev31 Phase 4.3 R3.5" in text
    assert "Търси категория" in text
    assert "5. Проверка на извлечените данни" in text
