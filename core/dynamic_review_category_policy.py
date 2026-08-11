def require_discovered_review_category(d):
    if not d.get("ready"): raise ValueError("Review category not ready")
    cid=str(d.get("selected_category_id") or "")
    if not cid.isdigit(): raise ValueError("Invalid review category id")
    return cid

def apply_dynamic_review_category_policy(*,is_existing_product,existing_category_ids,category_discovery):
    cid=require_discovered_review_category(category_discovery)
    existing=list(dict.fromkeys(str(x) for x in (existing_category_ids or []) if str(x).strip()))
    if is_existing_product:
        ids=existing+[cid] if cid not in existing else existing
        return {"mode":"KEEP_EXISTING_PLUS_DISCOVERED_REVIEW","review_category_id":cid,"write_category_ids":ids,"remove_original_categories":False}
    return {"mode":"DISCOVERED_REVIEW_ONLY_FOR_NEW_DRAFT","review_category_id":cid,"write_category_ids":[cid],"remove_original_categories":False}
