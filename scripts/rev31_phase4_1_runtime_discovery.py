from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/"admin-platform/app"

def scan(root, suffix, patterns):
    out=[]
    for p in root.rglob("*"+suffix):
        try: text=p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        score=sum(1 for x in patterns if re.search(x,text,re.I))
        if score: out.append((score,str(p.relative_to(ROOT)).replace("\\","/")))
    return sorted(out,reverse=True)[:20]

report={
 "supplier_browser_python":scan(APP,".py",[r"supplier-browser",r"ImportJob",r"preflight",r"canonical"]),
 "supplier_templates":scan(APP/"templates",".html",[r"Browse\s*&\s*Select",r"Open Supplier Browser",r"Direct Supplier Selection"]),
 "draft_import_references":scan(APP,".py",[r"ImportJob",r"DRAFT",r"ImportJobItem"]),
 "preflight_references":scan(APP,".py",[r"preflight",r"PREFLIGHT_READY"]),
 "canonical_preview_references":scan(APP,".py",[r"Canonical Preview",r"canonical_preview",r"publishable"]),
}
print(json.dumps(report,indent=2,ensure_ascii=False))
