from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_stage5_governed_publish_transition():
    r=(ROOT/"admin-platform/app/routers/product_import_wizard.py").read_bytes().decode("utf-8-sig")
    t=(ROOT/"admin-platform/app/templates/product_import_wizard/wizard.html").read_bytes().decode("utf-8-sig")
    assert r.count('@router.post("/publish"') == 1
    assert "m99_stage5_authorization_plan" in r
    assert "operator_confirmed=confirmed" in r
    assert 'form.get("payload_xml")' not in r[r.index('@router.post("/publish"'):]
    assert t.count('action="/operator/add-products/publish"') == 1
    assert 'name="operator_confirmed"' in t
