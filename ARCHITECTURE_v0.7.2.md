# M99 Architecture v0.7.2 — Canonical Data Model Foundation

## Goal

v0.7.2 begins the conversion of accumulated M99 architecture into stable,
version-independent production contracts.

## Phase 1 scope

This phase introduces a dependency-light `core/catalog` domain layer with:

- ProductGroup
- Product
- ProductVariant
- SupplierOffer
- ExternalIdentity
- Market
- Channel
- ChannelProductGroup
- ChannelPresence
- InventoryMapping
- KnowledgeStatus
- ProductLifecycle
- PublicationStatus

## Ownership rules

### M99 owns
- canonical M99 identity;
- ProductGroup/Product/ProductVariant relationships;
- supplier mappings and evidence links;
- market/channel configuration;
- publication mappings and governance.

### Dolibarr / ERP owns operational stock
InventoryMapping points to ERP inventory entities. M99 does not duplicate
physical stock quantity as canonical truth.

### External systems never own M99 identity
Supplier SKU, Dolibarr ID, website ID, EAN/GTIN and marketplace IDs are
ExternalIdentity mappings.

## Lifecycle rules

ProductLifecycle:
`draft -> active -> paused -> retired`

Retired is terminal in the baseline state machine.

Hard deletion requires:
1. operator approval;
2. explicit hard-delete permission;
3. literal `DELETE` confirmation.

An audit event will be mandatory when this contract is wired into Admin.

## Market/channel rule

A Market is a commercial/geographic context.
A Channel is a publication/operational endpoint inside a Market.
They are deliberately separate entities.

## Channel presence rule

Removing or disabling a product from a channel is represented by mappings and
PublicationStatus. It does not delete ProductGroup, Product, ProductVariant or
accumulated knowledge.

## Inventory rule

InventoryMapping records how an M99 variant maps to the operational ERP/warehouse.
It deliberately contains no canonical quantity field.

## Next phases of v0.7.2

1. SQLAlchemy persistence mappings.
2. Alembic migration baseline.
3. Admin read-only screens over canonical model.
4. Supplier master-data boundary.
5. Customer/counterparty boundary.
6. Dolibarr synchronization contracts.
7. Controlled migration adapters for legacy data.
