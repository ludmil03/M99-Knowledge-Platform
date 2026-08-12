from pathlib import Path
from datetime import datetime,timezone
import json
from core.robust_supplier_discovery_v067112 import discover_stenso,discover_palltex,run,merge
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=Path("output/v067112_robust_supplier_discovery");out.mkdir(parents=True,exist_ok=True)
a=run(discover_stenso());b=run(discover_palltex());m=merge(a,b)
r={"schema_version":"0.6.7.1.2","http_policy":"GET_ONLY","writes":False,"product":{"brand":"Cherokee","requested":"WWE601","target":"NAVY/DARK BLUE"},"suppliers":{"Stenso":a,"Palltex":b},"merge":m,"write_allowed":False}
f=out/f"{ts}_CHEROKEE_WWE601_ROBUST_SUPPLIER_DISCOVERY.json";f.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print("M99 v0.6.7.1.2 - ROBUST SUPPLIER DISCOVERY & DIRECT PAGE EXTRACTION");print("HTTP policy: GET ONLY")
for s in [a,b]:
 print("\n"+s["supplier"],"| discovered:",len(s["candidates"]),"| fetched:",len(s["pages"]))
 print(" methods:",",".join(sorted(set(x["method"] for x in s["candidates"]))) or "NONE")
 for i,x in enumerate(s["pages"],1):
  print(f" {i}. {x['identity']['class']} | score {x['identity']['score']} | ref={x['supplier_reference']} | stock={x['availability']} | sizes={len(x['sizes'])}")
  print("    title:",x["title"]);print("    prices:",x["raw_price_observations"][:6]);print("    url:",x["source_url"])
print("\nSupplier prices: PRESERVED SEPARATELY");print("Supplier stock: PRESERVED SEPARATELY");print("M99 selling price: NOT SELECTED");print("CONTENT GENERATION READY: NO");print("WRITE ALLOWED: NO");print("Output:",f)
