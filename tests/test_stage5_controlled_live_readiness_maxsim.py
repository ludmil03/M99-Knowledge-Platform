import pytest
from app.services.stage5_m99eu_live_readiness import *
def C():return {x:{'name':'N','short':'S','long':'L','meta_title':'T','meta_description':'D'} for x in ('en','bg','ru')}
@pytest.mark.parametrize('m',({'en':'1','bg':'2','ru':'3'},{'en':'7','bg':'4','ru':'9'},{'en':'99','bg':'3','ru':'12'}))
def test_dynamic(m):
 p=build(reference='M99 100019',category_id=26,gross_price='58.13',language_map=m,content=C());assert not p.write_allowed and not p.write_performed
 for lid in m.values():assert 'id="'+lid+'"' in p.xml
def test_bad_identity():
 with pytest.raises(ValueError):build(reference='M99-100019',category_id=26,gross_price='58.13',language_map={'en':'1','bg':'2','ru':'3'},content=C())
def test_duplicate_language_ids():
 with pytest.raises(ValueError):build(reference='M99 100019',category_id=26,gross_price='58.13',language_map={'en':'1','bg':'1','ru':'3'},content=C())
def test_readback():
 p=build(reference='M99 100019',category_id=26,gross_price='58.13',language_map={'en':'8','bg':'4','ru':'2'},content=C())
 x='<prestashop><product><id>123</id><reference>M99 100019</reference><id_category_default>26</id_category_default><active>0</active></product></prestashop>'
 assert verify_readback(p,x) and not verify_readback(p,x.replace('100019','100020'))
