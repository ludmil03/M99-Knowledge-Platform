from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/"admin-platform/app/routers/canonical_preview_runtime.py"
MAIN=ROOT/"admin-platform/app/main.py"

def test_dedicated_runtime_router_exists():
    t=RUNTIME.read_text(encoding="utf-8")
    assert 'router = APIRouter(prefix="/supplier-browser")' in t
    assert '@router.get("/canonical-preview")' in t
    assert "prepare_canonical_preview" in t

def test_main_explicitly_registers_runtime_router():
    t=MAIN.read_text(encoding="utf-8")
    assert "canonical_preview_runtime" in t
    assert "app.include_router(canonical_preview_runtime.router)" in t

def test_route_is_read_only_by_contract():
    t=RUNTIME.read_text(encoding="utf-8")
    assert ("READ/VERIFY ONLY" in t) or ("READ / VERIFY ONLY" in t)
    assert "create_draft_job" not in t
