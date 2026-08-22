# M99 v0.7.3 Phase 2 Revision 1

## Persistent ImportJob + Organization Registry + Live Supplier Browser Contract

### Governance baseline

This implementation follows README v9 and Decision Registry v002.

It does not reopen:
- Operator-first UX.
- Supplier/Manufacturer as Organization roles.
- Super Admin approval before operator visibility.
- Direct Supplier Selection.
- ImportJob as auditable persistent object.
- Identity Before Content.
- m99.eu as only one of multiple target channels.
- runtime read-only SupplierSource access.
- no uncontrolled external writes.

### Persistent entities

Phase2Base defines:
- Organization
- OrganizationRole
- SupplierSource
- SupplierObservation
- ImportJob
- ImportJobTarget

The schema is isolated from the production Admin database until a later,
explicitly approved Alembic migration.

### Live Supplier Connector Contract

Every live connector is read-only and implements:

health_check
list_categories
list_products
get_product
get_variants
get_images
get_commercial_data

The HTTP client permits only GET/HEAD and enforces an allowed-host list.

### STENSO reference adapter

STENSO Public Catalogue is the first reference adapter.
The installer makes no network call.

At runtime, after an explicit Phase 2 database URL is configured and the source
exists/has been seeded, an authenticated operator can browse configured category
roots. Product/category pages are fetched read-only.

Current reference root:
https://stenso.net/211-rabotni-obuvki-diadora

This is configuration data, not an operator URL-copy workflow.

### Import safety

Selecting supplier products does NOT publish them.

The intended next chain is:
Selection
→ SupplierObservation snapshot
→ persistent ImportJob
→ Identity Resolver
→ Target selection
→ pricing/content/images/variants
→ per-channel preflight
→ operator confirmation
→ TEST/Draft write
→ readback
→ Quality Report

### Daily Sync / Presence / External warehouses

README v9 and Decision Registry v002 already fix the contracts for:
- existing-product daily sync;
- Product Presence;
- Dolibarr supplier/manufacturer external availability warehouses.

They are intentionally not fully implemented in this Revision 1 code package.
The connector/observation model created here is designed to be reused by those
later runtime modules instead of creating a second supplier-reading mechanism.

### No production DB migration

Installer:
- does not create production tables;
- does not run production Alembic upgrade;
- does not contact supplier sites;
- does not write to sales channels;
- does not push Git automatically.

Dedicated tests use temporary SQLite and mocked HTTP responses.
