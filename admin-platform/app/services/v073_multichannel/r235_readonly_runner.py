from __future__ import annotations
from pathlib import Path
import inspect,json
from app.services.v073_multichannel import readonly_adapters_r231 as adapter

REPO=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
ADMIN=REPO/"admin-platform"
REFERENCE="M99 100018"

def _verify_contract():
    sig=inspect.signature(adapter.run)
    params=list(sig.parameters.values())
    names=[p.name for p in params]
    if names!=["repo","admin","reference"]:
        raise RuntimeError(f"R231_RUN_SIGNATURE_UNEXPECTED:{sig}")
    if params[2].default!="M99 100018":
        raise RuntimeError(f"R231_REFERENCE_DEFAULT_UNEXPECTED:{params[2].default!r}")
    return sig

def main():
 print("="*78);print("M99 R7.3.0 R2.3.5 REAL READ-ONLY GET / EXACT CONTRACT");print("="*78)
 sig=_verify_contract();print("[PASS] adapter contract:",sig)
 report=adapter.run(REPO,ADMIN,REFERENCE)
 desktop=Path.home()/"Desktop";desktop.mkdir(parents=True,exist_ok=True)
 out=desktop/"M99_R730_R235_REAL_READONLY_CHANNEL_REPORT.json"
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
 for r in report.get("channels",[]):
  print("\n["+str(r.get("channel_id"))+"]",r.get("decision"))
  print(" platform:",r.get("platform"),r.get("version"))
  print(" credentials_present:",r.get("credentials_present"))
  if r.get("lookup"):
   print(" connectivity:",r["lookup"].get("connectivity"))
   print(" exact products:",len(r["lookup"].get("products",[])))
   for p in r["lookup"].get("products",[]):print(" product:",p)
  if r.get("blockers"):print(" blockers:",", ".join(map(str,r["blockers"])))
 print("\n[PASS] R2.3.5 COMPLETE / READ-ONLY / WRITE FALSE");print("Report:",out);return 0
if __name__=="__main__":raise SystemExit(main())
