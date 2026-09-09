from pathlib import Path
import ast

SVC=Path("admin-platform/app/services/v073_phase46/content_manufacturer_intelligence.py")
ROUTER=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py")

def test_confirm_persistence_never_reenters_draft_context_with_blank_source_identity():
    s=SVC.read_text(encoding="utf-8")
    assert 'draft_context(db,job_id,"","")' not in s
    assert "supplier_evidence:dict|None=None" in s
    assert "supplier=dict(supplier_evidence or {})" in s
    r=ROUTER.read_text(encoding="utf-8")
    assert "supplier_evidence=s" in r

def test_runtime_failure_root_cause_is_closed_without_weakening_source_governance():
    s=SVC.read_text(encoding="utf-8")
    # Exact manufacturer fetch still enforces approved-domain/same-site semantics.
    assert 'if not _same(site,manufacturer_page_url):raise ValueError("Selected page is outside approved official domain.")' in s
    assert 'if not c.exact_reference:raise ValueError("Selected manufacturer page does not contain the exact reference.")' in s
    # R4 durable fallback remains explicit.
    assert 'result["persistence_upgrade"]="R4_DURABLE_DRAFT_SIDECAR"' in s

def test_meta_short_are_not_generated_from_the_same_value_anymore():
    s=SVC.read_text(encoding="utf-8")
    assert 'md=summary if len(summary)<=160' not in s
    assert "md=_meta_description_for(p,lang,summary)" in s
    assert "meta_short_similarity=_content_similarity(md,summary)" in s

def test_meta_short_quality_gate_is_multilingual_and_hard_fails():
    s=SVC.read_text(encoding="utf-8")
    assert "if similarity>=0.75:" in s
    assert "_validate_meta_short_distinctness" in s
    assert '"meta_short_threshold":0.75' in s
    assert "Meta Description / Short Description separation gate failed" in s
    assert '"meta_short_distinct_all_languages":True' in s
    for lang in ("BG","EN","RU","RO","GR"):
        assert f'lang=="{lang}"' in s or f'"{lang}"' in s

def test_no_syntax_regression():
    ast.parse(SVC.read_text(encoding="utf-8"))
    ast.parse(ROUTER.read_text(encoding="utf-8"))
