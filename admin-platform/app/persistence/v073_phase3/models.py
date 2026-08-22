from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Phase3Base(DeclarativeBase):
    """Isolated v0.7.3 Phase 3 metadata.

    Production migration is intentionally deferred to a separately approved
    Alembic milestone.
    """


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:20]}"


PRESENCE_STATES = {
    "NOT_PRESENT",
    "PRESENT_DRAFT",
    "PRESENT_TEST",
    "PRESENT_ACTIVE",
    "PRESENT_PAUSED",
    "PRESENT_RETIRED",
    "PRESENT_LAST_VERIFIED",
    "UNKNOWN",
    "VERIFICATION_FAILED",
}

CHANGE_STATES = {
    "NO_CHANGE",
    "PRICE_CHANGED",
    "AVAILABILITY_CHANGED",
    "VARIANT_AVAILABILITY_CHANGED",
    "PRODUCT_CHANGED",
    "SUPPLIER_DISCONTINUED",
    "VERIFICATION_FAILED",
}

WAREHOUSE_TYPES = {
    "M99_PHYSICAL",
    "SUPPLIER_EXTERNAL",
    "MANUFACTURER_EXTERNAL",
}

AVAILABILITY_STATES = {
    "EXACT_QUANTITY",
    "IN_STOCK",
    "LOW_STOCK",
    "OUT_OF_STOCK",
    "ON_REQUEST",
    "UNKNOWN",
    "VERIFICATION_FAILED",
}


class ProductPresence(Phase3Base):
    __tablename__ = "m99_v073_product_presence"
    __table_args__ = (
        UniqueConstraint("m99_product_id", "target_key", name="uq_v073_presence_target"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    m99_product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    target_key: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False, default="CHANNEL")
    external_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    presence_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    publication_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    price: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    stock_representation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    readback_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    front_office_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class SupplierProductMapping(Phase3Base):
    __tablename__ = "m99_v073_supplier_product_mappings"
    __table_args__ = (
        UniqueConstraint("source_id", "source_product_key", name="uq_v073_supplier_product_key"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    m99_product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_product_key: Mapped[str] = mapped_column(String(2000), nullable=False)
    supplier_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ean_gtin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    preferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    variants: Mapped[list["SupplierVariantMapping"]] = relationship(
        back_populates="product_mapping",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SupplierVariantMapping(Phase3Base):
    __tablename__ = "m99_v073_supplier_variant_mappings"
    __table_args__ = (
        UniqueConstraint(
            "supplier_product_mapping_id",
            "source_variant_key",
            name="uq_v073_supplier_variant_key",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    supplier_product_mapping_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("m99_v073_supplier_product_mappings.id", ondelete="CASCADE"),
        nullable=False,
    )
    m99_variant_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_variant_key: Mapped[str] = mapped_column(String(255), nullable=False)
    variant_type: Mapped[str] = mapped_column(String(64), nullable=False, default="SIZE")
    variant_value: Mapped[str] = mapped_column(String(255), nullable=False)

    product_mapping: Mapped[SupplierProductMapping] = relationship(back_populates="variants")


class DailySyncRun(Phase3Base):
    __tablename__ = "m99_v073_daily_sync_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False, default="SCHEDULED")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="RUNNING")
    products_checked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    supplier_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    channel_writes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dolibarr_writes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    no_change_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    items: Mapped[list["DailySyncItem"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", lazy="selectin"
    )


class DailySyncItem(Phase3Base):
    __tablename__ = "m99_v073_daily_sync_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sync_run_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("m99_v073_daily_sync_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    m99_product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    supplier_mapping_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    change_state: Mapped[str] = mapped_column(String(64), nullable=False)
    changed_fields_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    write_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped[DailySyncRun] = relationship(back_populates="items")


class ExternalWarehouseMapping(Phase3Base):
    __tablename__ = "m99_v073_external_warehouse_mappings"
    __table_args__ = (
        UniqueConstraint("organization_id", "warehouse_type", name="uq_v073_org_wh_type"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    warehouse_type: Mapped[str] = mapped_column(String(64), nullable=False)
    dolibarr_warehouse_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    observations: Mapped[list["ExternalAvailabilityObservation"]] = relationship(
        back_populates="warehouse_mapping",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ExternalAvailabilityObservation(Phase3Base):
    __tablename__ = "m99_v073_external_availability_observations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    warehouse_mapping_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("m99_v073_external_warehouse_mappings.id", ondelete="CASCADE"),
        nullable=False,
    )
    m99_product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    m99_variant_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supplier_mapping_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    availability_state: Mapped[str] = mapped_column(String(64), nullable=False)
    exact_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    warehouse_mapping: Mapped[ExternalWarehouseMapping] = relationship(back_populates="observations")
