from pathlib import Path
import ast
P=Path(__file__).resolve().parents[1]/"admin-platform/app/routers/r7k4_real_operator_publish.py"
def s():return P.read_text(encoding="utf-8")
def test_marker():assert any(v in s() for v in ("R7K.4 R7.2.2","R7K.4 R7.2.3.2"))
def test_job_query():assert "ImportJobItem.import_job_id==int(job_id)" in s()
def test_selector_identity():assert "m99_reference" in s() and "supplier_reference" in s()
def test_selector():assert "<select name=item_id required>" in s()
def test_preview_no_write():
 x=s();b=x[x.index("def preview("):x.index('@router.post("/publish"')];assert "publish_palltex_controlled" not in b
def test_proven_publish():assert "publish_palltex_controlled" in s()
def test_gates():assert "is_superuser" in s() and 'operator_approved!="yes"' in s()
def test_ast():ast.parse(s())
