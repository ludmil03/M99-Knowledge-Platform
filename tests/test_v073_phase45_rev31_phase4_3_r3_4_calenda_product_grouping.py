from app.services.v073_phase45.calenda_public_connector import (
    ProductHydration,
    _canonical_product_url,
    _group_product_links,
    _product_id,
    _variant_code,
)


CATEGORY_HTML = """
<html><body>
  <a href="/products/34408">ID207</a>
  <a href="/products/34408">ТЕНИСКА ТИП ЛАКОСТА PREMIUM TIPPED POLO</a>

  <a href="/products/34408?color=317"></a>
  <a href="/products/34408?color=480"></a>
  <a href="/products/34408?color=485"></a>
  <a href="/products/34408?color=486"></a>
  <a href="/products/34408?color=488"></a>

  <a href="/products/39026">ID3001</a>
  <a href="/products/39026">ДРУГА ТЕНИСКА</a>
  <a href="/products/39026?color=5976"></a>
  <a href="/products/39026?color=5977"></a>
</body></html>
"""


def test_variant_url_has_same_canonical_product_identity():
    base = "https://calenda.bg/products/34408"
    variant = "https://calenda.bg/products/34408?color=317"
    assert _canonical_product_url(variant) == base
    assert _product_id(variant) == "34408"
    assert _variant_code(variant) == "317"


def test_category_links_group_into_one_parent_per_calenda_product_id():
    products = _group_product_links(
        CATEGORY_HTML,
        "https://calenda.bg/categories/test-1",
    )
    assert len(products) == 2
    assert {p.calenda_product_id for p in products} == {"34408", "39026"}


def test_grouped_product_inherits_real_name_and_supplier_reference():
    products = _group_product_links(
        CATEGORY_HTML,
        "https://calenda.bg/categories/test-1",
    )
    p = next(x for x in products if x.calenda_product_id == "34408")
    assert p.name == "ТЕНИСКА ТИП ЛАКОСТА PREMIUM TIPPED POLO"
    assert p.supplier_reference == "ID207"
    assert p.source_key == "34408"
    assert p.url == "https://calenda.bg/products/34408"


def test_color_urls_are_variants_not_duplicate_product_rows():
    products = _group_product_links(
        CATEGORY_HTML,
        "https://calenda.bg/categories/test-1",
    )
    p = next(x for x in products if x.calenda_product_id == "34408")
    assert [v.code for v in p.variants] == ["317", "480", "485", "486", "488"]
    assert all(v.url.startswith("https://calenda.bg/products/34408?color=") for v in p.variants)


def test_missing_variant_anchor_text_has_safe_operator_fallback():
    products = _group_product_links(
        CATEGORY_HTML,
        "https://calenda.bg/categories/test-1",
    )
    p = next(x for x in products if x.calenda_product_id == "34408")
    assert p.variants[0].label == "Color 317"
    assert not p.variants[0].label.startswith("Calenda product")


def test_hydration_model_exposes_calenda_id_and_selected_variant():
    x = ProductHydration(
        source_key="34408",
        name="Example",
        url="https://calenda.bg/products/34408?color=317",
        supplier_reference="ID207",
        brand=None,
        price_text="5.98",
        currency="EUR",
        availability_text=None,
        description="d",
        images=(),
        variants=(),
        hydration_pass=False,
        warnings=("AVAILABILITY_NOT_FOUND",),
        calenda_product_id="34408",
        selected_variant_code="317",
    )
    assert x.calenda_product_id == "34408"
    assert x.selected_variant_code == "317"
