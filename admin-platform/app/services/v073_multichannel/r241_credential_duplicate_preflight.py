from __future__ import annotations
from pathlib import Path
import ast, inspect, json, os, re
from app.services.v073_multichannel import readonly_adapters_r231 as r231

REPO=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
ADMIN=REPO/"admin-platform"
REFERENCE="M99 100018"
M99EU_EXISTING_ID=2041

CANDIDATES=[
 ADMIN/"app/services/v073_phase45/real_test_center.py",
 REPO/"core/cherokee_real_publish_v0675.py",
 ADMIN/"app/services/v073_multichannel/readonly_adapters_r231.py",
]

SENSITIVE=re.compile(r"(?i)(key|token|secret|password|pass|credential)")
ENV_NAME=re.compile(r"^[A-Z][A-Z0-9_]{2,}$")

def _safe(v):
    if v is None: return None
    if isinstance(v,(bool,int,float)): return v
    return "<PRESENT_REDACTED>" if str(v) else "<EMPTY>"

def _source_contracts():
    out=[]
    for p in CANDIDATES:
        item={"path":str(p.relative_to(REPO)),"exists":p.is_file(),"functions":[],"env_names":[]}
        if p.is_file():
            txt=p.read_text(encoding="utf-8",errors="replace")
            tree=ast.parse(txt)
            for n in ast.walk(tree):
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    item["functions"].append({"name":n.name,"args":[a.arg for a in n.args.args]})
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ("getenv","get"):
                    if n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and ENV_NAME.match(n.args[0].value):
                        item["env_names"].append(n.args[0].value)
            item["env_names"]=sorted(set(item["env_names"]))
        out.append(item)
    return out

def _presence(names):
    # Values are never returned or printed. Presence only.
    return {n: bool(os.environ.get(n)) for n in names}

def _find_exact_product(report):
    hits=[]
    for ch in report.get("channels",[]):
        products=(ch.get("lookup") or {}).get("products") or []
        for p in products:
            ref=str(p.get("reference") or p.get("sku") or "").strip()
            if ref==REFERENCE:
                hits.append({"channel_id":ch.get("channel_id"),"id":p.get("id"),"reference":ref})
    return hits

def main():
    print("="*78)
    print("M99 R7.3.0 R2.4.1 CREDENTIAL BINDING + LIVE DUPLICATE PREFLIGHT")
    print("GET ONLY / WRITE FALSE")
    print("="*78)
    sig=inspect.signature(r231.run)
    if [p.name for p in sig.parameters.values()] != ["repo","admin","reference"]:
        print("[STOP] R231 contract changed:",sig); return 20

    contracts=_source_contracts()
    env_names=sorted({n for c in contracts for n in c["env_names"]})
    presence=_presence(env_names)

    print("[PASS] R231 contract:",sig)
    print("\nCredential/config bindings (presence only; values REDACTED):")
    for n in env_names:
        print(" -",n,":","PRESENT" if presence[n] else "NOT_PRESENT")

    # Proven R231 adapter owns all HTTP behavior. This call is read-only by its accepted contract.
    report=r231.run(REPO,ADMIN,REFERENCE)
    hits=_find_exact_product(report)

    # Hard duplicate safety assertion for m99.eu.
    m99=[h for h in hits if h["channel_id"]=="m99.eu"]
    duplicate_guard={"reference":REFERENCE,"expected_existing_m99eu_id":M99EU_EXISTING_ID,
                     "m99eu_exact_hits":m99,"create_allowed_m99eu":False}
    if m99:
        ids={str(x.get("id")) for x in m99}
        duplicate_guard["identity_match"]=str(M99EU_EXISTING_ID) in ids
        duplicate_guard["decision"]="UPDATE_EXISTING" if duplicate_guard["identity_match"] else "BLOCKED_IDENTITY_CONFLICT"
    else:
        duplicate_guard["identity_match"]=False
        duplicate_guard["decision"]="BLOCKED_EXISTING_2041_NOT_PROVEN"

    matrix=[]
    for ch in report.get("channels",[]):
        cid=ch.get("channel_id")
        exact=[h for h in hits if h["channel_id"]==cid]
        decision=ch.get("decision","BLOCKED")
        if cid=="m99.eu":
            decision=duplicate_guard["decision"]
        elif exact:
            decision="UPDATE_EXISTING"
        elif decision not in ("BLOCKED","NOT_SELECTED"):
            decision="CREATE_CANDIDATE"
        matrix.append({
            "channel_id":cid,"platform":ch.get("platform"),"version":ch.get("version"),
            "credentials_present":ch.get("credentials_present"),
            "connectivity":(ch.get("lookup") or {}).get("connectivity"),
            "exact_hits":exact,"decision":decision,"blockers":ch.get("blockers") or []
        })

    final={"version":"R7.3.0-R2.4.1","reference":REFERENCE,"write_allowed":False,
           "source_contracts":contracts,
           "credential_presence":presence,
           "duplicate_guard":duplicate_guard,
           "matrix":matrix,
           "raw_r231_report":report}
    desktop=Path.home()/"Desktop";desktop.mkdir(parents=True,exist_ok=True)
    out=desktop/"M99_R730_R241_CREDENTIAL_BINDING_DUPLICATE_PREFLIGHT.json"
    out.write_text(json.dumps(final,ensure_ascii=False,indent=2,default=str),encoding="utf-8")

    print("\nCHANNEL MATRIX")
    for x in matrix:
        print(f"[{x['channel_id']}] {x['decision']} | credentials={x['credentials_present']} | connectivity={x['connectivity']}")
        if x["exact_hits"]: print("  exact:",x["exact_hits"])
        if x["blockers"]: print("  blockers:",", ".join(map(str,x["blockers"])))
    print("\nM99.EU DUPLICATE GUARD:",duplicate_guard["decision"])
    print("CREATE_ALLOWED_M99EU: FALSE")
    print("WRITE_ALLOWED: FALSE")
    print("Report:",out)
    print("[PASS] R2.4.1 completed / GET-only preflight / no website write")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
