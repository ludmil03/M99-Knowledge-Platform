from pathlib import Path
import json
from integrations.channel_publish import Mela99ClientConfig, ControlledMela99Publisher
from core.live_channel_metadata import parse_languages_xml, parse_categories_xml
from core.product_2076_2100_comparison import build_full_product_snapshot, compare_products
from core.s3s_content_quality_v06642 import build_content_preview

ROOT=Path('.')
OUT=ROOT/'output/diadora_s3s_v06642_live_analysis_preview.json'
FIXTURE=ROOT/'tests/fixtures/diadora_glove_abox_low_pro_s3s_real.json'
client=ControlledMela99Publisher(Mela99ClientConfig(base_url='https://mela99.com',api_key_env='M99_MELA99_API_KEY',timeout_seconds=30))
langs=parse_languages_xml(client.get_resource_xml('languages', {'display':'full'}))
cats=parse_categories_xml(client.get_resource_xml('categories', {'display':'full'}), 'Test')
xml2076=client.get_product_xml('2076'); xml2100=client.get_product_xml('2100')
s2076=build_full_product_snapshot(xml2076); s2100=build_full_product_snapshot(xml2100)
comparison=compare_products(s2076,s2100)
facts=json.loads(FIXTURE.read_text(encoding='utf-8'))['manufacturer_evidence']['facts']
preview=build_content_preview(facts)
blocking=[]
if not langs['ready']: blocking.append(langs.get('blocking_reason'))
if not cats['ready']: blocking.append(cats.get('blocking_reason'))
data={'schema_version':'0.6.6.4.2','mode':'LIVE_GET_ONLY_ANALYSIS_PREVIEW','http_policy':'GET_ONLY','writes':{'channels':False,'dolibarr':False,'supplier':False},'language_discovery':langs,'review_category_discovery':cats,'product_comparison':comparison,'content_preview':preview,'write_allowed':False,'blocking_flags':[x for x in blocking if x]}
OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('M99 v0.6.6.4.2 - LIVE GET-ONLY ANALYSIS + CONTENT PREVIEW')
print('==========================================================')
print('Languages ready:',langs['ready'],'| BG ID:',langs.get('bg_id'),'| EN ID:',langs.get('en_id'))
print('Test category ready:',cats['ready'],'| Test ID:',cats.get('selected_category_id'))
print('Product comparison: 2076 vs 2100')
print('2076 categories:',s2076.get('category_ids'))
print('2100 categories:',s2100.get('category_ids'))
print('2076 images:',len(s2076.get('image_ids',[])),'| combinations:',len(s2076.get('combination_ids',[])))
print('2100 images:',len(s2100.get('image_ids',[])),'| combinations:',len(s2100.get('combination_ids',[])))
print('Recommended master: 2076')
print('Content preview BG FAQ:', '<h2>Често задавани въпроси</h2>' in preview['bg']['long_description_html'])
print('Content preview EN FAQ:', '<h2>Frequently asked questions</h2>' in preview['en']['long_description_html'])
print('WRITE ALLOWED: NO')
print('Output:',OUT)
