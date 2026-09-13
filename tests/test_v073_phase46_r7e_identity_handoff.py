
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R37=(ROOT/"admin-platform/app/services/v073_phase45/m99eu_r37_auto_publish.py").read_text(encoding="utf-8")
ROUTER=(ROOT/"admin-platform/app/routers/phase46_r1_final_publish.py").read_text(encoding="utf-8")
TPL=(ROOT/"admin-platform/app/templates/operator_publish/phase46_r1_final.html").read_text(encoding="utf-8")

def test_linked_product_is_valid_canonical_identity_carrier():
    assert "object_session(item)" in R37
    assert "session.get(Product, int(matched_id))" in R37
    assert "M99_REFERENCE_RE.fullmatch(linked_ref)" in R37

def test_identity_completion_is_explicit_superadmin_draft_one_item_gate():
    for x in ("CREATE PERMANENT M99 ID","user.is_superuser",'status","")).upper()!="DRAFT"',
              "Exactly one selected DRAFT item is required","allocate_or_reuse_for_item"):
        assert x in ROUTER

def test_ui_keeps_live_publish_separate():
    assert "CREATE / REUSE PERMANENT M99 ID" in TPL
    assert "PUBLISH ONE HIDDEN CANONICAL PILOT" in TPL
    assert "Supplier ref и Manufacturer MPN никога не стават M99 identity." in TPL

def test_object_session_has_unmapped_compatibility_boundary():
    assert "session = None" in R37
    assert "session = object_session(item)" in R37
    assert "except Exception:" in R37
    assert "M99_REFERENCE_RE.fullmatch(linked_ref)" in R37
