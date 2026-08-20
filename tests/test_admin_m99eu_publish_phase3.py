from pathlib import Path
import importlib.util
import sys


REPO = Path(__file__).resolve().parents[1]
ADMIN = REPO / "admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))


def test_admin_router_is_registered_in_main():
    text = (ADMIN / "app/main.py").read_text(encoding="utf-8-sig")
    assert "product_publish" in text
    assert "include_router" in text


def test_products_screen_links_to_publish_workflow():
    text = (ADMIN / "app/templates/products/list.html").read_text(encoding="utf-8-sig")
    assert "/products/publish/m99eu" in text


def test_publish_template_extends_existing_base():
    text = (ADMIN / "app/templates/products/publish_m99eu.html").read_text(encoding="utf-8-sig")
    assert '{% extends "base.html" %}' in text
    assert "CREATE_INACTIVE" in text
    assert "/products/publish/m99eu/dry-run" in text
    assert "/products/publish/m99eu/create-inactive" in text


def test_service_reuses_existing_prestashop_publisher():
    text = (ADMIN / "app/services/m99eu_publish_service.py").read_text(encoding="utf-8-sig")
    assert "build_inactive_product_xml" in text
    assert "PrestaShopWebserviceClient" in text
    assert "verify_product_readback" in text
    assert "client.create_product(xml_payload)" in text


def test_router_fails_closed_for_unauthenticated_requests():
    text = (ADMIN / "app/routers/product_publish.py").read_text(encoding="utf-8-sig")
    assert "def _is_authenticated" in text
    assert "return False" in text
    assert 'RedirectResponse(url="/login"' in text


def test_create_requires_operator_approval_and_exact_confirmation():
    text = (ADMIN / "app/routers/product_publish.py").read_text(encoding="utf-8-sig")
    assert 'operator_approved != "yes"' in text
    assert 'confirmation.strip() != "CREATE_INACTIVE"' in text


def test_installed_module_imports_without_network_call():
    module_path = ADMIN / "app/services/m99eu_publish_service.py"
    module_name = "phase3_service"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)

    # Python 3.14 dataclasses resolves postponed annotations through
    # sys.modules[cls.__module__]. Register the module before exec_module().
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        assert callable(module.build_live_dry_run)
        assert callable(module.create_inactive_after_ui_confirmation)
    finally:
        sys.modules.pop(module_name, None)
