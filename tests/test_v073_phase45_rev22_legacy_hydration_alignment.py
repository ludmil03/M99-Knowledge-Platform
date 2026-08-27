from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REV12=ROOT/"tests/test_v073_phase45_rev12_stenso_hydration.py"
SERVICE=ROOT/"admin-platform/app/services/supplier_browser.py"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"

def test_legacy_rev12_test_no_longer_requires_eager_category_hydration():
    t=REV12.read_text(encoding="utf-8")
    assert 'assert result["hydration_pass"] == 1' not in t
    assert 'result["products"][0]["hydration_status"] == "WAITING"' in t
    assert 'hydrate_stenso_product(' in t

def test_progressive_service_contract_remains_active():
    s=SERVICE.read_text(encoding="utf-8")
    assert '"hydration_status": "WAITING" if is_stenso else "NOT_IMPLEMENTED"' in s
    assert 'result["products"] = hydrate_stenso_products(links' not in s
    assert "_CACHE_TTL_SECONDS = 600" in s

def test_runtime_endpoint_and_gui_queue_remain_active():
    r=ROUTER.read_text(encoding="utf-8")
    t=TEMPLATE.read_text(encoding="utf-8")
    assert '@router.get("/hydrate-product")' in r
    assert "/supplier-browser/hydrate-product?" in t
    assert "runHydrationQueue(4)" in t
    assert "cb.disabled=!ok;" in t

def test_draft_and_manufacturer_separation_still_present():
    r=ROUTER.read_text(encoding="utf-8")
    t=TEMPLATE.read_text(encoding="utf-8")
    assert '@router.post("/create-job")' in r
    assert '@router.get("/manufacturer-start")' in r
    assert '<form method="post" action="/supplier-browser/manufacturer-review"' not in t
