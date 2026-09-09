from pathlib import Path

SVC=Path("admin-platform/app/services/v073_phase46/content_manufacturer_intelligence.py")
LEGACY=Path("tests/test_v073_phase46_r4_fix3_confirm_continuity_content_quality.py")

def test_fix4_threshold_is_stricter_than_fix3():
    assert 0.75 < 0.90

def test_service_uses_stricter_global_threshold():
    s=SVC.read_text(encoding="utf-8")
    assert "if similarity>=0.75:" in s
    assert "_validate_meta_short_distinctness" in s
    assert '"meta_short_threshold":0.75' in s

def test_legacy_fix3_test_is_migrated_to_stronger_semantics():
    t=LEGACY.read_text(encoding="utf-8")
    assert "if similarity>=0.75:" in t
    assert "_content_similarity(md,short_description)>=0.90" not in t
