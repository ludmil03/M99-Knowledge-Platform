from __future__ import annotations
from pathlib import Path
import ast,json,datetime,hashlib

ROOT=Path.home()/"Documents/GitHub/M99-Knowledge-Platform"
TERMS=("hydrate","add-products","supplier_reference","color_images","colour_images","variant","calenda")

def hits(text):
    out=[]
    for i,line in enumerate(text.splitlines(),1):
        low=line.casefold()
        if any(t in low for t in TERMS):
            out.append({"line":i,"text":line[:500]})
    return out[:120]

def routes(text):
    out=[]
    try:tree=ast.parse(text)
    except Exception:return out
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            dec=[]
            for d in n.decorator_list:
                try:dec.append(ast.unparse(d))
                except Exception:pass
            joined=" ".join(dec).casefold()
            if ("hydrate" in joined or "add-products" in joined) and ("get(" in joined or "post(" in joined or "route" in joined):
                out.append({"function":n.name,"line":n.lineno,"decorators":dec})
    return out

def main():
    rows=[]
    for base in (ROOT/"admin-platform/app",ROOT/"tests"):
        if not base.exists():continue
        for p in base.rglob("*.py"):
            try:text=p.read_text(encoding="utf-8",errors="replace")
            except Exception:continue
            if not any(t in text.casefold() for t in TERMS):continue
            rows.append({
              "path":str(p.relative_to(ROOT)).replace("\\","/"),
              "sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "routes":routes(text),
              "hits":hits(text),
            })
    templates=[]
    troot=ROOT/"admin-platform/app/templates"
    if troot.exists():
        for p in troot.rglob("*"):
            if not p.is_file():continue
            try:text=p.read_text(encoding="utf-8",errors="replace")
            except Exception:continue
            low=text.casefold()
            if "supplier ref" in low or "hydrate" in low or "color × size" in low or "color x size" in low:
                templates.append({"path":str(p.relative_to(ROOT)).replace("\\","/"),"hits":hits(text)})
    out=Path.home()/"Desktop"/("M99_R7B_HYDRATION_ROUTE_DISCOVERY_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".json")
    out.write_text(json.dumps({"read_only":True,"python_files":rows,"templates":templates},ensure_ascii=False,indent=2),encoding="utf-8")
    print("[REPORT]",out)
    print("[FILES]",len(rows),"[TEMPLATES]",len(templates))
    for row in rows:
        if row["routes"]:print("[ROUTE]",row["path"],row["routes"])
    print("[DONE] Local repository READ-ONLY discovery; no file mutation.")
if __name__=="__main__":
    main()
