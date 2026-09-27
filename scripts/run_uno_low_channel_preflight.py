from pathlib import Path
import sys, json
# scripts/<file>.py -> repository root is exactly parents[1].
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
for p in (ROOT,ADMIN):
 if str(p) not in sys.path: sys.path.insert(0,str(p))
from integrations.channel_preflight.uno_low_preflight import build_preflight,safety_gate
r=build_preflight(live_get=True)
print(json.dumps(r,ensure_ascii=False,indent=2))
g=safety_gate(r)
print("\nSAFETY_GATE:",json.dumps(g))
if not g["pass"]: raise SystemExit(2)
print("\n[SAFE] GET-only public reachability. No website write. No credentials printed.")
