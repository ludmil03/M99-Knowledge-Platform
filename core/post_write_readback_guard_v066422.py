import xml.etree.ElementTree as ET

def _langs(root, tag):
    node=root.find(f".//{tag}")
    if node is None: return {}
    return {str(x.attrib.get("id","")):(x.text or "").strip() for x in node.findall(".//language")}

def _ids(root,path):
    return {(x.findtext("id") or "").strip() for x in root.findall(path) if (x.findtext("id") or "").strip()}

def validate_write_readback(*,before_xml,after_xml,language_mapping,expected_review_category_id,expected_bg_markers=None,expected_en_markers=None):
    b=ET.fromstring(before_xml); a=ET.fromstring(after_xml)
    bg=str(language_mapping.get("bg_id") or ""); en=str(language_mapping.get("en_id") or "")
    flags=[]
    if not bg or not en or bg==en: flags.append("INVALID_LANGUAGE_MAPPING")
    bc=_ids(b,".//associations/categories/category"); ac=_ids(a,".//associations/categories/category")
    if str(expected_review_category_id) not in ac: flags.append("REVIEW_CATEGORY_NOT_PERSISTED")
    if not bc.issubset(ac): flags.append("ORIGINAL_CATEGORIES_LOST")
    if _ids(b,".//associations/images/image") != _ids(a,".//associations/images/image"): flags.append("IMAGES_CHANGED_OR_LOST")
    if _ids(b,".//associations/combinations/combination") != _ids(a,".//associations/combinations/combination"): flags.append("COMBINATIONS_CHANGED_OR_LOST")
    desc=_langs(a,"description"); bgt=desc.get(bg,""); ent=desc.get(en,"")
    for m in expected_bg_markers or []:
        if m.casefold() not in bgt.casefold(): flags.append("BG_CONTENT_NOT_IN_BG_LANGUAGE_ID"); break
    for m in expected_en_markers or []:
        if m.casefold() not in ent.casefold(): flags.append("EN_CONTENT_NOT_IN_EN_LANGUAGE_ID"); break
    return {"passed":not flags,"blocking_flags":flags,"bg_language_id":bg,"en_language_id":en,"review_category_id":str(expected_review_category_id)}
