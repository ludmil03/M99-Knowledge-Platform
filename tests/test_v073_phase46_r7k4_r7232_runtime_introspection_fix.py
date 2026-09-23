from pathlib import Path
import ast,re
P=Path(__file__).resolve().parents[1]/"admin-platform/app/routers/r7k4_real_operator_publish.py"
def s(): return P.read_text(encoding="utf-8")
def test_marker(): assert "R7K.4 R7.2.3.2" in s()
def test_selector_preserved(): assert "<select name=item_id required>" in s()
def test_job_scope_preserved(): assert "ImportJobItem.import_job_id==int(job_id)" in s()
def test_price_field_still_present(): assert "price_override" in s()
def test_optional_preview_placeholder(): assert "незадължително за проверката" in s()
def test_practical_gate_text(): assert "Практически gate" in s()
def test_preview_no_publish_call():
    x=s(); b=x[x.index("def preview("):x.index('@router.post("/publish"')]
    assert "publish_palltex_controlled" not in b
def test_publish_call_preserved(): assert "publish_palltex_controlled" in s()
def test_superadmin_preserved(): assert "is_superuser" in s()
def test_operator_approval_preserved(): assert "operator_approved" in s()
def test_no_new_network():
    x=s().lower()
    assert all(v not in x for v in ("requests.post","requests.put","httpx.post","urllib.request"))
def test_ast(): ast.parse(s())
