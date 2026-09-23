from pathlib import Path
import tempfile,subprocess,os
from tools.r7k4_existing_importer_recovery import main,find_git
def g(p,*a):subprocess.run([find_git(),*a],cwd=p,check=True,stdout=subprocess.DEVNULL)
def test_git_resolved(): assert Path(find_git()).exists()
def test_recovers_history():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);g(p,"init");g(p,"config","user.email","x@x");g(p,"config","user.name","x");(p/"legacy_importer.py").write_text("SOURCE='stenso.net'\n# Exact image candidates\n");g(p,"add",".");g(p,"commit","-m","legacy importer");(p/"legacy_importer.py").write_text("SOURCE='bultex99.com'\n");g(p,"add",".");g(p,"commit","-m","replace supplier source")
  r=main(p);assert r["status"]=="RECOVERY_EVIDENCE_FOUND";assert r["writes_performed"] is False
def test_fail_closed_when_absent():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);g(p,"init");g(p,"config","user.email","x@x");g(p,"config","user.name","x");(p/"x.py").write_text("print('x')");g(p,"add",".");g(p,"commit","-m","base");assert main(p)["status"]=="LEGACY_IMPORTER_NOT_FOUND"
def test_contract():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);g(p,"init");g(p,"config","user.email","x@x");g(p,"config","user.name","x");(p/"bultex_supplier.py").write_text("supplier='bultex99'\nwebp=True");g(p,"add",".");g(p,"commit","-m","supplier");x=main(p)["integration_target"];assert "image acquisition" in x["preserve"] and x["live_write"] is False
