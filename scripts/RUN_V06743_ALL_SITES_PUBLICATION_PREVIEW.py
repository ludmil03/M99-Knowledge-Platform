from pathlib import Path
from datetime import datetime,timezone
import json
from core.cherokee_all_sites_publish_v06743 import build_all_sites_package

d=build_all_sites_package()
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out=Path("output/v06743_all_sites_publication");out.mkdir(parents=True,exist_ok=True)
f=out/f"{ts}_CHEROKEE_WW601_ALL_SITES_PUBLICATION_PACKAGE.json"
f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

print("M99 v0.6.7.4.3 - ALL SITES CHANNEL-SPECIFIC PUBLICATION PACKAGE")
print("="*80)
print("ALL SITES REQUIRED: YES")
for site,m in d["publication_manifest"].items():
 print(site,"=>",m["mode"],"|",m["adapter_status"],"| languages:",",".join(m["required_languages"]))
print("Channel duplication guard:", "PASS" if d["similarity_guard"]["all_pass"] else "FAIL")
print("WRITE MODE: WRITE_DRAFT")
print("ACTIVE AFTER WRITE: NO")
print("LIVE PUBLISH: NO")
print("PARTIAL SUCCESS ACCEPTED: NO")
print("Output:",f)
