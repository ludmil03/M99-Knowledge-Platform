from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
from app.services.stage5_production_readiness import run_production_readiness, gross_to_net, build_blank_create_xml
from app.services.stage5_production_authorization import build_authorization
from app.services.stage5_final_ui_publish import _get_once, resolve_reference, execute_ui_publish, FinalPublishBlocked, ReadbackFailed
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config

TEST_CATEGORY_ID=26

def _price(v):
 s=str(v or '').replace(',','.').strip(); import re
 m=re.search(r'\d+(?:\.\d+)?',s)
 if not m: raise FinalPublishBlocked('SOURCE_PRICE_REQUIRED')
 x=Decimal(m.group(0))
 if x<=0: raise FinalPublishBlocked('SOURCE_PRICE_REQUIRED')
 return x

def _prove_test_category(cfg):
 x=_get_once(cfg,f'/api/categories/{TEST_CATEGORY_ID}')
 if '<category' not in x or f'<id><![CDATA[{TEST_CATEGORY_ID}]]></id>' not in x and f'<id>{TEST_CATEGORY_ID}</id>' not in x:
  raise FinalPublishBlocked('TEST_CATEGORY_26_NOT_PROVEN')
 return True

def prepare_canary(product):
 cfg=load_m99eu_prestashop_config(); rd=run_production_readiness(cfg)
 if not rd.ready: return {'ready':False,'blockers':list(rd.blockers),'target':'m99.eu'}
 _prove_test_category(cfg)
 gross=_price(product.get('price_text'))
 vat=Decimal(rd.vat_rate); net=gross_to_net(gross,vat)
 ref=rd.next_reference
 identity=resolve_reference(cfg,ref)
 if identity.state!='NEW': raise FinalPublishBlocked('CANARY_REFERENCE_NOT_NEW')
 name=str(product.get('name') or '').strip()
 if not name: raise FinalPublishBlocked('PRODUCT_NAME_REQUIRED')
 src=str(product.get('url') or '').strip()
 # Technical inactive canary content only; no invented commercial claims or translations.
 content={}
 for lang in ('en','bg','ru'):
  content[lang]={
   'name':f'[M99 CANARY] {name}',
   'short':f'M99 technical canary. Source: {src}',
   'long':f'M99 technical canary for end-to-end publish/readback validation. Source product: {name}. Source: {src}',
   'meta_title':f'M99 CANARY {name}',
   'meta_description':f'M99 technical canary. Source: {src}',
  }
 blank=_get_once(cfg,'/api/products',{'schema':'blank'})
 xml=build_blank_create_xml(blank,reference=ref,category_id=TEST_CATEGORY_ID,net_price=str(net),tax_rules_group_id=rd.tax_rules_group_id,language_map=rd.language_map,content=content)
 plan=build_authorization(identity_state='NEW',reference=ref,target='m99.eu',gross_price=str(gross),vat_rate=str(vat),language_map=rd.language_map,content=content,variants=[],payload_xml=xml,ready_targets=['m99.eu'])
 return {'ready':True,'blockers':[],'target':'m99.eu','reference':ref,'operation':plan.operation,'scope_token':plan.scope_token,'gross_price':str(gross),'net_price':str(net),'tax_rules_group_id':rd.tax_rules_group_id,'plan':asdict(plan),'inactive_hidden':True,'test_category_id':TEST_CATEGORY_ID}

def execute_canary(plan_raw,*,token,operation,reference,target,confirmed):
 from app.services.stage5_production_authorization import AuthorizationPlan
 p=AuthorizationPlan(**plan_raw); cfg=load_m99eu_prestashop_config()
 return execute_ui_publish(cfg=cfg,plan=p,submitted_token=token,submitted_operation=operation,submitted_reference=reference,submitted_target=target,operator_confirmed=confirmed)
