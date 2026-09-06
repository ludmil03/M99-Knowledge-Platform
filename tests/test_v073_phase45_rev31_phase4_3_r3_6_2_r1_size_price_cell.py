from app.services.v073_phase45 import calenda_public_connector as c

def test_size_price_cell_without_vat_suffix():
    assert c._first_size_price("20.40 € / 39.90 лв.") == "20.40"

def test_size_price_cell_with_html_normalized_text():
    assert c._first_size_price("21.47 €  /  41.99 лв.") == "21.47"

def test_product_level_price_parser_is_not_redefined():
    # R3.6.2R1 must not loosen the existing product-level parser.
    assert c._first_price("20.40 € / 39.90 лв.") is None
    assert c._first_price("20.40 € / 39.90 лв. без ДДС") == "20.40"
