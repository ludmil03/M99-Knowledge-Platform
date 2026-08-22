from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.persistence.v073_phase3.database import make_session_factory
from app.persistence.v073_phase3.models import (
    AVAILABILITY_STATES,
    WAREHOUSE_TYPES,
    ExternalAvailabilityObservation,
    ExternalWarehouseMapping,
    new_id,
)


def ensure_external_warehouse_mapping(
    database_url: str,
    *,
    organization_id: str,
    organization_name: str,
    warehouse_type: str,
    dolibarr_warehouse_id: str | None = None,
) -> dict:
    if warehouse_type not in {"SUPPLIER_EXTERNAL", "MANUFACTURER_EXTERNAL"}:
        raise ValueError("Only external supplier/manufacturer warehouse types are allowed here.")

    factory = make_session_factory(database_url)
    with factory.begin() as session:
        row = session.scalar(
            select(ExternalWarehouseMapping).where(
                ExternalWarehouseMapping.organization_id == organization_id,
                ExternalWarehouseMapping.warehouse_type == warehouse_type,
            )
        )
        if row is None:
            suffix = "SUPPLIER" if warehouse_type == "SUPPLIER_EXTERNAL" else "MANUFACTURER"
            row = ExternalWarehouseMapping(
                id=new_id("warehouse"),
                organization_id=organization_id,
                organization_name=organization_name,
                warehouse_type=warehouse_type,
                dolibarr_warehouse_id=dolibarr_warehouse_id,
                display_name=f"{organization_name} — EXTERNAL {suffix}",
            )
            session.add(row)
        elif dolibarr_warehouse_id is not None:
            row.dolibarr_warehouse_id = dolibarr_warehouse_id

        session.flush()
        return {
            "warehouse_mapping_id": row.id,
            "organization_id": row.organization_id,
            "warehouse_type": row.warehouse_type,
            "display_name": row.display_name,
            "dolibarr_warehouse_id": row.dolibarr_warehouse_id,
        }


def record_external_availability(
    database_url: str,
    *,
    warehouse_mapping_id: str,
    m99_product_id: str,
    availability_state: str,
    exact_quantity: int | None,
    m99_variant_id: str | None = None,
    supplier_mapping_id: str | None = None,
    verification_error: str | None = None,
) -> dict:
    if availability_state not in AVAILABILITY_STATES:
        raise ValueError(f"Invalid availability state: {availability_state}")

    if exact_quantity is not None and availability_state != "EXACT_QUANTITY":
        raise ValueError("Exact quantity may be stored only with EXACT_QUANTITY state.")

    if availability_state == "EXACT_QUANTITY" and exact_quantity is None:
        raise ValueError("EXACT_QUANTITY requires an exact quantity.")

    factory = make_session_factory(database_url)
    with factory.begin() as session:
        warehouse = session.get(ExternalWarehouseMapping, warehouse_mapping_id)
        if warehouse is None:
            raise ValueError("External warehouse mapping not found.")
        if warehouse.warehouse_type not in {"SUPPLIER_EXTERNAL", "MANUFACTURER_EXTERNAL"}:
            raise ValueError("External availability cannot be written to M99 physical stock mapping.")

        row = ExternalAvailabilityObservation(
            id=new_id("availability"),
            warehouse_mapping_id=warehouse_mapping_id,
            m99_product_id=m99_product_id,
            m99_variant_id=m99_variant_id,
            supplier_mapping_id=supplier_mapping_id,
            availability_state=availability_state,
            exact_quantity=exact_quantity,
            observed_at=datetime.now(timezone.utc),
            verified_at=None if availability_state == "VERIFICATION_FAILED" else datetime.now(timezone.utc),
            verification_error=verification_error,
        )
        session.add(row)
        session.flush()

        return {
            "observation_id": row.id,
            "warehouse_type": warehouse.warehouse_type,
            "m99_product_id": row.m99_product_id,
            "m99_variant_id": row.m99_variant_id,
            "availability_state": row.availability_state,
            "exact_quantity": row.exact_quantity,
            "verification_error": row.verification_error,
        }
