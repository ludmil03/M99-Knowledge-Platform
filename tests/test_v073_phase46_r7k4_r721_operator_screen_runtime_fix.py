from pathlib import Path
import ast
P=Path(__file__).resolve().parents[1]/"admin-platform/app/routers/r7k4_real_operator_publish.py"
def s():return P.read_text(encoding="utf-8")
def test_standalone():assert "Jinja2Templates" not in s() and "TemplateResponse" not in s() and "<!doctype html>" in s()
def test_runtime_no_write():
 b=s()[s().index("def runtime_check"):s().index('@router.post("/preview"')];assert "publish_palltex_controlled" not in b
def test_preview_no_write():
 b=s()[s().index("def preview("):s().index('@router.post("/publish"')];assert "build_canonical_payload_preview" in b and "publish_palltex_controlled" not in b
def test_publish_proven():assert "publish_palltex_controlled" in s() and "build_canonical_payload_preview" in s()
def test_gates():assert "is_superuser" in s() and 'operator_approved!="yes"' in s()
def test_no_new_http():
 x=s().lower();assert all(y not in x for y in ("requests.post","requests.put","httpx.post","urllib.request"))
def test_ast():ast.parse(s())
