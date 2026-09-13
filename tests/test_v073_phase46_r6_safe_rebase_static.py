from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=(ROOT/"admin-platform/app/services/v073_phase46/content_manufacturer_intelligence.py").read_text(encoding="utf-8")

def test_accepted_r5_bundle_contract_is_preserved():
    assert '"meta_short_distinct_all_languages":True' in S
    assert '"status":"PREVIEW_READY"' in S
    assert '"meta_short_threshold":0.75' in S
    assert '"schema":"m99.phase46.r3.content_bundle.v3"' in S

def test_generic_fallback_is_additive():
    assert "def _fallback_meta_description" in S
    assert "after generic fallback" in S
    assert "female_tokens=" in S
    assert "male_tokens=" in S
