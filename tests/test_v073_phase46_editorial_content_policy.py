from pathlib import Path
import ast
ADMIN=Path(__file__).resolve().parents[1]/"admin-platform"
POLICY=ADMIN/"app/services/v073_phase46/editorial_content_policy.py"
BRIDGE=ADMIN/"app/services/v073_phase46/r4_r1_canonical_payload_bridge.py"
TPL=ADMIN/"app/templates/operator_publish/phase46_r1_final.html"

def test_policy_machine_readable_and_compiles():
    s=POLICY.read_text(encoding="utf-8"); ast.parse(s)
    assert 'EDITORIAL_POLICY_ID = "CONTENT-EDITORIAL-001"' in s
    assert '"detector_evasion_objective": False' in s
    assert '"knowledge_first": True' in s
    assert '"ai_native_not_ai_invented": True' in s

def test_required_quality_gates():
    s=POLICY.read_text(encoding="utf-8")
    for x in ("FACTUAL_EVIDENCE_COVERAGE","SEO_SEARCH_INTENT_FIT","BOILERPLATE_SIMILARITY",
              "CROSS_PRODUCT_SIMILARITY","LANGUAGE_NATURALNESS","META_SHORT_DISTINCTNESS","CLAIM_SUPPORT"):
        assert x in s

def test_heading_hierarchy_is_semantic_not_forced():
    assert "H2_H5_ONLY_WHEN_SEMANTICALLY_NEEDED" in POLICY.read_text(encoding="utf-8")

def test_preview_surfaces_policy():
    assert "policy_preview" in BRIDGE.read_text(encoding="utf-8")
    assert "Editorial / SEO policy" in TPL.read_text(encoding="utf-8")
