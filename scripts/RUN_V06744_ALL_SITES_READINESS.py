import json,os
from pathlib import Path
cfg=json.loads(Path("config/publish/v0.6.7.4.4_all_sites_real_write.json").read_text(encoding="utf-8"))
print("M99 v0.6.7.4.4 - ALL SITES WRITE READINESS")
ready=True
for site,c in cfg["sites"].items():
 p=c["platform"];status="READY"
 if p=="SET_ME":status="SET PLATFORM REQUIRED";ready=False
 elif p=="prestashop":
  k="M99_"+site.upper().replace(".","_").replace("-","_")+"_API_KEY"
  if not os.environ.get(k):status="CREDENTIAL REQUIRED: "+k;ready=False
 elif p=="wordpress":
  pre="M99_"+site.upper().replace(".","_").replace("-","_")
  if not os.environ.get(pre+"_USER") or not os.environ.get(pre+"_APP_PASSWORD"):status="CREDENTIALS REQUIRED";ready=False
 print(site,"=>",p,"|",status)
print("ALL_SITES_READY:", "YES" if ready else "NO")
print("REAL WRITE COMMAND: scripts\\RUN_V06744_REAL_ALL_SITES_WRITE_DRAFT.bat")
