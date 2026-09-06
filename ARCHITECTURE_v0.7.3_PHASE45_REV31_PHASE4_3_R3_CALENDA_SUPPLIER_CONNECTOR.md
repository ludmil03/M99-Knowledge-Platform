# Revision 31 Phase 4.3 R3 — Calenda Supplier Connector

Calenda is implemented as a source-specific PUBLIC_WEBSITE adapter using the already decided STENSO connector contract:

`health_check -> list_categories -> list_products -> get_product`

Observed Calenda public URL contract used by this adapter:
- category pages: `/categories/<slug-id>`
- product pages: `/products/<numeric-id>`

The connector reads:
- supplier categories from the authorized Calenda source;
- products from a chosen category;
- product name;
- supplier code/reference;
- price excluding VAT when present;
- observed stock/availability text;
- description;
- source images;
- color observation when present.

It does not invent missing fields. Missing evidence remains a warning.

R3 is read-only:
- no product create/update;
- no target-channel write;
- no stock write;
- no DB migration;
- no credentials;
- no installer HTTP;
- no commit/push.

Acceptance order:
1. Add Products -> Календа -> Open source.
2. Real Calenda categories appear.
3. Open one category.
4. Real `/products/<id>` rows appear.
5. Hydrate exactly one product and visually compare with Calenda.
6. Only after acceptance: Identity -> DRAFT ImportJob -> Targets -> Canonical Preview.
