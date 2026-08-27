from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
START=ROOT/"admin-platform/app/templates/supplier_browser/manufacturer_start.html"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"

def test_supplier_template_has_single_draft_form_and_no_nested_form():
    raw=TEMPLATE.read_text(encoding="utf-8")
    assert raw.count('<form method="post" action="/supplier-browser/create-job"') == 1
    assert '<form method="post" action="/supplier-browser/manufacturer-review"' not in raw
    assert "/supplier-browser/manufacturer-start?" in raw

def test_draft_button_is_inside_create_job_form_source_order():
    raw=TEMPLATE.read_text(encoding="utf-8")
    start=raw.index('<form method="post" action="/supplier-browser/create-job"')
    button=raw.index('id="create-draft-btn"')
    end=raw.index("</form>", button)
    assert start < button < end

def test_manufacturer_form_is_separate_page():
    raw=START.read_text(encoding="utf-8")
    assert '<form method="post" action="/supplier-browser/manufacturer-review">' in raw
    assert 'name="manufacturer_url"' in raw

def test_router_has_separate_manufacturer_start_route():
    raw=ROUTER.read_text(encoding="utf-8")
    assert '@router.get("/manufacturer-start")' in raw
    assert '@router.post("/manufacturer-review")' in raw

def test_selection_and_draft_controls_preserved():
    raw=TEMPLATE.read_text(encoding="utf-8")
    assert 'class="product-check"' in raw
    assert 'id="selected-count"' in raw
    assert 'id="create-draft-btn"' in raw
    assert "checked.length === 0" in raw or "checked.length===0" in raw
