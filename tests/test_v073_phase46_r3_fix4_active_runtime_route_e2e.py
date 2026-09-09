from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/"admin-platform/app/main.py"
CANON=ROOT/"admin-platform/app/templates/add_products/r37_canonical_preview.html"
R3=ROOT/"admin-platform/app/routers/phase46_r3_content_intelligence.py"

def test_active_main_directly_includes_r3_router():
    s=MAIN.read_text(encoding="utf-8")
    assert "M99_PHASE46_R3_ACTIVE_RUNTIME_INCLUDE" in s
    assert "from app.routers.phase46_r3_content_intelligence import router as phase46_r3_content_router" in s
    assert "app.include_router(phase46_r3_content_router)" in s

def test_canonical_preview_carries_real_request_query_context():
    s=CANON.read_text(encoding="utf-8")
    assert 'request.query_params.get("source_uuid","")' in s
    assert 'request.query_params.get("product_url","")' in s

def test_r3_router_has_review_route():
    s=R3.read_text(encoding="utf-8")
    assert 'APIRouter(prefix="/content-intelligence"' in s
    assert '@router.get("/review"' in s
