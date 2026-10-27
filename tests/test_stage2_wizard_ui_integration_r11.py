from pathlib import Path
def test_existing_wizard_template_has_governed_channel_metadata():
    t=Path("admin-platform/app/templates/product_import_wizard/wizard.html").read_text(encoding="utf-8")
    assert "M99_CHANNEL_GOVERNANCE" in t
    assert "toplinka.com" not in t  # data-driven, never hardcoded into template
def test_controlled_publish_action_added():
    r=Path("admin-platform/app/routers/product_import_wizard.py").read_text(encoding="utf-8").lower()
    assert r.count('@router.post("/publish"') == 1
    assert "m99_stage5_authorization_plan" in r
    assert "operator_confirmed=confirmed" in r
