from pathlib import Path

from app.routers import unified_add_products as router_module


def _workspace():
    return (
        Path(router_module.__file__).resolve().parents[1]
        / "templates"
        / "add_products"
        / "workspace.html"
    ).read_text(encoding="utf-8")


def test_bulgarian_selected_category_label_is_utf8_correct():
    text = _workspace()
    assert "3. Избрана категория" in text


def test_bulgarian_product_review_label_is_utf8_correct():
    text = _workspace()
    assert "5. Проверка на извлечените данни" in text


def test_operator_actions_are_utf8_correct():
    text = _workspace()
    assert "Назад към продуктите" in text
    assert "Смени категорията" in text
    assert "Продължи към Identity / DRAFT" in text


def test_search_fields_still_exist():
    text = _workspace()
    assert 'id="supplierSearch"' in text
    assert 'id="productSearch"' in text


def test_r35_marker_still_present():
    assert "Rev31 Phase 4.3 R3.5" in _workspace()
