from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/"scripts/run_uno_low_channel_preflight.py"
def test_runner_root_expression_is_correct():
    text=RUNNER.read_text(encoding="utf-8-sig")
    assert "ROOT=Path(__file__).resolve().parents[1]" in text
def test_script_path_bootstrap_can_import_integrations():
    code=f"""from pathlib import Path
import sys
runner=Path(r'{RUNNER}').resolve()
ROOT=runner.parents[1]
ADMIN=ROOT/'admin-platform'
for p in (ROOT,ADMIN):
    sys.path.insert(0,str(p))
from integrations.channel_preflight.uno_low_preflight import build_preflight,safety_gate
r=build_preflight(live_get=False)
assert safety_gate(r)['pass']
assert not r['write_performed']
print('PASS')
"""
    p=subprocess.run([sys.executable,"-c",code],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,p.stdout+p.stderr
    assert "PASS" in p.stdout
