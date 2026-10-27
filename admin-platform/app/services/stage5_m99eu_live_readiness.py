from dataclasses import dataclass
from decimal import Decimal
import re,xml.etree.ElementTree as ET
RID=re.compile(r'^M99 [0-9]{6}$')
@dataclass(frozen=True)
class Payload:
 reference:str;category_id:int;price:str;language_map:dict;xml:str;write_allowed:bool=False;write_performed:bool=False
def build(*,reference,category_id,gross_price,language_map,content):
 if not RID.fullmatch(reference):raise ValueError('CANONICAL_M99_ID_REQUIRED')
 if category_id<=0 or Decimal(str(gross_price))<=0:raise ValueError('COMMERCIAL_FIELDS_INVALID')
 if set(language_map)!={'en','bg','ru'} or len(set(language_map.values()))!=3:raise ValueError('DYNAMIC_LANGUAGE_MAP_INVALID')
 root=ET.Element('prestashop');p=ET.SubElement(root,'product')
 for k,v in (('id_category_default',category_id),('reference',reference),('price',gross_price),('active','0'),('available_for_order','0'),('visibility','none')):ET.SubElement(p,k).text=str(v)
 for tag,key in (('name','name'),('description_short','short'),('description','long'),('meta_title','meta_title'),('meta_description','meta_description')):
  n=ET.SubElement(p,tag)
  for iso in ('en','bg','ru'):
   if iso not in content or not str(content[iso].get(key,'')).strip():raise ValueError('MISSING_CONTENT:'+iso+':'+key)
   ET.SubElement(n,'language',{'id':str(language_map[iso])}).text=str(content[iso][key])
 return Payload(reference,category_id,str(gross_price),dict(language_map),ET.tostring(root,encoding='unicode'),False,False)
def verify_readback(payload,xml):
 root=ET.fromstring(xml);p=root.find('.//product')
 if p is None:return False
 def t(x):
  n=p.find(x);return (n.text or '').strip() if n is not None else ''
 return bool(t('id')) and t('reference')==payload.reference and t('id_category_default')==str(payload.category_id) and t('active')=='0'
