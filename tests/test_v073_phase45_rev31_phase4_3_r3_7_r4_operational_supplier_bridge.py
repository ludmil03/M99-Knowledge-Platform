from types import SimpleNamespace

from app.services.v073_phase45.r37_import_bridge import (
    _host,
    _supplier_domain_candidates,
)

def test_host_normalizes_www_and_paths():
    assert _host("https://www.calenda.bg/products/1") == "calenda.bg"
    assert _host("calenda.bg") == "calenda.bg"

def test_supplier_domain_candidates_accept_multiple_possible_runtime_fields():
    s = SimpleNamespace(base_url="https://www.calenda.bg/", website=None, domain=None)
    assert _supplier_domain_candidates(s) == {"calenda.bg"}

def test_supplier_domain_candidates_merge_fields():
    s = SimpleNamespace(
        base_url="https://calenda.bg/",
        website="https://www.calenda.bg/about",
        domain="calenda.bg",
    )
    assert _supplier_domain_candidates(s) == {"calenda.bg"}
