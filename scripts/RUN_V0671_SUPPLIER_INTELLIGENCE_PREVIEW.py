from pathlib import Path
from datetime import datetime,timezone
import json,requests,re
from urllib.parse import quote
from core.multi_source_evidence_v0671 import commercial,evidence_pack
def search(domain):
    u="https://www.google.com/search?q="+quote("site:"+domain+" Cherokee WW601")
    try:
        t=requests.get(u,headers={"User-Agent":"Mozilla/5.0"},timeout=25).text
        urls=[]
        for x in re.findall(r'https?://[^"& ]+',t):
            if domain in x and ("ww601" in x.lower() or "wwe601" in x.lower()): urls.append(x.split("&")[0])
        return list(dict.fromkeys(urls))[:10]
    except Exception: return []
rows=[]
for name,domain in [("Stenso","stenso.net"),("Palltex","palltex.bg")]:
    urls=search(domain)
    rows.append({"supplier":name,"domain":domain,"candidate_urls":urls,
                 "commercial":commercial(name,urls[0] if urls else None),
                 "status":"CANDIDATES_FOUND" if urls else "NO_PROVEN_PRODUCT_PAGE"})
report={"schema_version":"0.6.7.1","mode":"MULTI_SOURCE_EVIDENCE_SUPPLIER_INTELLIGENCE_PREVIEW",
"http_policy":"GET_ONLY","writes":False,"product":{"brand":"Cherokee","requested":"WWE601","style_family":"WW601"},
"supplier_results":rows,"content_input":evidence_pack([],rows),
"gates":{"commercial_data_ready":False,"content_generation_ready":False,"write_allowed":False}}
out=Path("output/v0671_supplier_intelligence"); out.mkdir(parents=True,exist_ok=True)
f=out/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_CHEROKEE_WW601_MULTI_SOURCE_EVIDENCE.json")
f.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("M99 v0.6.7.1 - MULTI-SOURCE EVIDENCE & SUPPLIER INTELLIGENCE")
print("HTTP policy: GET ONLY")
for x in rows: print(x["supplier"],"=>",x["status"],"| candidates:",len(x["candidate_urls"]))
print("Raw supplier prices: PRESERVE"); print("M99 selling price: NOT SELECTED")
print("Stock: NOT CLAIMED WITHOUT LIVE PRODUCT PAGE"); print("WRITE ALLOWED: NO"); print("Output:",f)
