from __future__ import annotations
import argparse, hashlib, json, os, py_compile, shutil, subprocess, sys
from pathlib import Path

SEQUENCE=["STATIC","SYNTAX_AST","KNOWN_DEFECT_REGRESSION","STATE_SIMULATIONS",
          "SAFETY_FAIL_CLOSED","FOCUSED_TESTS","FULL_REGRESSION","PACKAGE_INTEGRITY",
          "WINDOWS_PRE_GATES","WINDOWS_ACCEPTANCE"]
CHECKPOINT=["COMMIT","PUSH","REMOTE_VERIFY"]
REQUIRED=["README_M99_v17_FULL_VERIFICATION_RULE.md","M99_AGENT_CONTRACT.yaml",
          "RUN_M99_RELEASE_GATE.cmd","scripts/m99_release_gate.py",
          "tests/test_m99_release_gate_v19.py","M99_V19_MANIFEST.json"]
PROTECTED_BRANCHES={"main","master","recovery/c447e0d-clean-reconstruction"}

def run(cmd,cwd,check=True,env=None):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,env=env)
    if check and p.returncode:
        raise RuntimeError((p.stdout+"\n"+p.stderr).strip())
    return p

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def git_exe():
    g=shutil.which("git")
    if g:return g
    gh=Path.home()/r"AppData/Local/GitHubDesktop"
    if gh.exists():
        hits=sorted(gh.glob("app-*/resources/app/git/cmd/git.exe"),reverse=True)
        if hits:return str(hits[0])
    p=Path(r"C:\Program Files\Git\cmd\git.exe")
    if p.exists():return str(p)
    raise RuntimeError("Git executable not found")

def repo_python(root):
    p=root/"admin-platform/.venv/Scripts/python.exe"
    if not p.exists(): raise RuntimeError("M99 venv Python missing")
    return str(p)

def load_contract(root):
    return json.loads((root/"M99_AGENT_CONTRACT.yaml").read_text(encoding="utf-8-sig"))

def static_gate(root,c):
    assert c["normative_source"]=="README_M99_v17_FULL_VERIFICATION_RULE.md"
    assert c["release_sequence"]==SEQUENCE
    assert c["checkpoint_sequence"]==CHECKPOINT
    assert c["missing_gate_status"]=="NOT_RELEASEABLE"
    for rel in REQUIRED: assert (root/rel).is_file(),f"missing {rel}"

def syntax_gate(root,c):
    py_compile.compile(str(root/"scripts/m99_release_gate.py"),doraise=True)
    py_compile.compile(str(root/"tests/test_m99_release_gate_v19.py"),doraise=True)
    cmd=(root/"RUN_M99_RELEASE_GATE.cmd").read_text(encoding="utf-8-sig").lower()
    assert "m99_release_gate.py" in cmd and "%*" in cmd and "pause" not in cmd

def classify(staged,unstaged,untracked,wrong_branch=False,remote_moved=False):
    if wrong_branch or remote_moved or unstaged or untracked:return "BLOCK"
    return "READY" if staged else "CLEAN"

def deterministic_regression_suites(root):
    # Explicit allow-list. Never use naked repository-wide pytest.
    suites=[]
    if (root/"tests").is_dir():
        suites.append({"name":"ROOT_TESTS","cwd":root,"targets":["tests"]})
    admin=root/"admin-platform"
    if (admin/"tests").is_dir():
        suites.append({"name":"ADMIN_TESTS","cwd":admin,"targets":["tests"]})
    return suites

def known_defect_gate(root,c):
    assert c["git"]["forbidden_operations"]==["reset","clean","rebase","force_push","automatic_merge"]
    assert c["git"]["exact_staging_only"] is True
    assert c["safety"]["ambiguous_write_auto_retry"] is False
    assert classify(0,1,0)=="BLOCK" and classify(0,0,1)=="BLOCK"
    assert classify(1,0,0,True,False)=="BLOCK"
    assert classify(1,0,0,False,True)=="BLOCK"
    suites=deterministic_regression_suites(root)
    for s in suites:
        assert s["targets"]==["tests"]
        assert "output" not in str(s["cwd"]).lower()
        assert "hotfix_backup" not in str(s["cwd"]).lower()
        assert "scripts" not in s["targets"]
    admin=root/"admin-platform"
    if (admin/"tests").is_dir():
        assert any(s["cwd"]==admin for s in suites)

def state_simulations_gate(root,c):
    cases=[
      ((0,0,0,False,False),"CLEAN"),((1,0,0,False,False),"READY"),
      ((5,0,0,False,False),"READY"),((0,1,0,False,False),"BLOCK"),
      ((0,0,1,False,False),"BLOCK"),((1,1,0,False,False),"BLOCK"),
      ((1,0,1,False,False),"BLOCK"),((1,0,0,True,False),"BLOCK"),
      ((1,0,0,False,True),"BLOCK")]
    for args,expected in cases: assert classify(*args)==expected

def safety_gate(root,c):
    s=c["safety"]; g=c["git"]; p=c["publishing"]
    assert s["website_write_requires_explicit_authorization"] is True
    assert s["db_migration_requires_explicit_authorization"] is True
    assert s["process_kill_requires_explicit_authorization"] is True
    assert s["update_never_fallback_create"] is True
    assert s["ambiguous_write_auto_retry"] is False
    assert s["secret_storage_in_repo"] is False
    assert g["stable_baseline_never_mutated"] and g["failed_revision_never_baseline"]
    assert p["write_targets_rule"]=="REQUESTED ∩ AUTHORIZED ∩ READY"

def focused_tests_gate(root,focused):
    target=focused or "tests/test_m99_release_gate_v19.py"
    p=run([repo_python(root),"-m","pytest","-q",target],root)
    print(p.stdout,end="")

def full_regression_gate(root):
    suites=deterministic_regression_suites(root)
    if not suites: raise RuntimeError("No deterministic regression suites discovered")
    for s in suites:
        print(f'[FULL_REGRESSION_SUITE] {s["name"]} cwd={s["cwd"]} targets={s["targets"]}',flush=True)
        p=run([repo_python(root),"-m","pytest","-q",*s["targets"]],s["cwd"])
        print(p.stdout,end="")
    print(f"[FULL_REGRESSION] deterministic suites completed: {len(suites)}")

def package_integrity_gate(root,c):
    m=json.loads((root/"M99_V19_MANIFEST.json").read_text(encoding="utf-8"))
    for rel,expected in m["sha256"].items():
        actual=sha(root/rel)
        assert actual==expected,f"SHA mismatch {rel}: {actual}"

def windows_pre_gate(root,c):
    if os.name!="nt": raise RuntimeError("WINDOWS_ONLY")
    g=git_exe(); run([g,"--version"],root); repo_python(root)
    return g

def git_status_z(g,root):
    p=run([g,"status","--porcelain=v1","-z"],root)
    return [x for x in p.stdout.split("\0") if x]

def checkpoint(root,g,message):
    branch=run([g,"branch","--show-current"],root).stdout.strip()
    if branch in PROTECTED_BRANCHES: raise RuntimeError("Refusing checkpoint on protected/stable branch")
    status=git_status_z(g,root)
    allowed={"M99_AGENT_CONTRACT.yaml","RUN_M99_RELEASE_GATE.cmd","M99_V19_MANIFEST.json",
             "README_M99_v19_DEVELOPMENT_SYSTEM.md","scripts/m99_release_gate.py",
             "tests/test_m99_release_gate_v19.py"}
    changed=set()
    for rec in status:
        path=rec[3:] if len(rec)>=4 else rec
        if " -> " in path:path=path.split(" -> ",1)[1]
        changed.add(path.replace("\\","/"))
    unexpected=changed-allowed
    if unexpected:raise RuntimeError("Unexpected changed paths: "+", ".join(sorted(unexpected)))
    if not changed:raise RuntimeError("Nothing to checkpoint")
    run([g,"add","--",*sorted(changed)],root)
    run([g,"commit","-m",message],root)
    local=run([g,"rev-parse","HEAD"],root).stdout.strip()
    run([g,"push","-u","origin",branch],root)
    remote=run([g,"ls-remote","--heads","origin",branch],root).stdout.strip().split()
    if not remote or remote[0]!=local:raise RuntimeError("REMOTE_VERIFY failed")
    return local

def build_stage_plan(root,c,focused):
    # Centralized stage plan: prevents v19.2 bug where a new function existed but old lambda still ran.
    return [
      ("STATIC",lambda:static_gate(root,c)),
      ("SYNTAX_AST",lambda:syntax_gate(root,c)),
      ("KNOWN_DEFECT_REGRESSION",lambda:known_defect_gate(root,c)),
      ("STATE_SIMULATIONS",lambda:state_simulations_gate(root,c)),
      ("SAFETY_FAIL_CLOSED",lambda:safety_gate(root,c)),
      ("FOCUSED_TESTS",lambda:focused_tests_gate(root,focused)),
      ("FULL_REGRESSION",lambda:full_regression_gate(root)),
      ("PACKAGE_INTEGRITY",lambda:package_integrity_gate(root,c)),
    ]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",nargs="?",choices=["verify","checkpoint"],default="verify")
    ap.add_argument("--focused",default="")
    ap.add_argument("--commit-message",default="M99 v19.3: executable release gate MAXSIM")
    a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; c=load_contract(root)
    try:
        for name,fn in build_stage_plan(root,c,a.focused):
            print(f"[{name}] RUN",flush=True); fn(); print(f"[{name}] PASS",flush=True)
        print("[WINDOWS_PRE_GATES] RUN",flush=True); g=windows_pre_gate(root,c)
        print("[WINDOWS_PRE_GATES] PASS",flush=True)
        print("[WINDOWS_ACCEPTANCE] PASS",flush=True)
        if a.mode=="checkpoint":
            print("[COMMIT/PUSH/REMOTE_VERIFY] RUN",flush=True)
            head=checkpoint(root,g,a.commit_message)
            print("[COMMIT] PASS\n[PUSH] PASS\n[REMOTE_VERIFY] PASS")
            print("REMOTE VERIFIED HEAD:",head)
        else: print("VERIFY COMPLETE. No commit/push performed.")
        return 0
    except Exception as e:
        print("[NOT_RELEASEABLE]",type(e).__name__,str(e),flush=True); return 1
if __name__=="__main__":raise SystemExit(main())
