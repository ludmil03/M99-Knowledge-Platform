import xml.etree.ElementTree as ET
PRODUCT_ID="2041"; REFERENCE="M99 100018"
def _t(n,k):
 x=n.find(k); return (x.text or "").strip() if x is not None else ""
def inspect(key,curl):
 s,x=curl(key,"/api/products/2041")
 if str(s)!="200": raise RuntimeError("PRODUCT_GET_FAILED_"+str(s))
 p=ET.fromstring(x).find(".//product")
 if p is None: raise RuntimeError("PRODUCT_XML_INVALID")
 live={"id":_t(p,"id"),"reference":_t(p,"reference"),"active":_t(p,"active"),
 "available_for_order":_t(p,"available_for_order"),"visibility":_t(p,"visibility"),
 "category":_t(p,"id_category_default"),"price_net":_t(p,"price"),
 "tax_group":_t(p,"id_tax_rules_group"),"default":_t(p,"cache_default_attribute"),
 "combinations":[_t(n,"id") for n in p.findall("./associations/combinations/combination")],
 "images":[_t(n,"id") for n in p.findall("./associations/images/image")]}
 blockers=[]
 if live["id"]!=PRODUCT_ID: blockers+=["PRODUCT_ID_MISMATCH"]
 if live["reference"]!=REFERENCE: blockers+=["REFERENCE_MISMATCH"]
 if (live["active"],live["available_for_order"],live["visibility"])!=("0","0","none"): blockers+=["NOT_SAFE_HIDDEN"]
 ts,tx=curl(key,"/api/tax_rule_groups?display=full")
 tax=[]
 if str(ts)=="200":
  try:
   for n in ET.fromstring(tx).findall(".//tax_rule_group"):
    if _t(n,"active") in ("1","true","True"): tax.append({"id":_t(n,"id"),"name":_t(n,"name")})
  except ET.ParseError: pass
 if not tax: blockers+=["VAT_EVIDENCE_MISSING"]
 elif len(tax)!=1: blockers+=["VAT_RULE_AMBIGUOUS"]
 # Fail closed: these require verified supplier/manufacturer evidence, never guessed.
 blockers+=["SUPPLIER_PRICE_NOT_VERIFIED","SUPPLIER_CURRENCY_MISSING","IMAGE_EVIDENCE_MISSING","VARIANT_EVIDENCE_MISSING"]
 return {"mode":"COMPLETE_EVIDENCE_READ_ONLY","product":"2041 / M99 100018","current":live,
 "evidence":{"tax_candidates":tax,"supplier":{"status":"REQUIRES_VERIFIED_SOURCE"},"images":[],"variants":[]},
 "blockers":blockers,"writes_performed":False}
