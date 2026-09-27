from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
for p in (ROOT,ADMIN):
 if str(p) not in sys.path:sys.path.insert(0,str(p))
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config
from integrations.m99eu_prestashop.connection_diagnostic import diagnose,classify
def main():
 cfg=load_m99eu_prestashop_config()
 r=diagnose(cfg.base_url,cfg.api_key,min(cfg.timeout_seconds,20))
 print(json.dumps(r,ensure_ascii=False,indent=2))
 print("CLASSIFICATION:",classify(r))
 print("[SAFE] GET only, one attempt per HTTP probe, no credential printed, no write.")
 return 0
if __name__=="__main__":raise SystemExit(main())
