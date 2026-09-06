from app.services.v073_phase45.calenda_public_connector import (
    CalendaPublicConnector, _is_category, _is_product, _category_key, _parse,
    _first_price, _availability, _description
)
from app.services.v073_phase45.unified_add_products import SourceView, connector_status


def test_calenda_url_contract():
    assert _is_category("https://calenda.bg/categories/chashi-za-sublimaciq-185")
    assert _is_product("https://calenda.bg/products/31671")
    assert not _is_product("https://calenda.bg/categories/test-1")
    assert _category_key("https://calenda.bg/categories/chashi-za-sublimaciq-185") == "chashi-za-sublimaciq-185"


def test_calenda_reference_product_text_contract():
    text = """КЕРАМИЧНА ЧАША ЗА СУБЛИМАЦИЯ LIMA
КОД: ID2221
Цвят: 30White
Цена
1.69 € / 3.31 лв. без ДДС
Наличност склад Варна:
2171 бр.
Доставка 1-2 работни дни:
154 бр.
Описание:
Керамична гланцирана чаша за сублимационен печат.
Свързани продукти:"""
    assert _first_price(text) == "1.69"
    assert _availability(text).startswith("IN_STOCK")
    assert "Керамична гланцирана" in _description(text)


def test_calenda_html_link_contract():
    html = """<html><body>
    <a href="/categories/chashi-za-sublimaciq-185">ЧАШИ ЗА СУБЛИМАЦИЯ</a>
    <a href="/products/31671">ID2221</a>
    <a href="/products/31671">КЕРАМИЧНА ЧАША ЗА СУБЛИМАЦИЯ LIMA</a>
    </body></html>"""
    p = _parse(html)
    assert any("/categories/" in href for href, _ in p.links)
    assert sum(1 for href, _ in p.links if "/products/31671" in href) == 2


def test_connector_contract_methods_exist():
    c = CalendaPublicConnector("https://calenda.bg")
    assert callable(c.health_check)
    assert callable(c.list_categories)
    assert callable(c.list_products)
    assert callable(c.get_product)


def test_unified_workspace_marks_calenda_ready():
    s = SourceView("s1", "SUPPLIER", "Календа", "calenda.bg", "https://calenda.bg", "ACTIVE")
    status = connector_status(s)
    assert status.kind == "CALENDA_PUBLIC"
    assert status.state == "READY"
