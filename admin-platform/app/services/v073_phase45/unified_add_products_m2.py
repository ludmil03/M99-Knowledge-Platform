from __future__ import annotations
import html,re

def clean_text(v):
 s='' if v is None else str(v);s=re.sub(r'(?i)<br\s*/?>',' ',s);s=re.sub(r'<[^>]+>',' ',s);return ' '.join(html.unescape(s).split())

def manufacturer_resolution(brand):
 if clean_text(brand).casefold()=='portwest': return {'manufacturer':'Portwest','official_site':'https://www.portwest.com','state':'OBSERVED_AUTHORIZED_MANUFACTURER_EVIDENCE','manual_override_required':False}
 return {'manufacturer':'UNKNOWN','official_site':'','state':'UNRESOLVED','manual_override_required':True}

def source_identifier_label(domain):
 return {'calenda.bg':'Calenda Product ID','palltex.bg':'Palltex Product ID / URL','bultex99.com':'Bultex Product ID / URL'}.get((domain or '').lower(),'Source Product ID')

def normalize_hydrated(h,domain):
 g=lambda n,d=None:getattr(h,n,d)
 return {'name':clean_text(g('name')),'supplier_reference':clean_text(g('supplier_reference')),'source_identifier':clean_text(g('calenda_product_id') or g('source_key')),'source_identifier_label':source_identifier_label(domain),'brand':clean_text(g('brand')),'manufacturer':manufacturer_resolution(g('brand')),'price_text':clean_text(g('price_text')),'currency':clean_text(g('currency')),'availability':clean_text(g('availability_text')),'url':clean_text(g('url')),'description':clean_text(g('description')),'images':list(g('images',[]) or []),'warnings':list(g('warnings',[]) or []),'hydration_pass':bool(g('hydration_pass',False))}

# M99_M3_TARGET_SCOPE
def target_rows(targets,requested=None):
 requested=set(requested or [])
 out=[]
 for t in targets:
  key=getattr(t,'key','');a=bool(getattr(t,'authorized',False));r=bool(getattr(t,'ready',False));q=key in requested
  state='REQUESTED_READY' if q and a and r else ('REQUESTED_BLOCKED' if q else 'NOT_REQUESTED')
  out.append({'key':key,'requested':q,'authorized':a,'ready':r,'state':state,'production_write_ready':False})
 return out
