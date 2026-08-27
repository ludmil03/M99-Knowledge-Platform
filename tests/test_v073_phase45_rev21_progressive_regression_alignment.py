from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
SERVICE=ROOT/"admin-platform/app/services/supplier_browser.py"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"

def test_progressive_runtime_selection_gate():
    t=TEMPLATE.read_text(encoding="utf-8")
    assert 'value="{{p.url}}" disabled' in t
    assert "const ok=p.hydration_status==='PASS';" in t
    assert "cb.disabled=!ok;" in t
    assert "runHydrationQueue(4)" in t
    assert "/supplier-browser/hydrate-product?" in t

def test_zero_selected_and_draft_disabled_contract():
    t=TEMPLATE.read_text(encoding="utf-8")
    assert "Избрани: 0" in t
    assert 'id="create-draft-btn"' in t
    assert "checked.length===0" in t or "checked.length === 0" in t

def test_category_render_is_not_eager_hydration():
    s=SERVICE.read_text(encoding="utf-8")
    assert '"hydration_status": "WAITING" if is_stenso else "NOT_IMPLEMENTED"' in s
    assert 'result["products"] = hydrate_stenso_products(links' not in s

def test_cache_and_runtime_endpoint_still_present():
    s=SERVICE.read_text(encoding="utf-8")
    r=ROUTER.read_text(encoding="utf-8")
    assert "_CACHE_TTL_SECONDS = 600" in s
    assert "_cache_get" in s
    assert "_cache_put" in s
    assert '@router.get("/hydrate-product")' in r

def test_draft_supplier_reverification_still_present():
    r=ROUTER.read_text(encoding="utf-8")
    assert "hydrate_stenso_product(selected_url" in r
