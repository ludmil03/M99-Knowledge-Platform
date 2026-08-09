

# M99 v0.5.4 — Identity, Catalog & Optimization Guardrails

- Canonical M99 ID: `M99 000001` (M99 + space + six digits).
- Existing MoneyWork, Dolibarr and website identifiers are preserved as mappings.
- Existing website canonical URLs are protected during SEO/content enrichment.
- Hierarchy: ProductGroup -> Product -> Variant.
- Each stock-managed variant gets its own M99 ID.
- Website UX may expose one product page with size/color attributes.
- Dolibarr may hold each stock-managed variant as a separate product/SKU.
- Supplier is a commercial relationship, not a canonical product category.
- One variant can have multiple SupplierProduct records.
- SEO/AI optimization is evaluated per Channel x Market using KEEP / ENRICH / REPLACE.
- Changes require evidence; successful existing pages are not rewritten automatically.
- Previous versions/baselines must be retained for rollback.
- Sync ownership: M99=identity/knowledge/SEO workflow; Dolibarr=stock/PMP/ERP; Channel=existing URL/record ID.
- Migration from old M99-PM/M99-PV IDs is phased through aliases, not destructive renaming.


# M99 v0.5.5 — Bultex99 B2B Connector + Pricing + Availability

- Bultex99 B2B is modeled as an authenticated HTML supplier source.
- Product pages `/pap/minfo.php?i=...` provide supplier product ID, variant code,
  B2B purchase price, recommended price, warehouse stock, barcode and name.
- No credentials are stored in GitHub.
- Live login remains disabled until exact form field names are confirmed.
- Stenso public gross price is the competitor/reference price.
- Default target selling price = Stenso public gross price minus 1.5%.
- Never publish below Dolibarr acquisition cost.
- Profit floor can force operator review.
- Bultex B2B current purchase price never silently overwrites historical Dolibarr cost.
- Own stock master = Dolibarr.
- Supplier stock source = Bultex99 B2B.
- Availability is variant-level.


# M99 v0.5.6 — Bultex99 B2B Read-Only Live Test

This release adds a safe live-read harness.

## Scope
- Discover the actual login form field names from `/pap/login.php`.
- Authenticate only if the three identity fields are safely mapped.
- Read only `/pap/minfo.php?i=<numeric id>`.
- Parse the control product and compare current values with the values manually
  verified in Chrome DevTools.

## Control product
- B2B product id: 109168
- Supplier variant: 06200368.39
- Size: 39
- Warehouse: 222 Radinovo
- Previous B2B purchase price: 23.24 EUR ex VAT
- Previous recommended/final price: 37.08 EUR ex VAT
- Previous supplier stock: 45 pairs
- Barcode: 2006200368030

A difference is reported as CHANGED, not treated as an error, because price and
stock are expected to change.

## Credential safety
Credentials are entered locally at runtime and exist only in the current
PowerShell process. They are cleared after the test. No `.env`, JSON, source
file, log or Git commit stores them.

## Write safety
This harness contains no method for:
- adding to basket;
- creating an order;
- writing documents;
- changing Dolibarr;
- changing any sales channel.

v0.5.6 is therefore a supplier READ-ONLY integration test.
