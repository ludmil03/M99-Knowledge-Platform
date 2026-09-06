from app.services.v073_phase45.palltex_public_connector import PalltexPublicConnector,_is_category,_is_product,_catkey,_parse
def test_url_contract():
 assert _is_category('https://palltex.bg/bg/cat/rabotno-obleklo'); assert _is_product('https://palltex.bg/bg/p/test/19466')
def test_filter_category():assert 'category=20207' in _catkey('https://palltex.bg/bg/cat/x?categories%5B20207%5D=20207')
def test_parse_links():
 p=_parse('<a href="/bg/cat/a">Cat</a><a href="/bg/p/x/1">Prod</a>');assert len(p.links)==2
def test_contract_methods():
 c=PalltexPublicConnector();assert all(callable(getattr(c,x)) for x in ['health_check','list_categories','list_products','get_product'])
