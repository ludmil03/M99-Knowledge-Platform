from __future__ import annotations
from pathlib import Path
import json
from app.services.v073_multichannel.readonly_adapters_r231 import run
def main():
 print("="*78);print("M99 R7.3.0 R2.3.3 REAL READ-ONLY GET / MODULE MODE");print("="*78)
 report=run("M99 100018")
 for r in report["channels"]:
  print("\n["+r["channel_id"]+"]",r["decision"]);print(" platform:",r["platform"],r["version"]);print(" credentials_present:",r["credentials_present"])
  if r.get("lookup"):
   print(" connectivity:",r["lookup"]["connectivity"]);print(" exact products:",len(r["lookup"]["products"]))
   for product in r["lookup"]["products"]:print(" product:",product)
  if r.get("blockers"):print(" blockers:",", ".join(r["blockers"]))
 desktop=Path.home()/"Desktop";desktop.mkdir(parents=True,exist_ok=True)
 out=desktop/"M99_R730_R233_REAL_READONLY_CHANNEL_REPORT.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print("\n[PASS] R2.3.3 COMPLETE / GET ONLY / WRITE FALSE");print("Report:",out);return 0
if __name__=="__main__":raise SystemExit(main())
