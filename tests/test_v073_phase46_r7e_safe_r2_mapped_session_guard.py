
from pathlib import Path
from types import SimpleNamespace
import sys, pytest
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0,str(ADMIN))
from app.services.v073_phase45.m99eu_r37_auto_publish import AutoPublishError, canonical_reference_from_draft

def test_exact_previous_failure_simple_namespace():
    with pytest.raises(AutoPublishError, match="permanent canonical"):
        canonical_reference_from_draft(
            job=SimpleNamespace(),
            item=SimpleNamespace(detection={"reference":"SUP-1"})
        )

def test_unmapped_fake_matched_id_does_not_crash_or_synthesize():
    with pytest.raises(AutoPublishError, match="permanent canonical"):
        canonical_reference_from_draft(
            job=SimpleNamespace(),
            item=SimpleNamespace(detection={"reference":"93300"}, matched_product_id=123)
        )

def test_valid_embedded_m99_reference_still_works_without_session():
    assert canonical_reference_from_draft(
        job=SimpleNamespace(m99_reference="M99-77"),
        item=SimpleNamespace(detection={"reference":"SUP-1"})
    )=="M99-77"

def test_supplier_and_manufacturer_like_values_remain_noncanonical():
    for ref in ("93300","65-014-0","PUNT-52","blue","ID35","SUP-1"):
        with pytest.raises(AutoPublishError, match="permanent canonical"):
            canonical_reference_from_draft(
                job=SimpleNamespace(),
                item=SimpleNamespace(detection={"reference":ref})
            )
