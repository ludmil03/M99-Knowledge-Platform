import json,sys
from pathlib import Path
R=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform");sys.path.insert(0,str(R/"admin-platform"))
from app.services.v073_phase46.secure_integration_settings import effective_m99eu_credentials
from app.services.v073_phase45.m99eu_operator_single_publish import _curl
from app.services.v073_phase46.product_2041_live_readonly_preflight import inspect
enabled,key,source=effective_m99eu_credentials()
if not enabled or not key:raise SystemExit("[STOP] m99.eu credentials unavailable")
print("M99 PRODUCT 2041 LIVE READ-ONLY PREFLIGHT - GET ONLY")
r=inspect(key,_curl);print(json.dumps(r,indent=2,ensure_ascii=False))
p=R/"var/phase46_draft_enrichment/product_2041_live_readonly_preflight.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
print("[PASS] GET-only live inspection complete");print("[SAFE] Product 2041 was NOT modified.")
