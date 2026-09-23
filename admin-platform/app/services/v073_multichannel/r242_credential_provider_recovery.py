from __future__ import annotations
from pathlib import Path
import ast, json, re

REPO=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
ADMIN=REPO/"admin-platform"
TARGETS={"run_m99eu_test","run_dolibarr_test","config","credential_status","real_write",
         "execute_live_hidden_update","controlled_publish"}
SECRET_WORDS=("key","token","secret","password","credential","consumer_secret","app_password")
SKIP_DIRS={".git",".venv","venv","node_modules","__pycache__",".pytest_cache","dist","build"}
MAX_FILE=2_000_000

def is_secret_name(s):
    x=s.lower()
    return any(w in x for w in SECRET_WORDS)

def safe_const(v):
    if isinstance(v,(str,int,float,bool)) or v is None:
        if isinstance(v,str) and (len(v)>120 or is_secret_name(v)): return "<REDACTED>"
        return v
    return "<NONSCALAR>"

def iter_py():
    for base in (ADMIN, REPO/"core", REPO/"scripts"):
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            if any(part in SKIP_DIRS for part in p.parts): continue
            try:
                if p.stat().st_size<=MAX_FILE: yield p
            except OSError: pass

def dotted(n):
    if isinstance(n,ast.Name): return n.id
    if isinstance(n,ast.Attribute):
        a=dotted(n.value); return (a+"." if a else "")+n.attr
    return ""

def analyze(p):
    try:
        text=p.read_text(encoding="utf-8",errors="replace"); tree=ast.parse(text)
    except Exception:
        return None
    rel=str(p.relative_to(REPO))
    funcs=[]; calls=[]; env_names=[]; config_files=[]
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            if n.name in TARGETS or any(t in n.name.lower() for t in ("config","credential","publish","preflight")):
                funcs.append({"name":n.name,"args":[a.arg for a in n.args.args]})
        elif isinstance(n,ast.Call):
            name=dotted(n.func); leaf=name.split(".")[-1]
            if leaf in TARGETS:
                args=[]
                for a in n.args:
                    if isinstance(a,ast.Name): args.append({"kind":"name","value":a.id})
                    elif isinstance(a,ast.Attribute): args.append({"kind":"attr","value":dotted(a)})
                    elif isinstance(a,ast.Constant): args.append({"kind":"const","value":safe_const(a.value)})
                    else: args.append({"kind":type(a).__name__,"value":"<EXPRESSION>"})
                kws=[]
                for k in n.keywords:
                    val=k.value
                    if isinstance(val,ast.Name): vv=val.id
                    elif isinstance(val,ast.Attribute): vv=dotted(val)
                    elif isinstance(val,ast.Constant): vv=safe_const(val.value)
                    else: vv="<EXPRESSION>"
                    if k.arg and is_secret_name(k.arg): vv="<REDACTED_BINDING>"
                    kws.append({"name":k.arg,"value":vv})
                calls.append({"callee":name,"args":args,"keywords":kws,"line":getattr(n,"lineno",None)})
            if leaf in ("getenv","get") and n.args and isinstance(n.args[0],ast.Constant):
                v=n.args[0].value
                if isinstance(v,str) and re.fullmatch(r"[A-Z][A-Z0-9_]{2,}",v): env_names.append(v)
            if leaf in ("open","read_text","load","dotenv_values","load_dotenv"):
                for a in n.args[:1]:
                    if isinstance(a,ast.Constant) and isinstance(a.value,str):
                        s=a.value
                        if any(x in s.lower() for x in (".env",".json",".toml",".yaml",".yml","config")):
                            config_files.append(s)
    if funcs or calls or env_names or config_files:
        return {"path":rel,"functions":funcs,"calls":calls,
                "env_names":sorted(set(env_names)),"config_file_literals":sorted(set(config_files))}
    return None

def main():
    print("="*78);print("M99 R7.3.0 R2.4.2 EXISTING CREDENTIAL PROVIDER RECOVERY / NO NETWORK");print("="*78)
    if not REPO.is_dir() or not ADMIN.is_dir(): print("[STOP] repo/admin missing"); return 2
    findings=[]
    for p in iter_py():
        r=analyze(p)
        if r: findings.append(r)
    callers=[{"path":f["path"],**c} for f in findings for c in f["calls"] if c["callee"].split(".")[-1] in TARGETS]
    envs=sorted({x for f in findings for x in f["env_names"]})
    configs=sorted({x for f in findings for x in f["config_file_literals"]})
    report={"version":"R7.3.0-R2.4.2","network":False,"write_allowed":False,
            "target_reference":"M99 100018","m99eu_existing_id":2041,
            "callers":callers,"env_names":envs,"config_file_literals":configs,"findings":findings}
    desktop=Path.home()/"Desktop"; desktop.mkdir(parents=True,exist_ok=True)
    out=desktop/"M99_R730_R242_CREDENTIAL_PROVIDER_RECOVERY.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"[PASS] Python files with relevant contracts: {len(findings)}")
    print(f"[PASS] Target caller sites: {len(callers)}")
    print("\nCALLER CHAIN (values never printed):")
    for c in callers[:80]:
        print(f" - {c['path']}:{c['line']} -> {c['callee']}")
        if c["args"]: print("   args:",", ".join(str(x["value"]) for x in c["args"]))
        if c["keywords"]: print("   kwargs:",", ".join(str(x["name"])+"="+str(x["value"]) for x in c["keywords"]))
    print("\nENV BINDING NAMES ONLY:")
    for n in envs: print(" -",n)
    print("\nCONFIG FILE LITERALS ONLY:")
    for n in configs: print(" -",n)
    print("\nWRITE_ALLOWED: FALSE");print("NETWORK: FALSE");print("Report:",out)
    print("[PASS] R2.4.2 recovery complete; no credential values exposed.")
    return 0
if __name__=="__main__": raise SystemExit(main())
