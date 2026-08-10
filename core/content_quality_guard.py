import re
from core.content_claims import find_forbidden_marketing_claims

REQUIRED_FIELDS=("channel_profile","seo_title","meta_description","h1","short_description","long_description","h2","faq","image_alt","specifications")
LANGUAGE_FORBIDDEN={"bg":("exact item","nitrile rubber","aluminium 200j"),"ro":("exact item","nitrile rubber","aluminium 200j"),"en":()}

def _flatten(v):
    if isinstance(v,str): return [v]
    if isinstance(v,dict): return sum((_flatten(x) for x in v.values()),[])
    if isinstance(v,list): return sum((_flatten(x) for x in v),[])
    return []

def evaluate_content_quality(channel,language,content,facts):
    issues=[]
    for field in REQUIRED_FIELDS:
        if content.get(field) in (None,"",[],{}): issues.append(f"MISSING_FIELD:{field}")
    texts=_flatten(content); joined="\n".join(texts); pc=str(facts["protection_class"])
    if any(re.search(rf"\b{re.escape(pc)}\s+{re.escape(pc)}\b",text,re.I) for text in texts): issues.append("DUPLICATE_PROTECTION_CLASS")
    low=joined.lower()
    for fragment in LANGUAGE_FORBIDDEN.get(language,()):
        if fragment in low: issues.append(f"LANGUAGE_CONTAMINATION:{fragment}")
    for phrase in ("текстилна защита от пробиване","textile anti-puncture","protecție textilă antiperforație"):
        if phrase in low and "textile" not in str(facts.get("anti_puncture","")).lower(): issues.append(f"UNSUPPORTED_CLAIM:{phrase}")
    for phrase in find_forbidden_marketing_claims(joined): issues.append(f"MARKETING_CLAIM_REQUIRES_EVIDENCE:{phrase}")
    model=str(facts["model_name"])
    for field in ("seo_title","h1"):
        if model not in str(content.get(field,"")): issues.append(f"IDENTITY_MISSING:{field}")
    if not any(str(v)==pc for v in (content.get("specifications") or {}).values()): issues.append("SPEC_MISSING:protection_class")
    faq=content.get("faq") or []
    if len(faq)<5: issues.append("FAQ_TOO_SHALLOW")
    unique=[]
    for x in issues:
        if x not in unique: unique.append(x)
    return {"channel":channel,"language":language,"status":"CONTENT_READY" if not unique else "REVIEW","issues":unique,"publish_allowed":False}

def evaluate_all_content(content_by_channel,facts):
    results=[evaluate_content_quality(ch,lang,c,facts) for ch,langs in content_by_channel.items() for lang,c in langs.items()]
    ready=all(r["status"]=="CONTENT_READY" for r in results)
    return {"status":"CONTENT_READY" if ready else "REVIEW","all_content_ready":ready,"results":results,"publication_enabled":False}
