
from pathlib import Path

ROUTER=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py")
TPL=Path("admin-platform/app/templates/content_intelligence/review.html")

def test_r7k22_loads_checksum_verified_durable_store():
    s=ROUTER.read_text(encoding="utf-8")
    assert "load_durable_enrichment" in s
    assert "def _verified_durable_readback" in s
    assert "Durable readback supplier-reference mismatch." in s
    assert "Durable readback supplier-product URL mismatch." in s
    assert "Durable readback target mismatch." in s

def test_r7k22_readback_is_authoritative_on_review():
    s=ROUTER.read_text(encoding="utf-8")
    # Manufacturer evidence remains authoritative after checksum-verified durable readback.
    assert 'manufacturer=durable["manufacturer_evidence"]' in s

    # R7K.3.2 explicitly supersedes verbatim reuse of stale customer-facing durable content.
    # Content must be regenerated through the current generator from verified manufacturer evidence.
    assert 'content=durable["content_bundle"]' not in s
    assert 'content=build_content_bundle(' in s
    assert 'manufacturer_evidence=manufacturer' in s
    assert '"reason":"DURABLE_READBACK_VERIFIED"' in s
    assert "publish-handoff?job_id=" in s

def test_r7k22_fails_closed_on_invalid_or_mismatched_sidecar():
    s=ROUTER.read_text(encoding="utf-8")
    assert "Durable manufacturer readback blocked safely:" in s
    assert 'manufacturer.get("status") not in {"OPERATOR_CONFIRMED_EXACT","CONFIRMED_EXACT"}' in s
    assert 'if not content.get("documents")' in s

def test_r7k22_template_shows_confirmed_manufacturer_in_resolution():
    s=TPL.read_text(encoding="utf-8")
    assert "confirmed_manufacturer" in s
    assert "Manufacturer: <b>{{ manufacturer.manufacturer_name" in s
    assert "Resolution: <b>{{ manufacturer.status }}</b>" in s
    assert "Supplier and Manufacturer remain separate governed roles." in s

def test_r7k22_suppresses_duplicate_confirmation_and_manual_discovery():
    s=TPL.read_text(encoding="utf-8")
    assert "(not confirmed_manufacturer)" in s
    assert "Manufacturer is already resolved from verified durable evidence." in s

def test_r7k22_displays_verified_checksum_readback():
    s=TPL.read_text(encoding="utf-8")
    assert "Durable manufacturer readback: <b>VERIFIED</b>" in s
    assert "durable_readback.payload_sha256[:12]" in s

def test_r7k22_does_not_touch_identity_allocator_or_publish_transport():
    payload=list(Path("payload").rglob("*")) if Path("payload").exists() else []
    names={p.name for p in payload if p.is_file()}
    assert "canonical_identity_allocator.py" not in names
    assert "palltex_controlled_publish.py" not in names
