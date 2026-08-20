# M99 Architecture v0.7.2.1 — SQLAlchemy Persistence & Alembic Baseline

## Purpose

Phase 2 converts the v0.7.2 canonical domain contracts into a durable
persistence schema without replacing or mutating the existing Admin operational
tables.

## Persistence strategy

The new schema uses `canonical_*` table names so the canonical model can be
introduced safely alongside the existing Admin prototype tables.

This is deliberate. Existing tables such as `products`, `channels` and
`product_presence` are not silently repurposed.

## Tables introduced

- canonical_product_groups
- canonical_products
- canonical_product_variants
- canonical_external_identities
- canonical_supplier_offers
- canonical_markets
- canonical_channels
- canonical_channel_product_groups
- canonical_channel_presence
- canonical_inventory_mappings

## ERP boundary

`canonical_inventory_mappings` maps an M99 variant to an ERP/warehouse record.
It deliberately does not contain a stock quantity field. Operational physical
stock remains owned by the ERP/warehouse system.

## Supplier boundary

Canonical SupplierOffer references the existing supplier registry while keeping
offer identity, SKU, observed purchase price, currency and availability separate
from canonical product identity.

## Migration governance

Alembic is now the target schema-evolution mechanism.

The first canonical migration is:
`0001_v072_canonical`

The existing local database is NOT migrated automatically by the SAFE installer.
Migration testing uses a temporary SQLite database.

Applying migrations to the real Admin database will be a separate, explicit,
backed-up operator step after review.

## Next phase

Phase 3 should add:
1. repository/service mappers between `core.catalog` domain objects and
   SQLAlchemy persistence models;
2. read-only Admin views for canonical ProductGroup/Product/Variant;
3. deterministic legacy/Admin-to-canonical mapping plan;
4. explicit database backup + real migration procedure.
