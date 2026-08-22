from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

from app.persistence.v073_phase3.database import create_temporary_or_explicit_schema
from app.services.v073_phase3.daily_sync import (
    SupplierState,
    compare_supplier_state,
    filter_existing_write_targets,
)
from app.services.v073_phase3.external_warehouse import (
    ensure_external_warehouse_mapping,
    record_external_availability,
)
from app.services.v073_phase3.product_presence import (
    missing_in_targets,
    product_to_targets,
    target_to_products,
    upsert_presence,
)


@pytest.fixture
def db_url(tmp_path):
    url = f"sqlite:///{(tmp_path / 'phase3.sqlite3').as_posix()}"
    create_temporary_or_explicit_schema(url)
    return url


def test_product_presence_is_bidirectional(db_url):
    upsert_presence(
        db_url,
        m99_product_id="M99-100001",
        target_key="m99.eu",
        target_type="CHANNEL",
        presence_status="PRESENT_ACTIVE",
        external_product_id="501",
        verified=True,
    )
    upsert_presence(
        db_url,
        m99_product_id="M99-100001",
        target_key="mela99.com",
        target_type="CHANNEL",
        presence_status="PRESENT_TEST",
        external_product_id="9001",
        verified=True,
    )

    product_rows = product_to_targets(db_url, "M99-100001")
    assert {x["target_key"] for x in product_rows} == {"m99.eu", "mela99.com"}

    target_rows = target_to_products(db_url, "m99.eu")
    assert [x["m99_product_id"] for x in target_rows] == ["M99-100001"]


def test_presence_verification_failure_preserves_last_verified_present(db_url):
    before = upsert_presence(
        db_url,
        m99_product_id="M99-100002",
        target_key="m99.eu",
        target_type="CHANNEL",
        presence_status="PRESENT_ACTIVE",
        external_product_id="777",
        verified=True,
    )
    assert before["presence_status"] == "PRESENT_ACTIVE"

    after = upsert_presence(
        db_url,
        m99_product_id="M99-100002",
        target_key="m99.eu",
        target_type="CHANNEL",
        presence_status="VERIFICATION_FAILED",
        last_error="HTTP timeout",
    )
    assert after["presence_status"] == "PRESENT_LAST_VERIFIED"
    assert after["last_error"] == "HTTP timeout"


def test_missing_target_report(db_url):
    upsert_presence(
        db_url,
        m99_product_id="M99-1",
        target_key="m99.eu",
        target_type="CHANNEL",
        presence_status="PRESENT_ACTIVE",
        verified=True,
    )
    result = missing_in_targets(
        db_url,
        canonical_product_ids=["M99-1", "M99-2"],
        target_keys=["m99.eu", "laviro.ro"],
    )
    index = {x["m99_product_id"]: set(x["missing_targets"]) for x in result}
    assert index["M99-1"] == {"laviro.ro"}
    assert index["M99-2"] == {"m99.eu", "laviro.ro"}


def test_daily_sync_no_change_means_no_write():
    state = SupplierState(
        verification_ok=True,
        price="100.00",
        availability="IN_STOCK",
        variants=(("42","IN_STOCK"),("43","OUT_OF_STOCK")),
        product_fingerprint="abc",
    )
    decision = compare_supplier_state(state, state)
    assert decision.change_state == "NO_CHANGE"
    assert decision.write_required is False


def test_daily_sync_detects_variant_availability_change():
    previous = SupplierState(
        verification_ok=True,
        price="100.00",
        availability="PARTIAL_VARIANT_AVAILABILITY",
        variants=(("42","IN_STOCK"),("43","OUT_OF_STOCK")),
        product_fingerprint="abc",
    )
    current = SupplierState(
        verification_ok=True,
        price="100.00",
        availability="PARTIAL_VARIANT_AVAILABILITY",
        variants=(("42","OUT_OF_STOCK"),("43","IN_STOCK")),
        product_fingerprint="abc",
    )
    decision = compare_supplier_state(previous, current)
    assert decision.change_state == "VARIANT_AVAILABILITY_CHANGED"
    assert decision.write_required is True


def test_daily_sync_verification_failure_preserves_last_verified():
    previous = SupplierState(
        verification_ok=True,
        price="100.00",
        availability="IN_STOCK",
        variants=(),
        product_fingerprint="abc",
    )
    failed = SupplierState(
        verification_ok=False,
        price=None,
        availability=None,
        variants=(),
    )
    decision = compare_supplier_state(previous, failed)
    assert decision.change_state == "VERIFICATION_FAILED"
    assert decision.write_required is False
    assert decision.preserve_last_verified is True


def test_daily_sync_never_auto_creates_missing_channel():
    writable, skipped = filter_existing_write_targets(
        requested_existing_targets=["m99.eu", "laviro.ro", "mela99.com"],
        presence_by_target={
            "m99.eu": "PRESENT_ACTIVE",
            "mela99.com": "PRESENT_TEST",
            "laviro.ro": "NOT_PRESENT",
        },
    )
    assert set(writable) == {"m99.eu", "mela99.com"}
    assert skipped == ["laviro.ro"]


def test_external_supplier_warehouse_is_not_physical_stock(db_url):
    mapping = ensure_external_warehouse_mapping(
        db_url,
        organization_id="org-stenso",
        organization_name="STENSO",
        warehouse_type="SUPPLIER_EXTERNAL",
    )
    assert mapping["warehouse_type"] == "SUPPLIER_EXTERNAL"
    assert "EXTERNAL" in mapping["display_name"]


def test_external_warehouse_rejects_fake_quantity_for_qualitative_state(db_url):
    mapping = ensure_external_warehouse_mapping(
        db_url,
        organization_id="org-stenso",
        organization_name="STENSO",
        warehouse_type="SUPPLIER_EXTERNAL",
    )
    with pytest.raises(ValueError):
        record_external_availability(
            db_url,
            warehouse_mapping_id=mapping["warehouse_mapping_id"],
            m99_product_id="M99-1",
            availability_state="IN_STOCK",
            exact_quantity=30,
        )


def test_external_warehouse_accepts_exact_quantity_only_when_explicit(db_url):
    mapping = ensure_external_warehouse_mapping(
        db_url,
        organization_id="org-stenso",
        organization_name="STENSO",
        warehouse_type="SUPPLIER_EXTERNAL",
    )
    result = record_external_availability(
        db_url,
        warehouse_mapping_id=mapping["warehouse_mapping_id"],
        m99_product_id="M99-1",
        m99_variant_id="M99-1-42",
        availability_state="EXACT_QUANTITY",
        exact_quantity=7,
    )
    assert result["exact_quantity"] == 7
    assert result["m99_variant_id"] == "M99-1-42"


def test_external_warehouse_rejects_m99_physical_type(db_url):
    with pytest.raises(ValueError):
        ensure_external_warehouse_mapping(
            db_url,
            organization_id="org-m99",
            organization_name="M99",
            warehouse_type="M99_PHYSICAL",
        )


def test_phase3_architecture_keeps_production_and_external_writes_off():
    text = (ROOT / "ARCHITECTURE_v0.7.3_PHASE3.md").read_text(encoding="utf-8-sig")
    assert "makes no external HTTP calls" in text
    assert "makes no Dolibarr API writes" in text
    assert "performs no production DB migration" in text
    assert "NO_CHANGE" in text
    assert "never auto-created by Daily Sync" in text
