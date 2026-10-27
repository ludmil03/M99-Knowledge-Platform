from pathlib import Path
R=Path(__file__).resolve().parents[1]
RO=R/"admin-platform/app/routers/product_import_wizard.py"
TP=R/"admin-platform/app/templates/product_import_wizard/wizard.html"
def test_single_authoritative_wizard_router():
    s=RO.read_text(encoding="utf-8-sig")
    assert 'prefix="/operator/add-products"' in s
    assert "context.update(extra)" in s
    assert s.count('@router.post("/publish"') == 1
    assert "m99_stage5_authorization_plan" in s
def test_router_not_modified_for_r8():
    assert "qa_view" not in RO.read_text(encoding="utf-8-sig")
def test_display_only_qa_block_once():
    s=TP.read_text(encoding="utf-8")
    assert s.count('id="m99-stage3-qa"') == 1
    assert "qa_view is defined and qa_view" in s
    assert "READY_FOR_TARGETS" in s and "BLOCKED" in s
    assert "Publish:</strong> ИЗКЛЮЧЕНО" in s
def test_controlled_publish_form_added():
    s=TP.read_text(encoding="utf-8").lower()
    assert s.count('action="/operator/add-products/publish"') == 1
    assert 'name="operator_confirmed"' in s
