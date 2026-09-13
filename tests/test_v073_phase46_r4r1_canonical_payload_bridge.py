from pathlib import Path
import ast

ADMIN=Path(__file__).resolve().parents[1]/"admin-platform"
BRIDGE=ADMIN/"app/services/v073_phase46/r4_r1_canonical_payload_bridge.py"
ROUTER=ADMIN/"app/routers/phase46_r1_final_publish.py"
TPL=ADMIN/"app/templates/operator_publish/phase46_r1_final.html"
CONTENT=ADMIN/"app/services/v073_phase46/content_manufacturer_intelligence.py"
DURABLE=ADMIN/"app/services/v073_phase46/durable_draft_enrichment.py"

def test_bridge_files_compile_and_exist():
    for p in (BRIDGE,ROUTER,CONTENT,DURABLE):
        assert p.exists(); ast.parse(p.read_text(encoding="utf-8"))

def test_three_identifier_roles_are_separate():
    s=BRIDGE.read_text(encoding="utf-8")
    assert '"channel_reference_role":"PERMANENT_M99_REFERENCE"' in s
    assert '"supplier_reference_role":"SUPPLIER_MAPPING_ONLY"' in s
    assert '"manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY"' in s
    assert "supplier_ref==mref" in s

def test_manufacturer_code_requires_exact_manufacturer_evidence():
    s=BRIDGE.read_text(encoding="utf-8")
    assert 'manufacturer.get("status")=="OPERATOR_CONFIRMED_EXACT"' in s
    assert 'manufacturer.get("manufacturer_product_code_status")=="VERIFIED_EXACT_REFERENCE"' in s

def test_supplier_evidence_is_durably_persisted_for_variants():
    s=DURABLE.read_text(encoding="utf-8")
    assert "durable_enrichment.v2" in s
    assert '"supplier_evidence":supplier_evidence or {}' in s
    c=CONTENT.read_text(encoding="utf-8")
    assert "supplier_evidence=supplier_evidence or {}" in c

def test_content_no_longer_labels_supplier_ref_as_generic_model_code():
    s=CONTENT.read_text(encoding="utf-8")
    assert '"manufacturer_reference":manufacturer_ref' in s
    assert '"supplier_reference":supplier_ref' in s
    assert "Manufacturer reference / MPN" in s
    assert "Код на производителя / MPN" in s
    assert '"mpn":p.get("manufacturer_reference")' in s

def test_preview_requires_en_bg_ru_variants_images_and_v3_identifier_contract():
    s=BRIDGE.read_text(encoding="utf-8")
    assert 'REQUIRED_LANGUAGES=("EN","BG","RU")' in s
    assert "Variant/availability evidence is missing" in s
    assert "No canonical product image evidence" in s
    assert "identifier_governance" in s

def test_live_publish_is_governed_server_side_and_ui_monotonic_upgrade():
    """R7F replaces env-only enablement with stronger integrated secure settings."""
    r=ROUTER.read_text(encoding="utf-8")
    t=TPL.read_text(encoding="utf-8")
    s=(ADMIN/"app/services/v073_phase46/canonical_live_pilot.py").read_text(encoding="utf-8")
    settings=(ADMIN/"app/services/v073_phase46/secure_integration_settings.py").read_text(encoding="utf-8")
    for frag in (
        "PUBLISH CANONICAL PILOT TO M99.EU",
        "effective_m99eu_credentials()",
        'str(confirmation or "").strip()!=CONFIRMATION',
        'getattr(user,"is_superuser",False)',
        'str(getattr(job,"status","")).upper()!="DRAFT"',
        '"m99eu" not in requested or "m99eu" not in authorized',
        "validate_preview(preview)",
        "_find_existing",
        "_readback",
        'tag("active","0")',
        'tag("available_for_order","0")',
        'tag("visibility","none")',
    ):
        assert frag in s
    for frag in (
        "WINDOWS_DPAPI_CURRENT_USER",
        "effective_m99eu_credentials",
        "verify_m99eu_connection",
        "LEGACY_ENV_FALLBACK",
    ):
        assert frag in settings
    assert "payload_preview = build_canonical_payload_preview" in r
    assert "publish_canonical_pilot" in r
    assert "/integration-settings/save" in r
    assert "/integration-settings/verify" in r
    assert "M99 Integration Settings — m99.eu" in t
    assert "PUBLISH ONE HIDDEN CANONICAL PILOT" in t
    assert "PUBLISH BLOCKED — CANONICAL PREVIEW NOT READY" in t
    assert "disabled" in t
