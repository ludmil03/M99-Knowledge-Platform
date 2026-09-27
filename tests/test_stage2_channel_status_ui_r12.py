from pathlib import Path
from app.services.product_import_wizard import available_targets

def test_governed_targets_have_expected_toplinka_state():
    t={x.key:x for x in available_targets()}["toplinka.com"]
    assert t.authorized is True and t.ready is False

def test_existing_template_contains_status_ui_once():
    s=Path("admin-platform/app/templates/product_import_wizard/wizard.html").read_text(encoding="utf8")
    assert s.count("M99_STAGE2_R12_CHANNEL_STATUS_BEGIN")==1
    assert "Статус на каналите" in s
    assert "РАЗРЕШЕН / ОЧАКВА ПРОВЕРКА" in s

def test_ui_does_not_add_publish_form_or_secret():
    s=Path("admin-platform/app/templates/product_import_wizard/wizard.html").read_text(encoding="utf8").lower()
    block=s.split("m99_stage2_r12_channel_status_begin",1)[1].split("m99_stage2_r12_channel_status_end",1)[0]
    assert "<form" not in block and "api_key" not in block and "password" not in block
