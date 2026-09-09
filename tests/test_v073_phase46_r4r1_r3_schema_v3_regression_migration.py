from pathlib import Path

ADMIN=Path(__file__).resolve().parents[1]/"admin-platform"
CONTENT=ADMIN/"app/services/v073_phase46/content_manufacturer_intelligence.py"
LEGACY=Path(__file__).resolve().parent/"test_v073_phase46_r4_fix4_all_languages_meta_short.py"

def test_v3_is_current_content_contract():
    s=CONTENT.read_text(encoding="utf-8")
    assert 'content_bundle.v3' in s
    assert '"supplier_reference_role":"SUPPLIER_MAPPING_ONLY"' in s
    assert '"manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY"' in s
    assert '"channel_reference_role":"PERMANENT_M99_REFERENCE"' in s

def test_legacy_fix4_test_is_migrated_not_weakened():
    s=LEGACY.read_text(encoding="utf-8")
    assert 'content_bundle.v2' not in s
    assert 'content_bundle.v3' in s
    assert 'supplier_reference_role' in s
    assert 'manufacturer_reference_role' in s
    assert 'channel_reference_role' in s

def test_meta_short_quality_gate_remains_strict():
    s=CONTENT.read_text(encoding="utf-8")
    assert '"meta_short_threshold":0.75' in s
    assert "_validate_meta_short_distinctness" in s
