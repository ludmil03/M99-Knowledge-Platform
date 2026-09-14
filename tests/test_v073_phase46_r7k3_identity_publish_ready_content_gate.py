from types import SimpleNamespace
import importlib.util, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]

def test_normative_identity_policy_is_space_six_digits():
    import json
    p=json.loads((ROOT/'config/identity/m99_identity_policy.json').read_text())
    assert p['format']=='M99 000001'
    assert p['regex']=='^M99 [0-9]{6}$'

def test_allocator_normative_regex_and_reserved_floor():
    from app.services.v073_phase46 import canonical_identity_allocator as a
    assert a.NORMATIVE_M99_RE.fullmatch('M99 100018')
    assert not a.NORMATIVE_M99_RE.fullmatch('M99-100018')
    assert a.M99_RE.fullmatch('M99-1')
    assert a.RESERVED_CANONICAL_FLOOR==100017

def test_publisher_accepts_normative_and_historical_compatibility():
    from app.services.v073_phase45 import m99eu_r37_auto_publish as p
    assert p.M99_REFERENCE_RE.fullmatch('M99 100018')
    assert p.M99_REFERENCE_RE.fullmatch('M99-3')

def test_content_gate_blocks_trousers_called_shirt():
    from app.services.v073_phase46.publish_ready_content_gate import validate_publish_ready_content
    r=validate_publish_ready_content(supplier_title='Летен работен панталон BWOLF DAYTONA',supplier_description='',languages={'BG':{'product_name':'BWOLF DAYTONA','h1':'BWOLF DAYTONA','short_description':'Мъжка риза за работа','long_description_html':'','meta_title':'DAYTONA','meta_description':'Панталон'}})
    assert not r['pass']
    assert r['source_type']=='trousers'

def test_content_gate_blocks_raw_br_in_customer_fields():
    from app.services.v073_phase46.publish_ready_content_gate import validate_publish_ready_content
    r=validate_publish_ready_content(supplier_title='Летен работен панталон',supplier_description='',languages={'BG':{'product_name':'DAYTONA <br> Антрацит','h1':'DAYTONA','short_description':'Работен панталон','long_description_html':'','meta_title':'DAYTONA','meta_description':'Работен панталон'}})
    assert not r['pass']
    assert any('raw HTML' in x for x in r['blockers'])

def test_generator_generic_trousers_has_no_shirt_boilerplate():
    from app.services.v073_phase46.content_manufacturer_intelligence import _section_texts
    p={'name':'Летен работен панталон BWOLF DAYTONA','brand':'BWOLF','product_type':'product','reference':'042554','sizes':['XS','S'],'colors':['Антрацит'],'variants':[]}
    text=' '.join(x[0]+' '+x[1] for x in _section_texts(p,'BG')).lower()
    assert 'риза' not in text
    assert 'панталон' in text

def test_clean_inline_removes_supplier_br():
    from app.services.v073_phase46.content_manufacturer_intelligence import _clean_inline
    assert _clean_inline('DAYTONA <br>Антрацит')=='DAYTONA Антрацит'
