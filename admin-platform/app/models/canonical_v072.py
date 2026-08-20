from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalProductGroup(Base):
    __tablename__ = "canonical_product_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    m99_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    lifecycle: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class CanonicalProduct(Base):
    __tablename__ = "canonical_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    m99_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    product_group_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_product_groups.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    lifecycle: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class CanonicalProductVariant(Base):
    __tablename__ = "canonical_product_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "variant_key", name="uq_canonical_product_variant_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    m99_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_products.id", ondelete="RESTRICT"), index=True
    )
    variant_key: Mapped[str] = mapped_column(String(160))
    lifecycle: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class CanonicalExternalIdentity(Base):
    __tablename__ = "canonical_external_identities"
    __table_args__ = (
        UniqueConstraint(
            "system", "entity_type", "external_id",
            name="uq_canonical_external_identity_source"
        ),
        UniqueConstraint(
            "owner_type", "owner_m99_id", "system",
            name="uq_canonical_external_identity_owner_system"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(40), index=True)
    owner_m99_id: Mapped[str] = mapped_column(String(64), index=True)
    system: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CanonicalSupplierOffer(Base):
    __tablename__ = "canonical_supplier_offers"
    __table_args__ = (
        UniqueConstraint(
            "supplier_id", "variant_id", "supplier_sku",
            name="uq_canonical_supplier_variant_sku"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    m99_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"), index=True
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_product_variants.id", ondelete="RESTRICT"), index=True
    )
    supplier_sku: Mapped[str] = mapped_column(String(160), index=True)
    purchase_price_ex_vat: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    available: Mapped[bool] = mapped_column(Boolean, default=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CanonicalMarket(Base):
    __tablename__ = "canonical_markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    country_code: Mapped[str] = mapped_column(String(2))
    default_currency: Mapped[str] = mapped_column(String(3))
    default_language: Mapped[str] = mapped_column(String(12))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CanonicalChannel(Base):
    __tablename__ = "canonical_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    market_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_markets.id", ondelete="RESTRICT"), index=True
    )
    kind: Mapped[str] = mapped_column(String(40))
    base_url: Mapped[str] = mapped_column(String(500), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CanonicalChannelProductGroup(Base):
    __tablename__ = "canonical_channel_product_groups"
    __table_args__ = (
        UniqueConstraint(
            "channel_id", "product_group_id",
            name="uq_canonical_channel_product_group"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_channels.id", ondelete="CASCADE"), index=True
    )
    product_group_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_product_groups.id", ondelete="CASCADE"), index=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class CanonicalChannelPresence(Base):
    __tablename__ = "canonical_channel_presence"
    __table_args__ = (
        UniqueConstraint(
            "channel_id", "variant_id",
            name="uq_canonical_channel_variant_presence"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_channels.id", ondelete="CASCADE"), index=True
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_product_variants.id", ondelete="CASCADE"), index=True
    )
    publication_status: Mapped[str] = mapped_column(
        String(40), default="not_published", index=True
    )
    external_product_id: Mapped[str] = mapped_column(String(160), default="")
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CanonicalInventoryMapping(Base):
    __tablename__ = "canonical_inventory_mappings"
    __table_args__ = (
        UniqueConstraint(
            "variant_id", "system", "warehouse_id",
            name="uq_canonical_inventory_mapping"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_product_variants.id", ondelete="CASCADE"), index=True
    )
    system: Mapped[str] = mapped_column(String(80), index=True)
    warehouse_id: Mapped[str] = mapped_column(String(120))
    external_product_id: Mapped[str] = mapped_column(String(160), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
