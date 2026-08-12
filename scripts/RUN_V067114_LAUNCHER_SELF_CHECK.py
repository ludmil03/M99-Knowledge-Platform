from pathlib import Path
from core.launcher_integrity_v067114 import scan_repo_launchers, all_ok
repo=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
results=scan_repo_launchers(repo)
print("M99 v0.6.7.1.4 - LAUNCHER SELF-CHECK")
for name,errors in sorted(results.items()):
    print(name,"=>","OK" if not errors else "ERROR: "+", ".join(errors))
ok=all_ok(results)
print("Launcher integrity:","PASS" if ok else "FAIL")
raise SystemExit(0 if ok else 2)
