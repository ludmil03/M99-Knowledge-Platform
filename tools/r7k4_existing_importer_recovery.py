from __future__ import annotations
from pathlib import Path
import subprocess,json,hashlib,os,shutil
TERMS=("bultex99","stenso","exact image candidates","109168","06200368.39","five-channel","five channel","supplier connector","webp","apify")
EXTS={".py",".md",".txt",".json",".ps1",".bat",".yaml",".yml"}
def find_git():
    for x in (os.environ.get("M99_GIT_EXE"), shutil.which("git")):
        if x and Path(x).exists(): return str(x)
    c=list((Path.home()/"AppData/Local/GitHubDesktop").glob("app-*/resources/app/git/cmd/git.exe"))
    if c:return str(sorted(c,reverse=True)[0])
    raise RuntimeError("GIT_NOT_FOUND")
def _run(repo,*args):
 p=subprocess.run([find_git(),*args],cwd=repo,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 return p.stdout if p.returncode==0 else ""
def scan_worktree(repo):
 hits=[]; excluded={".git",".venv","venv","node_modules","__pycache__","var"}
 for p in repo.rglob("*"):
  if not p.is_file() or p.suffix.lower() not in EXTS or any(x in excluded for x in p.parts):continue
  try:txt=p.read_text(encoding="utf-8",errors="replace")
  except OSError:continue
  f=[t for t in TERMS if t in txt.lower()]
  if f:hits.append({"path":str(p.relative_to(repo)),"terms":f,"sha256":hashlib.sha256(txt.encode()).hexdigest()})
 return hits
def scan_history(repo):
 commits=_run(repo,"log","--all","--format=%H").splitlines(); fh=[]; ch=[]
 for sha in commits:
  for n in _run(repo,"ls-tree","-r","--name-only",sha).splitlines():
   if any(t in n.lower() for t in ("bultex","stenso","import","supplier","image")):fh.append({"commit":sha,"path":n})
 for term in TERMS:
  for row in _run(repo,"log","--all","-S",term,"--format=%H|%cs|%s","--").splitlines():
   a=row.split("|",2)
   if len(a)==3:ch.append({"term":term,"commit":a[0],"date":a[1],"subject":a[2]})
 return commits,fh,ch
def main(repo):
 wt=scan_worktree(repo); commits,fh,ch=scan_history(repo)
 ev=[{"source":"WORKTREE",**x} for x in wt]+[{"source":"GIT_HISTORY_FILENAME",**x} for x in fh]+[{"source":"GIT_HISTORY_CONTENT",**x} for x in ch]
 return {"mode":"READ_ONLY_RECOVERY","git_exe":find_git(),"status":"RECOVERY_EVIDENCE_FOUND" if ev else "LEGACY_IMPORTER_NOT_FOUND",
 "commit_count_scanned":len(commits),"worktree_hits":wt,"history_filename_hits":fh,"history_content_hits":ch,"recovery_evidence":ev,
 "integration_target":{"source_adapter":"RECOVER EXISTING Bultex99/Stenso acquisition; do not rewrite",
 "canonical_bridge":"ProductCandidate -> Canonical/DRAFT","preserve":["price acquisition","variant acquisition","image acquisition","WebP/media processing"],
 "replace_with_current_governance":["identity allocation","duplicate guard","pricing policy","VAT resolution","multi-channel selection","hidden publish","readback/QA"],"live_write":False},
 "writes_performed":False}
if __name__=="__main__":
 repo=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform"); r=main(repo); print(json.dumps(r,indent=2,ensure_ascii=False))
 p=repo/"var/phase46_draft_enrichment/r7k4_existing_importer_recovery_r1.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
 print("[PASS] READ-ONLY repository/history recovery scan complete");print("[SAFE] NO WEBSITE WRITE / NO DB MIGRATION / NO COMMIT / NO PUSH");print("[REPORT]",p)
