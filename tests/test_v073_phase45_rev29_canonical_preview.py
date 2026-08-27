from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
SERVICE=ROOT/"admin-platform/app/services/canonical_preview.py"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"
INDEX=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
PREVIEW=ROOT/"admin-platform/app/templates/supplier_browser/canonical_preview.html"


def load_service():
    spec=importlib.util.spec_from_file_location("canonical_preview_rev29",SERVICE)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_preview_is_read_only_and_not_publishable():
    m=load_service()
    product={
        "url":"https://stenso.net/produkt/test",
        "title":"Работен полугащеризон TEST 02002744",
        "supplier_reference":"02002744",
        "price_text":"29.6 EUR",
        "availability_text":"IN_STOCK",
        "description":"Тестово описание.",
        "images":["a.jpg","b.jpg"],
        "specifications":[{"name":"Материал","value":"65% polyester"}],
        "variants":[
            {"type":"SIZE","value":"44","availability":"IN_STOCK"},
            {"type":"SIZE","value":"46","availability":"OUT_OF_STOCK"},
        ],
    }
    p=m.prepare_canonical_preview(product)
    assert p["status"]=="PREVIEW_READY"
    assert p["canonical_identity"]["name"]=="Работен полугащеризон TEST"
    assert p["publishable"] is False
    assert p["quality_gate"]["website_write_allowed"] is False
    assert p["m99_draft"]["translation_status"]=="NOT_GENERATED"


def test_router_adds_preview_without_touching_working_routes():
    r=ROUTER.read_text(encoding="utf-8")
    runtime=(ROOT/"admin-platform/app/routers/canonical_preview_runtime.py").read_text(encoding="utf-8")
    assert '@router.get("/canonical-preview")' not in r
    assert '@router.get("/canonical-preview")' in runtime
    assert '@router.get("/hydrate-product")' in r
    assert '@router.post("/create-job")' in r
    assert '@router.get("/manufacturer-start")' in r
    assert '@router.post("/manufacturer-review")' in r


def test_supplier_browser_keeps_proven_runtime_contract():
    t=INDEX.read_text(encoding="utf-8")
    assert 'action="/supplier-browser/inspect"' in t
    assert t.count('<form method="post" action="/supplier-browser/create-job"') == 1
    assert "runHydrationQueue(4)" in t
    assert 'id="create-draft-btn"' in t
    assert 'class="product-check"' in t
    assert "/supplier-browser/canonical-preview?" in t


def test_preview_template_has_explicit_write_block():
    p=PREVIEW.read_text(encoding="utf-8")
    assert "PREVIEW ONLY" in p
    assert "Website write allowed" in p
    assert "Translation status" in p
    assert "Supplier Evidence" in p
    assert "M99 Canonical Draft" in p
