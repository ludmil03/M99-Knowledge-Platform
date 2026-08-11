from __future__ import annotations
import xml.etree.ElementTree as ET
from core.product_snapshot_analysis import summarize_product_xml, add_snapshot_quality

def _lang_map(root, tag):
    node=root.find(f'.//{tag}')
    if node is None: return {}
    return {str(x.attrib.get('id','')):(x.text or '').strip() for x in node.findall('.//language')}

def _assoc_ids(root,path):
    result=[]
    for node in root.findall(path):
        value=(node.findtext('id') or '').strip()
        if value: result.append(value)
    return result

def build_full_product_snapshot(xml_text:str)->dict:
    root=ET.fromstring(xml_text); base=add_snapshot_quality(summarize_product_xml(xml_text))
    base.update({'names_by_language_id':_lang_map(root,'name'),'meta_titles_by_language_id':_lang_map(root,'meta_title'),'meta_descriptions_by_language_id':_lang_map(root,'meta_description'),'short_descriptions_by_language_id':_lang_map(root,'description_short'),'descriptions_by_language_id':_lang_map(root,'description'),'slugs_by_language_id':_lang_map(root,'link_rewrite'),'category_ids':_assoc_ids(root,'.//associations/categories/category'),'image_ids':_assoc_ids(root,'.//associations/images/image'),'combination_ids':_assoc_ids(root,'.//associations/combinations/combination')})
    return base

def compare_products(a:dict,b:dict)->dict:
    fields=['reference','ean13','active','price','id_category_default','date_add','date_upd','category_ids','image_ids','combination_ids','names_by_language_id','meta_titles_by_language_id','meta_descriptions_by_language_id','short_descriptions_by_language_id','descriptions_by_language_id','slugs_by_language_id']
    diffs={}
    for f in fields:
        if a.get(f)!=b.get(f): diffs[f]={'2076':a.get(f),'2100':b.get(f)}
    return {'same_product_family_review':True,'product_2076':a,'product_2100':b,'differences':diffs,'recommended_master':'2076','automatic_merge':False,'automatic_delete':False}
