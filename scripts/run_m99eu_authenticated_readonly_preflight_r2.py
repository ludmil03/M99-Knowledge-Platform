from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
for p in (ROOT,ADMIN):
 if str(p) not in sys.path:sys.path.insert(0,str(p))
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config
from integrations.m99eu_prestashop.readonly_preflight_r2 import OneShotBasicGetTransport,run_preflight
def main():
 cfg=load_m99eu_prestashop_config()
 t=OneShotBasicGetTransport(cfg.base_url,cfg.api_key,min(cfg.timeout_seconds,20))
 r=run_preflight(cfg,t)
 print(json.dumps(r,ensure_ascii=False,indent=2))
 print("[PASS] M99.EU AUTHENTICATED READ-ONLY PREFLIGHT R2")
 print("[SAFE] GET only / no retry / credential not printed / no write")
 return 0
if __name__=="__main__":raise SystemExit(main())
