# M99 v0.7.3 Phase 3
## Product Presence + Daily Sync + External Warehouse Foundation

### Governance baseline

This phase implements the next README v9 priorities after the successful
Phase 2 Revision 1 foundation.

It implements persistent foundations for:

1. Product Presence / Channel Mapping.
2. Existing Product Daily Sync compare rules.
3. Dolibarr external Supplier/Manufacturer warehouse semantics.

It does not reopen any Decision Registry v002 rule.

### Product Presence

Bidirectional reports are supported:

Product → Channels / ERP
Channel / ERP → Products

Presence remains separate from stock.

States:
NOT_PRESENT
PRESENT_DRAFT
PRESENT_TEST
PRESENT_ACTIVE
PRESENT_PAUSED
PRESENT_RETIRED
PRESENT_LAST_VERIFIED
UNKNOWN
VERIFICATION_FAILED

A verification failure does not destroy the last verified PRESENT truth.

### Daily Existing Product Sync

This phase implements the compare/policy foundation only.

Change states:
NO_CHANGE
PRICE_CHANGED
AVAILABILITY_CHANGED
VARIANT_AVAILABILITY_CHANGED
PRODUCT_CHANGED
SUPPLIER_DISCONTINUED
VERIFICATION_FAILED

NO_CHANGE → NO_WRITE.

Daily Sync filters writes to already-existing Product Presence mappings only.
A missing channel is skipped/blocked and is never auto-created by Daily Sync.

Verification failure:
- no write;
- preserve last verified state;
- never infer zero stock, NOT_PRESENT or discontinued.

### External Supplier / Manufacturer Warehouses

Dedicated mapping types:
SUPPLIER_EXTERNAL
MANUFACTURER_EXTERNAL

These are explicitly different from:
M99_PHYSICAL

External availability may be:
EXACT_QUANTITY
IN_STOCK
LOW_STOCK
OUT_OF_STOCK
ON_REQUEST
UNKNOWN
VERIFICATION_FAILED

An exact quantity is accepted only when the source exposes a verified exact
quantity. Qualitative availability never receives an invented number.

External availability is variant-aware.

### Safety boundary

This installer:
- makes no external HTTP calls;
- makes no Dolibarr API writes;
- performs no production DB migration;
- performs no channel writes;
- performs no automatic Git Push.

Dedicated tests use temporary SQLite databases.

### Next

After Phase 3 is committed and pushed:

1. formal Alembic migration for v0.7.3 Phase 2/3 tables;
2. Super Admin Organization / SupplierSource / external warehouse configuration;
3. Identity Resolver integration;
4. LIVE VERIFY Product Presence via target adapters;
5. Daily Sync orchestration using SupplierConnector + SupplierObservation;
6. controlled Dolibarr external warehouse adapter;
7. live per-channel preflight;
8. controlled TEST/Draft publishing from generalized Add Products.
