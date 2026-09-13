from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parents[1]
def test_all_r7f_reads_are_explicit_utf8():
 for p in (ROOT/"tests").glob("test_v073_phase46_r7f*.py"):
  tree=ast.parse(p.read_text(encoding="utf-8"))
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="read_text":assert "encoding" in {k.arg for k in n.keywords if k.arg}
def test_no_imported_test_named_production_helper():
 for p in (ROOT/"tests").glob("test_v073_phase46_r7f*.py"):
  tree=ast.parse(p.read_text(encoding="utf-8"))
  for n in ast.walk(tree):
   if isinstance(n,ast.ImportFrom):
    for a in n.names:assert not (a.asname or a.name).startswith("test_")
