from app.services.v073_phase45.calenda_public_connector import (
    _parse,
    _extract_brand,
    _variants_from_product_page,
    _product_images,
    _availability_for_hydration,
)

PRODUCT_HTML = """
<html>
<head>
<meta property="og:image" content="/media/products/31809/main-river.jpg">
</head>
<body>
<header><img src="/assets/calenda-logo.png" alt="КАЛЕНДА"></header>
<main class="product-detail">
  <h1>МЪЖКА РИЗА RIVER</h1>
  <div>КОД: 93100</div>
  <section class="product-gallery">
    <img src="/media/products/31809/main-river.jpg" alt="МЪЖКА РИЗА RIVER">
    <img src="/media/products/31809/river-back.jpg" alt="МЪЖКА РИЗА RIVER 93100">
  </section>
  <div>Описание:</div>
  <p>Мъжка риза с класическа кройка.</p>
  <p>Марка:</p><strong>PROMO STARS</strong>
  <div class="color-selector">
    <a href="/products/31809?color=20">20 бял</a>
    <a href="/products/31809?color=26">26 черно</a>
    <a href="/products/31809?color=42">42 тъмно-синьо</a>
    <a href="/products/31809?color=46">46 небесно-синьо</a>
  </div>
  <h3>Свързани продукти:</h3>
  <img src="/media/products/93300/brook.jpg" alt="ДАМСКА РИЗА BROOK">
  <h2>ПОДОБНИ ПРОДУКТИ</h2>
  <img src="/media/products/94100/other-shirt.jpg" alt="МЪЖКА РИЗА SHORT RIVER">
</main>
<footer><img src="/assets/footer-logo.png"></footer>
</body>
</html>
"""

def test_brand_is_explicit_supplier_evidence():
    p = _parse(PRODUCT_HTML)
    assert _extract_brand(p.text_parts) == "PROMO STARS"

def test_same_product_color_links_become_four_variants():
    p = _parse(PRODUCT_HTML)
    variants = _variants_from_product_page(p, "https://calenda.bg/products/31809")
    assert [v["code"] for v in variants] == ["20", "26", "42", "46"]
    assert [v["value"] for v in variants] == ["бял", "черно", "тъмно-синьо", "небесно-синьо"]

def test_related_and_similar_product_images_are_excluded():
    p = _parse(PRODUCT_HTML)
    images = _product_images(p, "https://calenda.bg/products/31809", "МЪЖКА РИЗА RIVER", "93100")
    assert "https://calenda.bg/media/products/31809/main-river.jpg" in images
    assert "https://calenda.bg/media/products/31809/river-back.jpg" in images
    assert not any("93300" in x or "94100" in x for x in images)
    assert not any("logo" in x.lower() for x in images)

def test_missing_public_stock_is_unknown_not_out_of_stock():
    value, warning = _availability_for_hydration("Описание: test")
    assert value == "UNKNOWN"
    assert warning == "AVAILABILITY_NOT_PUBLISHED"
