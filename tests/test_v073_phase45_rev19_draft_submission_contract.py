from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
START=ROOT/"admin-platform/app/templates/supplier_browser/manufacturer_start.html"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"

def test_draft_form_contract_is_single_and_submit_capable():
    raw=TEMPLATE.read_text(encoding="utf-8")
    assert raw.count('<form method="post" action="/supplier-browser/create-job"') == 1
    assert '<form method="post" action="/supplier-browser/manufacturer-review"' not in raw
    assert 'id="create-draft-btn"' in raw
    assert 'name="selected_url"' in raw
    assert 'name="target"' in raw

def test_manufacturer_form_lives_on_separate_page():
    raw=START.read_text(encoding="utf-8")
    assert '<form method="post" action="/supplier-browser/manufacturer-review">' in raw
    assert 'name="manufacturer_url"' in raw
    assert 'name="supplier_url"' in raw

def test_router_exposes_separated_routes():
    raw=ROUTER.read_text(encoding="utf-8")
    assert '@router.get("/manufacturer-start")' in raw
    assert '@router.post("/manufacturer-review")' in raw
    assert '@router.post("/create-job")' in raw

def test_button_enable_logic_tracks_checked_products():
    raw=TEMPLATE.read_text(encoding="utf-8")
    assert "checked.length===0" in raw or "checked.length === 0" in raw
    assert "updateSelectedCount()" in raw
