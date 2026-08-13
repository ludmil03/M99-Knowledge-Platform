from core.cherokee_canonical_merge_v0672 import fetch,strip_html
def supplier_market_evidence():
 return {"source":"Stenso","classification":"EXACT_PRODUCT","url":"","market_language_signals":[],"supplier_claims":[],"rules":{"supplier_verbatim_copy":False,"price_in_content":False,"unverified_stock_in_content":False}}
def evidence_model(claims,market):
 facts={}
 for c in claims:
  if str(c.get("content_use","")).startswith("ALLOW"): facts.setdefault(c["field"],c["value"])
 return {"facts":facts,"market_language_signals":market.get("market_language_signals",[]),"rules":{"original_m99_content":True,"supplier_verbatim_copy":False,"claim_level_provenance":True,"invented_claims":False,"price_in_content":False,"unverified_stock_in_content":False}}
def preview(model):
 s=model.get("facts",{}).get("canonical_style","WW601")
 return {"bg":{"name":f"Дамска медицинска туника Cherokee WW Revolution {s} Navy","h1":f"Дамска медицинска туника Cherokee WW Revolution {s} Navy","h2_h3":["Дизайн и кройка","Материя и комфорт","Джобове и функционалност","Технически характеристики","Често задавани въпроси"],"faq_count":6},"en":{"name":f"Cherokee WW Revolution {s} Navy Women's Scrub Top","h1":f"Cherokee WW Revolution {s} Navy Women's Scrub Top"},"ru":{"name":f"Женская медицинская туника Cherokee WW Revolution {s} Navy","h1":f"Женская медицинская туника Cherokee WW Revolution {s} Navy"},"ro":{"name":f"Bluză medicală damă Cherokee WW Revolution {s} Navy","h1":f"Bluză medicală damă Cherokee WW Revolution {s} Navy"}}
deterministic_preview=preview
