from pathlib import Path
import inspect

from app.services.v073_phase45.unified_add_products import (
    SourceView,
    connector_status,
)
from app.routers import unified_add_products as router_module


def test_calenda_remains_ready():
    source = SourceView(
        "calenda-1",
        "SUPPLIER",
        "Календа",
        "calenda.bg",
        "https://calenda.bg",
        "ACTIVE",
    )
    status = connector_status(source)
    assert status.kind == "CALENDA_PUBLIC"
    assert status.state == "READY"


def test_ready_connector_category_loading_is_generic():
    source = inspect.getsource(router_module._selected_source_context)
    assert 'status.state == "READY"' in source
    assert "list_source_categories(source)" in source
    assert "PALLTEX_PUBLIC" not in source


def test_source_selection_redirect_preserves_uuid():
    source = inspect.getsource(router_module.source)
    assert "/add-products?source_uuid=" in source
    assert "status_code=303" in source


def test_home_accepts_selected_source_query_state():
    sig = inspect.signature(router_module.home)
    assert "source_uuid" in sig.parameters
    source = inspect.getsource(router_module.home)
    assert "_selected_source_context" in source


def test_template_preserves_selected_source_in_add_products_nav():
    template_path = (
        Path(router_module.__file__).resolve().parents[1]
        / "templates"
        / "add_products"
        / "workspace.html"
    )
    text = template_path.read_text(encoding="utf-8")
    assert "/add-products?source_uuid={{ selected_source.source_uuid }}" in text
    assert "Rev31 Phase 4.3 R3." in text
