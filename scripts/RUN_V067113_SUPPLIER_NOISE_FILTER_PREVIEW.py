from pathlib import Path
from datetime import datetime,timezone
import json,requests
from core.supplier_noise_filter_v067113 import page_type,strip_tags,extract_title,classify,dedupe

UA={"User-Agent":"Mozilla/5.0 Chrome/150 Safari/537.36"}
URLS=[
"https://stenso.net/produkt/medicinski-tuniki/4443-damska-medicinska-tunika-cherokee-v-neck-navy-wwe601",
"https://stenso.net/en/produkt/medical-tunics/4443-cherokee-v-neck-navy-wwe601-women-s-medical-tunic",
"https://stenso.net/produkt/medicinski-komplekti/4444-damska-medicinska-tunika-cherokee-v-neck-grey-wwe601",
"https://stenso.net/produkt/medicinski-komplekti/4573-damska-medicinska-tunika-cherokee-v-neck-black-wwe601",
"https://stenso.net/product?s=Cherokee+WWE601",
"https://stenso.net/39-medicinski-tuniki",
"https://stenso.net/14408-large_default/damska-medicinska-tunika-cherokee-v-neck-navy-wwe601.jpg"]

rows=[]
for url in URLS:
    try:
        r=requests.get(url,headers=UA,timeout=30,allow_redirects=True); r.raise_for_status()
        html=r.text if "text/html" in r.headers.get("content-type","") else ""
        title,src=extract_title(html)
        rows.append({"source_url":r.url,"title":title,"title_source":src,
                     **classify(r.url,title,strip_tags(html))})
    except Exception as e:
        rows.append({"source_url":url,"page_type":page_type(url),"evidence_role":"FETCH_ERROR",
                     "commercial_allowed":False,"error":str(e)[:250]})

rows=dedupe(rows)
exact=[x for x in rows if x.get("evidence_role")=="EXACT_PRODUCT"]
wrong=[x for x in rows if x.get("evidence_role")=="SAME_MODEL_WRONG_COLOUR"]
noise=[x for x in rows if x.get("evidence_role")=="DISCOVERY_ONLY"]

out=Path("output/v067113_supplier_noise_filter"); out.mkdir(parents=True,exist_ok=True)
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
f=out/f"{ts}_CHEROKEE_WWE601_PRODUCT_PAGE_CANONICALIZATION.json"
f.write_text(json.dumps({"schema_version":"0.6.7.1.3","http_policy":"GET_ONLY","records":rows,
"exact":exact,"wrong_colour":wrong,"discovery_only":noise,
"palltex_status":"UNRESOLVED_NO_EVIDENCE_INVENTED","m99_selling_price":None,
"content_generation_ready":False,"write_allowed":False},ensure_ascii=False,indent=2),encoding="utf-8")

print("M99 v0.6.7.1.3 - PRODUCT PAGE CANONICALIZATION & SUPPLIER NOISE FILTER")
print("HTTP policy: GET ONLY")
for x in rows:
    print("\n%s | %s | commercial=%s"%(x.get("evidence_role"),x.get("page_type"),x.get("commercial_allowed")))
    print(" title:",x.get("title"),"| source:",x.get("title_source"))
    print(" url:",x.get("canonical_url",x["source_url"]))
print("\nExact target product records:",len(exact))
print("Wrong-colour product records:",len(wrong))
print("Discovery-only records:",len(noise))
print("Search/category/image commercial evidence: BLOCKED")
print("Palltex: UNRESOLVED - NO EVIDENCE INVENTED")
print("M99 selling price: NOT SELECTED")
print("CONTENT GENERATION READY: NO")
print("WRITE ALLOWED: NO")
print("Output:",f)
