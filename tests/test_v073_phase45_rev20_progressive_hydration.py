from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
SERVICE=ROOT/"admin-platform/app/services/supplier_browser.py"
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"

def test_category_inspection_no_longer_eager_hydrates_all_products():
    s=SERVICE.read_text(encoding="utf-8")
    assert '"hydration_status": "WAITING" if is_stenso else "NOT_IMPLEMENTED"' in s
    assert 'result["products"] = hydrate_stenso_products(links' not in s

def test_runtime_hydration_endpoint_exists():
    r=ROUTER.read_text(encoding="utf-8")
    assert '@router.get("/hydrate-product")' in r
    assert "hydrate_stenso_product(url, supplier.base_url, use_cache=True)" in r

def test_template_progressively_hydrates_and_disables_before_pass():
    t=TEMPLATE.read_text(encoding="utf-8")
    assert 'data-url="{{p.url}}"' in t
    assert 'class="product-check"' in t
    assert 'value="{{p.url}}" disabled' in t
    assert "runHydrationQueue(4)" in t
    assert "/supplier-browser/hydrate-product?" in t
    assert "Hydrated: 0 /" in t

def test_runtime_cache_contract_present():
    s=SERVICE.read_text(encoding="utf-8")
    for marker in ("_CACHE_TTL_SECONDS = 600","_cache_get","_cache_put",'cache_status'):
        assert marker in s

def test_draft_reverification_still_present():
    r=ROUTER.read_text(encoding="utf-8")
    assert "hydrate_stenso_product(selected_url" in r
