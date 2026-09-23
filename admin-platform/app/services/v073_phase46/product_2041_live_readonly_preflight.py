import xml.etree.ElementTree as ET
PRODUCT_ID="2041";REFERENCE="M99 100018"
def inspect(api_key,curl):
 s,x=curl(api_key,"/api/products/2041")
 if str(s)!="200":raise RuntimeError("GET_FAILED_"+str(s))
 p=ET.fromstring(x).find(".//product")
 def t(k):
  n=p.find(k);return (n.text or "").strip() if n is not None else ""
 def ids(path):return [(n.text or "").strip() for n in p.findall(path) if (n.text or "").strip()]
 r={"id":t("id"),"reference":t("reference"),"active":t("active"),"available_for_order":t("available_for_order"),"visibility":t("visibility"),"category":t("id_category_default"),"price_net":t("price"),"tax_rules_group":t("id_tax_rules_group"),"cache_default_attribute":t("cache_default_attribute"),"combinations":ids("./associations/combinations/combination/id"),"images":ids("./associations/images/image/id"),"stock":ids("./associations/stock_availables/stock_available/id")}
 b=[]
 if r["id"]!=PRODUCT_ID:b+=["PRODUCT_ID_MISMATCH"]
 if r["reference"]!=REFERENCE:b+=["REFERENCE_MISMATCH"]
 if (r["active"],r["available_for_order"],r["visibility"])!=("0","0","none"):b+=["NOT_SAFE_HIDDEN"]
 if not r["category"]:b+=["CATEGORY_MISSING"]
 if r["tax_rules_group"] in ("","0"):b+=["VAT_RULE_UNRESOLVED"]
 if not r["images"]:b+=["NO_IMAGES"]
 if not r["combinations"]:b+=["NO_COMBINATIONS"]
 if r["combinations"] and (not r["cache_default_attribute"] or r["cache_default_attribute"] not in r["combinations"]):b+=["DEFAULT_COMBINATION_INVALID"]
 return {"mode":"LIVE_READ_ONLY","product":"2041 / M99 100018","live":r,"blockers":b,"writes_performed":False}
