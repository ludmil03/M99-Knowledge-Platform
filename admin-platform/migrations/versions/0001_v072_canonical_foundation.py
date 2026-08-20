"""M99 v0.7.2 canonical persistence baseline.

Revision ID: 0001_v072_canonical
Revises:
Create Date: 2026-08-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_v072_canonical"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "canonical_product_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("m99_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("lifecycle", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("m99_id", name="uq_canonical_product_groups_m99_id"),
    )
    op.create_index("ix_canonical_product_groups_m99_id", "canonical_product_groups", ["m99_id"])
    op.create_index("ix_canonical_product_groups_lifecycle", "canonical_product_groups", ["lifecycle"])

    op.create_table(
        "canonical_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("m99_id", sa.String(length=64), nullable=False),
        sa.Column("product_group_id", sa.Integer(), sa.ForeignKey("canonical_product_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("lifecycle", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("m99_id", name="uq_canonical_products_m99_id"),
    )
    op.create_index("ix_canonical_products_m99_id", "canonical_products", ["m99_id"])
    op.create_index("ix_canonical_products_group", "canonical_products", ["product_group_id"])
    op.create_index("ix_canonical_products_lifecycle", "canonical_products", ["lifecycle"])

    op.create_table(
        "canonical_product_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("m99_id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("canonical_products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("variant_key", sa.String(length=160), nullable=False),
        sa.Column("lifecycle", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("m99_id", name="uq_canonical_product_variants_m99_id"),
        sa.UniqueConstraint("product_id", "variant_key", name="uq_canonical_product_variant_key"),
    )
    op.create_index("ix_canonical_product_variants_m99_id", "canonical_product_variants", ["m99_id"])
    op.create_index("ix_canonical_product_variants_product", "canonical_product_variants", ["product_id"])
    op.create_index("ix_canonical_product_variants_lifecycle", "canonical_product_variants", ["lifecycle"])

    op.create_table(
        "canonical_external_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_type", sa.String(length=40), nullable=False),
        sa.Column("owner_m99_id", sa.String(length=64), nullable=False),
        sa.Column("system", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("system", "entity_type", "external_id", name="uq_canonical_external_identity_source"),
        sa.UniqueConstraint("owner_type", "owner_m99_id", "system", name="uq_canonical_external_identity_owner_system"),
    )
    op.create_index("ix_canonical_external_owner", "canonical_external_identities", ["owner_type", "owner_m99_id"])
    op.create_index("ix_canonical_external_source", "canonical_external_identities", ["system", "external_id"])

    op.create_table(
        "canonical_markets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("default_currency", sa.String(length=3), nullable=False),
        sa.Column("default_language", sa.String(length=12), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("code", name="uq_canonical_markets_code"),
    )
    op.create_index("ix_canonical_markets_code", "canonical_markets", ["code"])

    op.create_table(
        "canonical_channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("market_id", sa.Integer(), sa.ForeignKey("canonical_markets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("code", name="uq_canonical_channels_code"),
    )
    op.create_index("ix_canonical_channels_code", "canonical_channels", ["code"])
    op.create_index("ix_canonical_channels_market", "canonical_channels", ["market_id"])

    op.create_table(
        "canonical_supplier_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("m99_id", sa.String(length=64), nullable=False),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("canonical_product_variants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("supplier_sku", sa.String(length=160), nullable=False),
        sa.Column("purchase_price_ex_vat", sa.Numeric(18, 6), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("m99_id", name="uq_canonical_supplier_offers_m99_id"),
        sa.UniqueConstraint("supplier_id", "variant_id", "supplier_sku", name="uq_canonical_supplier_variant_sku"),
    )
    op.create_index("ix_canonical_supplier_offer_supplier", "canonical_supplier_offers", ["supplier_id"])
    op.create_index("ix_canonical_supplier_offer_variant", "canonical_supplier_offers", ["variant_id"])

    op.create_table(
        "canonical_channel_product_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("channel_id", sa.Integer(), sa.ForeignKey("canonical_channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_group_id", sa.Integer(), sa.ForeignKey("canonical_product_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("channel_id", "product_group_id", name="uq_canonical_channel_product_group"),
    )

    op.create_table(
        "canonical_channel_presence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("channel_id", sa.Integer(), sa.ForeignKey("canonical_channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("canonical_product_variants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("publication_status", sa.String(length=40), nullable=False, server_default="not_published"),
        sa.Column("external_product_id", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("channel_id", "variant_id", name="uq_canonical_channel_variant_presence"),
    )

    op.create_table(
        "canonical_inventory_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("canonical_product_variants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system", sa.String(length=80), nullable=False),
        sa.Column("warehouse_id", sa.String(length=120), nullable=False),
        sa.Column("external_product_id", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("variant_id", "system", "warehouse_id", name="uq_canonical_inventory_mapping"),
    )


def downgrade() -> None:
    op.drop_table("canonical_inventory_mappings")
    op.drop_table("canonical_channel_presence")
    op.drop_table("canonical_channel_product_groups")
    op.drop_table("canonical_supplier_offers")
    op.drop_table("canonical_channels")
    op.drop_table("canonical_markets")
    op.drop_index("ix_canonical_external_source", table_name="canonical_external_identities")
    op.drop_index("ix_canonical_external_owner", table_name="canonical_external_identities")
    op.drop_table("canonical_external_identities")
    op.drop_index("ix_canonical_product_variants_lifecycle", table_name="canonical_product_variants")
    op.drop_index("ix_canonical_product_variants_product", table_name="canonical_product_variants")
    op.drop_index("ix_canonical_product_variants_m99_id", table_name="canonical_product_variants")
    op.drop_table("canonical_product_variants")
    op.drop_index("ix_canonical_products_lifecycle", table_name="canonical_products")
    op.drop_index("ix_canonical_products_group", table_name="canonical_products")
    op.drop_index("ix_canonical_products_m99_id", table_name="canonical_products")
    op.drop_table("canonical_products")
    op.drop_index("ix_canonical_product_groups_lifecycle", table_name="canonical_product_groups")
    op.drop_index("ix_canonical_product_groups_m99_id", table_name="canonical_product_groups")
    op.drop_table("canonical_product_groups")
