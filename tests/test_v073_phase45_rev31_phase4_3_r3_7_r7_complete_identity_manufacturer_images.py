from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "admin-platform/app/services/v073_phase45/r37_identity_persistence_reconcile.py"
PATCH = ROOT / "scripts/r37r7_patch_runtime.py"

def test_identity_reconcile_is_metadata_driven_without_common_base_assumption():
    text = RECON.read_text(encoding="utf-8")
    assert 'IDENTITY_PREFIX = "m99_v073_identity_"' in text
    assert "_discover_identity_tables" in text
    assert 'getattr(obj, "__table__", None)' in text
    assert 'getattr(obj, "metadata", None)' in text
    assert "table.create(" in text
    assert "_backup(db)" in text

def test_no_one_table_guessing():
    text = RECON.read_text(encoding="utf-8")
    assert "m99_v073_identity_resolutions" not in text
    assert "m99_v073_identity_external_mappings" not in text

def test_manufacturer_operator_evidence_contract():
    text = PATCH.read_text(encoding="utf-8")
    assert 'manufacturer_name: str = Form("")' in text
    assert "confirmed_manufacturer" in text
    assert "approved Manufacturer" in text

def test_variant_images_preserved():
    text = PATCH.read_text(encoding="utf-8")
    assert "variant_image_evidence" in text
    assert 'variant.get("image_url")' in text
    assert "all_images" in text
