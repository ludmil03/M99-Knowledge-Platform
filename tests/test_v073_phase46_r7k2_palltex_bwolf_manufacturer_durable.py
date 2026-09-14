
from types import SimpleNamespace
from pathlib import Path

def test_r7k2_router_contains_exact_super_admin_confirmation():
    p=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    assert 'CONFIRM PALLTEX IS BWOLF MANUFACTURER' in p
    assert 'user.is_superuser' in p
    assert 'roles_are_distinct' in p
    assert 'OPERATOR_CONFIRMED_EXACT' in p
    assert 'VERIFIED_EXACT_REFERENCE' in p

def test_r7k2_is_bounded_to_palltex_and_bwolf():
    p=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    assert '{"palltex.bg","www.palltex.bg"}' in p
    assert 'brand.casefold()!="bwolf"' in p
    assert 'R7K.2 applies only' in p

def test_r7k2_does_not_change_global_supplier_manufacturer_model():
    p=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    assert '"supplier_role":"SUPPLIER"' in p
    assert '"manufacturer_role":"MANUFACTURER_BRAND_OWNER"' in p
    assert '"roles_are_distinct":True' in p

def test_r7k2_uses_existing_durable_persistence_path():
    p=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    section=p[p.index('def confirm_palltex_bwolf_brand_owner'):]
    assert 'persist_confirmed_enrichment(' in section
    assert 'publish_palltex' not in section.split('@router.get("/publish-handoff"')[0]

def test_r7k2_template_exposes_controlled_action_only():
    p=Path("admin-platform/app/templates/content_intelligence/review.html").read_text(encoding="utf-8")
    assert 'R7K.2 — Palltex ↔ BWOLF controlled Manufacturer resolution' in p
    assert '/content-intelligence/confirm-palltex-bwolf-brand-owner' in p
    assert 'CONFIRM PALLTEX IS BWOLF MANUFACTURER' in p

def test_r7k2_does_not_weaken_canonical_bridge_manufacturer_gate():
    p=Path("admin-platform/app/services/v073_phase46/r4_r1_canonical_payload_bridge.py").read_text(encoding="utf-8")
    assert 'manufacturer.get("status")=="OPERATOR_CONFIRMED_EXACT"' in p
    assert 'manufacturer.get("manufacturer_product_code_status")=="VERIFIED_EXACT_REFERENCE"' in p

def test_identity_policy_audit_matches_superseding_governance_decision():
    import json
    policy=json.loads(Path("config/identity/m99_identity_policy.json").read_text(encoding="utf-8"))
    assert policy["format"]=="M99 000001"
    assert policy["regex"]=="^M99 [0-9]{6}$"
    p=Path("DECISION_REGISTRY.yaml").read_text(encoding="utf-8")
    assert "M99 canonical reference format is M99 + single space + exactly six digits." in p
    assert "supersedes: ID-002" in p
    allocator=Path("admin-platform/app/services/v073_phase46/canonical_identity_allocator.py").read_text(encoding="utf-8")
    assert 'NORMATIVE_M99_RE = re.compile(r"^M99 ([0-9]{6})$")' in allocator
    assert 'return f"M99 {high+1:06d}"' in allocator
