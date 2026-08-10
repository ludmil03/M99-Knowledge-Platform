import re

REQUIRED_FIELDS=("seo_title","meta_description","h1","short_description","long_description","h2","faq","image_alt","specifications")
LANGUAGE_FORBIDDEN={
    "bg":("exact item","nitrile rubber","aluminium 200J","aluminium 200 J"),
    "ro":("exact item","nitrile rubber","aluminium 200J","aluminium 200 J"),
    "en":()
}

def _flatten_text(value):
    if isinstance(value,str): return [value]
    if isinstance(value,dict):
        out=[]
        for v in value.values(): out.extend(_flatten_text(v))
        return out
    if isinstance(value,list):
        out=[]
        for v in value: out.extend(_flatten_text(v))
        return out
    return []

def _duplicate_model_qualifier(text, protection_class):
    t=re.escape(protection_class)
    return bool(re.search(rf"\b{t}\s+{t}\b",text,flags=re.I))

def _unsupported_claims(texts,facts):
    joined="\n".join(texts).lower()
    issues=[]
    suspicious=("текстилна защита от пробиване","textile anti-puncture","protecție textilă antiperforație")
    for phrase in suspicious:
        if phrase in joined:
            anti=str(facts.get("anti_puncture","")).lower()
            if "textile" not in anti and "текстил" not in anti:
                issues.append(f"UNSUPPORTED_CLAIM:{phrase}")
    return issues

def evaluate_content_quality(channel,language,content,canonical_facts):
    issues=[]
    for field in REQUIRED_FIELDS:
        if field not in content or content[field] in (None,"",[],{}):
            issues.append(f"MISSING_FIELD:{field}")
    texts=_flatten_text(content)
    for text in texts:
        if _duplicate_model_qualifier(text,str(canonical_facts["protection_class"])):
            issues.append("DUPLICATE_PROTECTION_CLASS")
    joined="\n".join(texts).lower()
    for fragment in LANGUAGE_FORBIDDEN.get(language,()):
        if fragment.lower() in joined:
            issues.append(f"LANGUAGE_CONTAMINATION:{fragment}")
    issues.extend(_unsupported_claims(texts,canonical_facts))
    model=str(canonical_facts["model_name"])
    for field in ("seo_title","h1"):
        if field in content and model not in str(content[field]):
            issues.append(f"IDENTITY_MISSING:{field}")
    specs=content.get("specifications") or {}
    if not any(str(v)==str(canonical_facts["protection_class"]) for v in specs.values()):
        issues.append("SPEC_MISSING:protection_class")
    unique=[]; seen=set()
    for issue in issues:
        if issue not in seen:
            seen.add(issue); unique.append(issue)
    return {
        "channel":channel,
        "language":language,
        "status":"CONTENT_READY" if not unique else "REVIEW",
        "issues":unique,
        "publish_allowed":False
    }

def evaluate_all_content(content_by_channel,canonical_facts):
    results=[]
    for channel,languages in content_by_channel.items():
        for language,content in languages.items():
            results.append(evaluate_content_quality(channel,language,content,canonical_facts))
    all_ready=all(r["status"]=="CONTENT_READY" for r in results)
    return {
        "status":"CONTENT_READY" if all_ready else "REVIEW",
        "all_content_ready":all_ready,
        "results":results,
        "publication_enabled":False
    }
