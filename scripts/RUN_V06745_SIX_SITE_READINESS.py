import getpass, json
from pathlib import Path
from datetime import datetime,timezone
from core.six_site_readiness_v06745 import prestashop_probe, wordpress_probe

CFG=Path("config/publish/v0.6.7.4.5_six_site_readiness.json")
cfg=json.loads(CFG.read_text(encoding="utf-8"))
ref=cfg["target_product"]["reference"]
creds={}
print("M99 v0.6.7.4.5 - SIX-SITE PLATFORM & CREDENTIAL READINESS")
print("HTTP policy: GET ONLY")
print("NO WEBSITE WRITE\n")

for site,s in cfg["sites"].items():
    if s["api_family"]=="prestashop_webservice":
        creds[site]={"key":getpass.getpass(f"{site} Webservice API key: ")}
    else:
        creds[site]={"user":input(f"{site} WordPress username: ").strip(),
                     "password":getpass.getpass(f"{site} Application Password: ")}

results={}
for site,s in cfg["sites"].items():
    print(f"\nChecking {site} ...")
    try:
        if s["api_family"]=="prestashop_webservice":
            results[site]=prestashop_probe(site,creds[site]["key"],ref)
        else:
            results[site]=wordpress_probe(site,creds[site]["user"],creds[site]["password"],ref)
    except Exception as e:
        results[site]={"site":site,"ready":False,"error":str(e)}

ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
od=Path("output/v06745_six_site_readiness")/ts
od.mkdir(parents=True,exist_ok=True)
report=od/"SIX_SITE_READINESS.json"
report.write_text(json.dumps({
 "schema_version":"0.6.7.4.5","http_policy":"GET_ONLY","write_allowed":False,
 "credentials_persisted":False,"results":results
},ensure_ascii=False,indent=2),encoding="utf-8")

print("\nREADINESS MATRIX")
for site in cfg["sites"]:
    r=results[site]
    print(f"{site:23} => {'READY' if r.get('ready') else 'NOT READY'}")
    if r.get("languages_discovered"): print("  languages:",r["languages_discovered"])
    if r.get("product_routes_discovered") is not None: print("  product routes:",r["product_routes_discovered"])
    if r.get("error"): print("  error:",r["error"])
all_ready=all(results[x].get("ready") for x in cfg["sites"])
print("\nALL_SITES_READY:", "YES" if all_ready else "NO")
print("WRITE PERFORMED: NO")
print("Credentials persisted: NO")
print("Output:",report)
print("\nNext action:", "RUN v0.6.7.4.4 REAL WRITE_DRAFT only after reviewing this report." if all_ready else "Fix only the NOT READY channel(s), then rerun this single readiness launcher.")
input("\nPress Enter: ")
