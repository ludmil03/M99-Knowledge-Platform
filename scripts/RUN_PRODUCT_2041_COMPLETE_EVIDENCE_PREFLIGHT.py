import json,sys
from pathlib import Path
R=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"); sys.path.insert(0,str(R/"admin-platform"))
from app.services.v073_phase46.secure_integration_settings import effective_m99eu_credentials
from app.services.v073_phase45.m99eu_operator_single_publish import _curl
from app.services.v073_phase46.product_2041_complete_evidence_preflight import inspect
enabled,key,source=effective_m99eu_credentials()
if not enabled or not key: raise SystemExit("[STOP] m99.eu credentials unavailable")
print("M99 R7K.4 PRODUCT 2041 COMPLETE EVIDENCE PREFLIGHT R1")
print("LIVE READ-ONLY / GET ONLY / FAIL CLOSED")
r=inspect(key,_curl)
print(json.dumps(r,indent=2,ensure_ascii=False))
out=R/"var/phase46_draft_enrichment/product_2041_complete_evidence_preflight.json"
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
print("[PASS] COMPLETE EVIDENCE PREFLIGHT FINISHED")
print("[SAFE] NO WEBSITE WRITE / NO DB MIGRATION / NO COMMIT / NO PUSH")
print("[REPORT]",out)
