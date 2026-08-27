from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/"admin-platform/app/routers/canonical_preview_runtime.py"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"
GUARD=ROOT/"admin-platform/app/services/source_role_guard.py"
INDEX=ROOT/"admin-platform/app/templates/supplier_browser/index.html"

def load_guard():
    spec=importlib.util.spec_from_file_location("source_role_guard",GUARD)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_dedicated_preview_router_is_single_owner():
    r=RUNTIME.read_text(encoding="utf-8")
    s=ROUTER.read_text(encoding="utf-8")
    assert '@router.get("/canonical-preview")' in r
    assert '@router.get("/canonical-preview")' not in s

def test_supplier_and_manufacturer_hosts_must_differ():
    g=load_guard()
    assert g.validate_manufacturer_source("https://stenso.net","https://stenso.net/product/x")[0] is False
    assert g.validate_manufacturer_source("https://stenso.net","https://pandasafety.com/product/marine/")== (True,"PASS")

def test_stable_supplier_flow_markers_preserved():
    s=ROUTER.read_text(encoding="utf-8")
    t=INDEX.read_text(encoding="utf-8")
    assert '@router.get("/hydrate-product")' in s
    assert '@router.post("/create-job")' in s
    assert 'runHydrationQueue(4)' in t
    assert t.count('<form method="post" action="/supplier-browser/create-job"') == 1
    assert '/supplier-browser/canonical-preview?' in t

def test_manufacturer_review_has_role_guard():
    s=ROUTER.read_text(encoding="utf-8")
    assert "validate_manufacturer_source" in s
    assert "MANUFACTURER_MUST_DIFFER_FROM_SUPPLIER" not in s  # reason comes from guard service
