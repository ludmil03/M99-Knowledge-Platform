from __future__ import annotations
import xml.etree.ElementTree as ET

def _text(node, tag):
    child=node.find(tag)
    return (child.text or '').strip() if child is not None and child.text else ''

def parse_languages_xml(xml_text: str) -> dict:
    root=ET.fromstring(xml_text)
    rows=[]
    for lang in root.findall('.//language'):
        lid=_text(lang,'id'); iso=_text(lang,'iso_code').lower(); name=_text(lang,'name'); active=_text(lang,'active')
        if lid and iso:
            rows.append({'id':lid,'iso_code':iso,'name':name,'active':active})
    mapping={x['iso_code']:x['id'] for x in rows if x['active']!='0'}
    result={'languages':rows,'active_iso_to_id':mapping,'bg_id':mapping.get('bg'),'en_id':mapping.get('en'),'ready':bool(mapping.get('bg') and mapping.get('en'))}
    if not result['ready']: result['blocking_reason']='BG_EN_LANGUAGE_MAPPING_NOT_UNAMBIGUOUS'
    return result

def parse_categories_xml(xml_text: str, target_name: str='Test') -> dict:
    root=ET.fromstring(xml_text); target=target_name.casefold().strip(); matches=[]
    for cat in root.findall('.//category'):
        cid=_text(cat,'id'); active=_text(cat,'active'); names=[]; name_node=cat.find('name')
        if name_node is not None:
            for lang in name_node.findall('.//language'):
                txt=(lang.text or '').strip()
                if txt: names.append({'language_id':str(lang.attrib.get('id','')),'value':txt})
        if any(x['value'].casefold().strip()==target for x in names):
            matches.append({'id':cid,'active':active,'names':names})
    active_matches=[x for x in matches if x['active']!='0']
    result={'target_name':target_name,'matches':matches,'active_matches':active_matches,'ready':len(active_matches)==1,'selected_category_id':active_matches[0]['id'] if len(active_matches)==1 else None}
    if not result['ready']: result['blocking_reason']='TEST_CATEGORY_NOT_UNAMBIGUOUS' if active_matches else 'TEST_CATEGORY_NOT_FOUND'
    return result
