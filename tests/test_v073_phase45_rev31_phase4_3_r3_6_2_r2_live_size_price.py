from app.services.v073_phase45 import calenda_public_connector as c

def test_live_calenda_table_shape_without_slash():
    assert c._first_size_price("20.40 € 39.90 лв.") == "20.40"

def test_live_calenda_table_shape_with_html_entity_after_normalization():
    raw = "21.47 &euro; <br/> 41.99 лв."
    normalized = c._cell_text(raw)
    assert normalized == "21.47 € 41.99 лв."
    assert c._first_size_price(normalized) == "21.47"

def test_old_slash_shape_still_supported():
    assert c._first_size_price("20.40 € / 39.90 лв.") == "20.40"

def test_eur_only_is_valid_exact_supplier_evidence():
    assert c._first_size_price("20.40 €") == "20.40"

def test_product_level_price_parser_semantics_unchanged():
    assert c._first_price("20.40 € / 39.90 лв.") is None
    assert c._first_price("20.40 € / 39.90 лв. без ДДС") == "20.40"
