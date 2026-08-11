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

def parse_categories_xml(xml_text: str, target_name: str="Test", *, allow_inactive_review_category: bool=True) -> dict:
    root=ET.fromstring(xml_text)
    target=target_name.casefold().strip()
    matches=[]
    for cat in root.findall(".//category"):
        cid=_text(cat,"id"); active=_text(cat,"active")
        names=[]
        name_node=cat.find("name")
        if name_node is not None:
            for lang in name_node.findall(".//language"):
                value=(lang.text or "").strip()
                if value:
                    names.append({"language_id":str(lang.attrib.get("id","")),"value":value})
        if any(x["value"].casefold().strip()==target for x in names):
            matches.append({"id":cid,"active":active,"is_active":active!="0","names":names})
    selected=matches[0] if len(matches)==1 else None
    ready=bool(selected and (selected["is_active"] or allow_inactive_review_category))
    result={
        "target_name":target_name,
        "matches":matches,
        "ready":ready,
        "selected_category_id":selected["id"] if ready else None,
        "selected_category_active":selected["is_active"] if selected else None,
        "review_category_can_be_inactive":allow_inactive_review_category,
        "discovery_authority":"LIVE_API_NAME_MATCH",
    }
    if len(matches)==0: result["blocking_reason"]="TEST_CATEGORY_NOT_FOUND"
    elif len(matches)>1: result["blocking_reason"]="TEST_CATEGORY_AMBIGUOUS"
    elif not ready: result["blocking_reason"]="TEST_CATEGORY_NOT_ELIGIBLE"
    return result
