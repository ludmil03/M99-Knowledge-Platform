from pathlib import Path
import ast

ROUTER=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py")

def test_review_context_accepts_publish_review_url_and_exports_it():
    s=ROUTER.read_text(encoding="utf-8")
    assert 'publish_review_url=""' in s
    assert "publish_review_url=publish_review_url" in s

def test_confirm_success_publish_review_keyword_matches_context_signature():
    tree=ast.parse(ROUTER.read_text(encoding="utf-8"))
    review=None
    confirm=None
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and n.name=="_review_context": review=n
        if isinstance(n,ast.FunctionDef) and n.name=="confirm": confirm=n
    assert review is not None and confirm is not None
    accepted={a.arg for a in review.args.args+review.args.kwonlyargs}
    calls=[]
    for n in ast.walk(confirm):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_review_context":
            calls.append({kw.arg for kw in n.keywords if kw.arg})
    assert calls
    for kws in calls:
        assert kws.issubset(accepted), f"unsupported _review_context kwargs: {sorted(kws-accepted)}"

def test_confirm_success_has_final_safe_render_boundary():
    s=ROUTER.read_text(encoding="utf-8")
    assert "Confirmed data was produced, but the review UI failed safely:" in s
    assert 'publish_review_url=""' in s

def test_dynamic_publish_handoff_is_preserved():
    s=ROUTER.read_text(encoding="utf-8")
    assert '@router.get("/publish-handoff", name="phase46_r4_publish_handoff")' in s
    assert 'endswith("/r1-final")' in s

def test_router_compiles():
    ast.parse(ROUTER.read_text(encoding="utf-8"))
