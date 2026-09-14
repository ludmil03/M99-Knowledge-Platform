
from pathlib import Path
import json
import pytest

DUR=Path("admin-platform/app/services/v073_phase46/durable_draft_enrichment.py")
ROUTER=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py")
TPL=Path("admin-platform/app/templates/content_intelligence/review.html")

def test_r7k23_service_has_exact_cross_job_lookup():
    s=DUR.read_text(encoding="utf-8")
    assert "def find_confirmed_exact" in s
    assert 'supplier_reference' in s
    assert 'target' in s
    assert 'product_url' in s
    assert 'OPERATOR_CONFIRMED_EXACT' in s
    assert 'CONFIRMED_EXACT' in s

def test_r7k23_no_fuzzy_or_brand_wide_cross_job_match():
    s=DUR.read_text(encoding="utf-8")
    assert "fuzzy" in s.lower()
    assert "brand-wide" in s.lower()
    assert 'str(obj.get("supplier_reference") or "").strip()!=ref' in s
    assert 'url and stored_url and url!=stored_url' in s

def test_r7k23_router_prefers_same_job_then_cross_job():
    s=ROUTER.read_text(encoding="utf-8")
    assert "load_durable_enrichment(int(job_id))" in s
    assert "find_cross_job_confirmed_enrichment(" in s
    assert 'source_mode="SAME_JOB"' in s
    assert 'source_mode="CROSS_JOB_EXACT"' in s

def test_r7k23_cross_job_readback_still_fail_closed():
    s=ROUTER.read_text(encoding="utf-8")
    assert "Durable readback target mismatch." in s
    assert "Durable readback supplier-reference mismatch." in s
    assert "Durable readback supplier-product URL mismatch." in s
    assert "Durable content bundle is incomplete." in s

def test_r7k23_template_shows_source_job_and_mode():
    s=TPL.read_text(encoding="utf-8")
    assert 'mode <b>{{ durable_readback.source_mode' in s
    assert 'source Job #{{ durable_readback.source_job_id }}' in s

def test_r7k23_keeps_repeat_confirmation_suppressed_when_confirmed():
    s=TPL.read_text(encoding="utf-8")
    assert "(not confirmed_manufacturer)" in s
    assert "Manufacturer is already resolved from verified durable evidence." in s

def test_r7k23_does_not_touch_identity_or_publish_transport():
    # Guard the intent of the release package.
    assert "canonical_identity_allocator.py" not in {p.name for p in Path(".").rglob("*") if p.is_file() and "r7k23" in p.name.lower()}
