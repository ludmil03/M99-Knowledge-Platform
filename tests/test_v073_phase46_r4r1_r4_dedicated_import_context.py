from pathlib import Path
import ast

LEGACY=Path(__file__).resolve().parent/"test_v073_phase46_r4_fix4_all_languages_meta_short.py"

def test_legacy_fix4_test_derives_admin_from_file_location():
    s=LEGACY.read_text(encoding="utf-8")
    ast.parse(s)
    assert 'REPO_ROOT = Path(__file__).resolve().parents[1]' in s
    assert 'ADMIN = REPO_ROOT / "admin-platform"' in s
    assert 'sys.path.insert(0, str(ADMIN))' in s

def test_import_context_fix_does_not_weaken_quality_assertions():
    s=LEGACY.read_text(encoding="utf-8")
    assert 'content_bundle.v3' in s
    assert 'supplier_reference_role' in s
    assert 'manufacturer_reference_role' in s
    assert 'channel_reference_role' in s
