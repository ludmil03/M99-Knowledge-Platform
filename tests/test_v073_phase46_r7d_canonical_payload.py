from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'admin-platform/app/services/v073_phase46/canonical_live_pilot.py'
def load():
 s=importlib.util.spec_from_file_location('r7d',MOD);m=importlib.util.module_from_spec(s);import sys;sys.modules[s.name]=m;s.loader.exec_module(m);return m
def preview():
 docs={}
 for c in ('EN','BG','RU'):
  docs[c]={'product_name':f'Name {c}','h1':f'H1 {c}','short_description':f'Short {c}','long_description_html':f'<p>Long {c}</p>','meta_title':f'Meta {c}','meta_description':f'Desc {c}','manufacturer_reference_in_specs':'MPN-7'}
 return {'status':'READY','ready':True,'job_id':1,'item_id':2,'identifiers':{'channel_reference':'M99-123','channel_reference_role':'PERMANENT_M99_REFERENCE','supplier_reference':'SUP-5','supplier_reference_role':'SUPPLIER_MAPPING_ONLY','manufacturer_reference':'MPN-7','manufacturer_reference_role':'VERIFIED_MANUFACTURER_MPN_ONLY'},'languages':docs,'images':{'count':2},'variants':{'rows_count':3}}
def test_multilingual_canonical_payload_is_hidden_and_role_safe():
 m=load();x=m.build_canonical_product_xml(preview(),'49.90',26,[('1','en'),('2','bg'),('3','ru')])
 assert '<reference><![CDATA[M99-123]]></reference>' in x
 assert '<supplier_reference><![CDATA[SUP-5]]></supplier_reference>' in x
 assert '<mpn><![CDATA[MPN-7]]></mpn>' in x
 assert '<active><![CDATA[0]]></active>' in x and '<visibility><![CDATA[none]]></visibility>' in x
 assert 'Name EN' in x and 'Name BG' in x and 'Name RU' in x
 assert 'Short EN' in x and '<p>Long BG</p>' in x and 'Desc RU' in x
def test_bad_preview_blocks():
 m=load();p=preview();p['identifiers']['channel_reference']='SUP-5'
 try:m.validate_preview(p)
 except m.CanonicalPilotError:return
 assert False
def test_missing_language_blocks():
 m=load();p=preview();del p['languages']['RU']
 try:m.validate_preview(p)
 except m.CanonicalPilotError:return
 assert False
def test_invalid_price_blocks():
 m=load()
 try:m.build_canonical_product_xml(preview(),'0',26,[('1','en'),('2','bg'),('3','ru')])
 except m.CanonicalPilotError:return
 assert False
