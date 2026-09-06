from types import SimpleNamespace

from app.services.v073_phase45.unified_add_products import (
    SourceView,
    normalize_domain,
    validate_selection,
    _classify,
)


def src():
    return SourceView("s1", "SUPPLIER", "Palltex", "palltex.bg", "https://palltex.bg/", "ACTIVE")


def test_normalize_domain():
    assert normalize_domain("https://www.palltex.bg/path") == "palltex.bg"


def test_selection_modes():
    s = src()
    mode, urls = validate_selection("ONE_PRODUCT", ["https://palltex.bg/product/1"], s)
    assert mode == "ONE_PRODUCT"
    assert len(urls) == 1

    mode, urls = validate_selection("ALL_PRODUCTS", [], s)
    assert mode == "ALL_PRODUCTS"
    assert urls == ("https://palltex.bg/",)


def test_reject_cross_domain():
    s = src()
    try:
        validate_selection("ONE_PRODUCT", ["https://evil.example/x"], s)
    except ValueError:
        pass
    else:
        raise AssertionError("cross-domain selection must be rejected")


def test_generic_classification_contract():
    assert _classify("https://x.bg/category/work-shoes", "Работни обувки")[0] == "category"
    assert _classify("https://x.bg/product/123", "Product 123")[0] == "product"
