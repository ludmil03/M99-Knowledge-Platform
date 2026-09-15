from pathlib import Path
import subprocess, os, sys, shutil, hashlib

REPO = Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
VERSION = "R1.2 BOOTSTRAP TEST ENV FIX"
EXPECTED_PARENT = "2be8ca39e927e65d02c4e5696fd05b185cf31b6e"
RUNTIME_RULE = "var/phase46_draft_enrichment/"
TEST_RUNNER_RULE = ".m99-test-runner/"
INSTALL_FILES = [".gitignore", "tools/safe_git_checkpoint_engine.py", "tests/test_safe_git_checkpoint_engine.py"]

def classify(path):
    p=path.replace("\\","/").lower().lstrip("/")
    if p.startswith("var/") or p.startswith(".env") or "/.env" in p or "__pycache__" in p or ".venv" in p or p.endswith((".db",".sqlite",".sqlite3",".log",".zip",".rar",".7z",".pyc")): return "DENY"
    if p==".gitignore" or p.startswith(("tools/","tests/","admin-platform/","core/","integrations/","docs/","governance/","config/")) or p.startswith(("readme_m99_","m99_master_machine_memory_","m99_all_decisions_bg_","decision_registry","project_state","m99_current_context")): return "ALLOW"
    return "REVIEW"

def git_exe():
    p=shutil.which("git")
    if p: return p
    hits=sorted((Path.home()/"AppData/Local/GitHubDesktop").glob("app-*/resources/app/git/cmd/git.exe"),reverse=True)
    if not hits: raise RuntimeError("Git executable not found")
    return str(hits[0])

def run(g,*args):
    env=os.environ.copy(); env.update(GIT_PAGER="cat",PAGER="cat",GIT_TERMINAL_PROMPT="0")
    p=subprocess.run([g,*args],cwd=REPO,env=env,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if p.stdout: print(p.stdout,end="")
    if p.returncode: raise RuntimeError("Git failed: "+" ".join(args))
    return p.stdout.strip()

def pytest_python():
    # First prefer an existing project/system interpreter with pytest.
    candidates=[Path(sys.executable), REPO/".venv/Scripts/python.exe", REPO/"venv/Scripts/python.exe", REPO/"admin-platform/.venv/Scripts/python.exe"]
    for base in [Path.home()/"AppData/Local/Programs/Python", Path.home()/"AppData/Local/Python"]:
        if base.exists(): candidates.extend(sorted(base.glob("**/python.exe")))
    seen=set()
    for candidate in candidates:
        py=str(candidate)
        if py.lower() in seen or not Path(py).exists(): continue
        seen.add(py.lower())
        probe=subprocess.run([py,"-c","import pytest; print(pytest.__version__)"],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if probe.returncode==0:
            print("[PASS] existing pytest interpreter:",py,probe.stdout.strip()); return py

    # Controlled fallback: isolated local test environment under .m99-test-runner.
    # It is ignored by Git and never changes project dependency files.
    bootstrap=REPO/".m99-test-runner"
    py=str(Path(sys.executable))
    if not bootstrap.exists():
        print("[INFO] Creating isolated test runner; project dependencies are not modified")
        subprocess.run([py,"-m","venv",str(bootstrap)],cwd=REPO,check=True)
    bpython=bootstrap/"Scripts/python.exe"
    if not bpython.exists(): raise RuntimeError("Isolated test runner Python was not created")
    probe=subprocess.run([str(bpython),"-c","import pytest"],cwd=REPO)
    if probe.returncode!=0:
        subprocess.run([str(bpython),"-m","pip","install","--disable-pip-version-check","pytest"],cwd=REPO,check=True)
    probe=subprocess.run([str(bpython),"-c","import pytest; print(pytest.__version__)"],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if probe.returncode!=0: raise RuntimeError("Isolated pytest bootstrap failed")
    print("[PASS] isolated pytest interpreter:",str(bpython),probe.stdout.strip()); return str(bpython)

def main():
    g=git_exe()
    if run(g,"branch","--show-current")!="main": raise RuntimeError("Expected main branch")
    head=run(g,"rev-parse","HEAD"); run(g,"fetch","origin","main"); remote=run(g,"rev-parse","origin/main")
    if head!=EXPECTED_PARENT or remote!=EXPECTED_PARENT: raise RuntimeError("Baseline moved; stop safely")
    prestaged=[x for x in run(g,"diff","--cached","--name-only").splitlines() if x]
    unexpected=[x for x in prestaged if x not in INSTALL_FILES]
    if unexpected: raise RuntimeError("Unexpected pre-existing staged files: "+repr(unexpected))
    if prestaged:
        print("[INFO] Recovering exact staged set from failed R1 attempt:",prestaged)
        run(g,"restore","--staged","--",*prestaged)
    gi=REPO/".gitignore"; old=gi.read_text(encoding="utf-8") if gi.exists() else ""
    rules=[x.strip() for x in old.splitlines()]
    additions=[]
    if RUNTIME_RULE not in rules: additions.append(RUNTIME_RULE)
    if TEST_RUNNER_RULE not in rules: additions.append(TEST_RUNNER_RULE)
    if additions:
        sep="" if not old or old.endswith("\n") else "\n"
        gi.write_text(old+sep+"\n# M99 local-only runtime/test environments\n"+"\n".join(additions)+"\n",encoding="utf-8",newline="\n")
    (REPO/"tools").mkdir(exist_ok=True); shutil.copy2(__file__,REPO/"tools/safe_git_checkpoint_engine.py")
    test=(REPO/"tests/test_safe_git_checkpoint_engine.py")
    test.write_text('from tools.safe_git_checkpoint_engine import classify\n\ndef test_runtime(): assert classify("var/phase46_draft_enrichment/job-27.json")=="DENY"\ndef test_env(): assert classify(".env")=="DENY"\ndef test_source(): assert classify("admin-platform/app/main.py")=="ALLOW"\ndef test_unknown(): assert classify("mystery.bin")=="REVIEW"\n',encoding="utf-8",newline="\n")
    run(g,"add","--",*INSTALL_FILES)
    staged=[x for x in run(g,"diff","--cached","--name-only").splitlines() if x]
    if set(staged)!=set(INSTALL_FILES) or len(staged)!=len(INSTALL_FILES): raise RuntimeError("Unexpected staged set: "+repr(staged))
    run(g,"diff","--cached","--check")
    py=pytest_python()
    subprocess.run([py,"-m","pytest","-q",str(REPO/"tests"),str(REPO/"admin-platform/tests")],cwd=REPO,check=True)
    print("[PASS] Maintained regression")
    for f in staged: print(hashlib.sha256((REPO/f).read_bytes()).hexdigest(),f)
    if input("Type SAVE M99 CHECKPOINT to commit and push: ").strip()!="SAVE M99 CHECKPOINT": raise RuntimeError("Not approved")
    run(g,"fetch","origin","main")
    if run(g,"rev-parse","HEAD")!=EXPECTED_PARENT or run(g,"rev-parse","origin/main")!=EXPECTED_PARENT: raise RuntimeError("Remote parent moved")
    run(g,"commit","-m","feat: add permanent Safe Git Checkpoint Engine")
    new=run(g,"rev-parse","HEAD"); run(g,"push","origin","main"); run(g,"fetch","origin","main")
    if run(g,"rev-parse","HEAD")!=new or run(g,"rev-parse","origin/main")!=new: raise RuntimeError("Post-push verification failed")
    print("[PASS] HEAD == origin/main ==",new)
    print("[PASS] GitHub Desktop runtime files are ignored; files remain local")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("\n[STOP]",e); print("No force/reset-hard/clean/rebase used."); sys.exit(1)
