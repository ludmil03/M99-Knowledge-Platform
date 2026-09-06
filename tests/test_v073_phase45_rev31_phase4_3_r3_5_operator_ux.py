from pathlib import Path
import inspect

from app.routers import unified_add_products as r


def _template_text():
    return (
        Path(r.__file__).resolve().parents[1]
        / "templates"
        / "add_products"
        / "workspace.html"
    ).read_text(encoding="utf-8")


def test_category_context_has_get_route_and_redirect():
    paths = {(route.path, ",".join(route.methods or [])) for route in r.router.routes}
    assert any(path == "/add-products/category" and "GET" in methods for path, methods in paths)
    source = inspect.getsource(r.category)
    assert "RedirectResponse" in source
    assert "category_url=" in source


def test_selected_category_is_preserved_during_hydration():
    source = inspect.getsource(r.hydrate)
    assert "selected_category" in source
    assert "current_category_url=category_url" in source


def test_operator_search_fields_exist():
    text = _template_text()
    assert 'id="supplierSearch"' in text
    assert 'id="productSearch"' in text
    assert "Търси категория" in text
    assert "Supplier ref или Calenda Product ID" in text


def test_only_selected_category_stays_open_after_selection():
    text = _template_text()
    assert "{% if categories and not current_category_url %}" in text
    assert "3. Избрана категория" in text
    assert "Смени категорията" in text


def test_hydration_is_explained_in_bulgarian_with_operator_actions():
    text = _template_text()
    assert "5. Проверка на извлечените данни" in text
    assert "Какво означава това?" in text
    assert "Нищо не се публикува" in text
    assert "Назад към продуктите" in text
    assert "Продължи към Identity / DRAFT" in text


def test_current_r35_marker():
    assert "Rev31 Phase 4.3 R3.5" in _template_text()
