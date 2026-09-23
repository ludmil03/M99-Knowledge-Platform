from pathlib import Path
import ast
R=Path(__file__).resolve().parents[1]
RO=R/"admin-platform/app/routers/r7k4_real_operator_publish.py"
TP=R/"admin-platform/app/templates/products/r7k4_real_operator_publish.html"
def text(p):return p.read_text(encoding="utf-8")
def test_route_is_real_operator_path():
 s=text(RO);assert '"/publish"' in s and "publish_palltex_controlled" in s
def test_rebuilds_canonical_preview_at_publish_time():
 s=text(RO);block=s[s.index("def publish("):];assert "build_canonical_payload_preview(job=job,item=item)" in block
def test_superadmin_and_operator_gate():
 s=text(RO);assert 'is_superuser' in s and 'operator_approved!="yes"' in s
def test_uses_existing_proven_r7k_publisher_not_new_http():
 s=text(RO);assert "publish_palltex_controlled" in s
 for bad in ("requests.post","requests.put","urllib.request","httpx."):assert bad not in s
def test_hidden_first_explained_to_operator():
 s=text(TP);assert "HIDDEN-FIRST" in s and "ПУБЛИКУВАЙ СКРИТО" in s
def test_no_exact_confirmation_typing():
 s=text(TP);assert "R7K_CONFIRMATION" not in s and "confirmation" not in s
def test_result_exposes_truth_readback():
 s=text(TP);assert "api_truth_verified" in s and "truth_summary" in s
def test_router_ast():
 ast.parse(text(RO))
