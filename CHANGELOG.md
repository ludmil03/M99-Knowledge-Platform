# CHANGELOG

Всички съществени промени по проекта **M99 Knowledge Platform** се документират в този файл.

Проектът следва принципите на:

- Semantic Versioning (SemVer)
- Milestones
- Sprint Development
- Continuous Documentation

---

# [0.1.0] - 2026-08-03

## 🚀 Project Initialization

### Repository

- Created GitHub repository **M99-Knowledge-Platform**
- Repository set as official project source

---

## 📚 Documentation

Added

- README.md
- PROJECT_STATE.md
- ROADMAP.md
- CHANGELOG.md

---

## 🏗 Architecture

Established the core architecture of the platform.

### Principles

- Single Source of Truth
- Knowledge First
- AI Native
- Evidence Based
- No Duplicate Data

---

## 📖 Knowledge Model

Defined the first version of the M99 Knowledge Model.

Main entities:

- Brand
- Product
- Technology
- Material
- Standard
- Collection
- Profession
- Risk
- Supplier

---

## 🎯 Reference Product

Selected the first Gold Master product:

**PUMA VELOCITY 2.0 BLACK LOW S3S ESD**

---

## 📑 Source Priority

Official information priority:

1. Official Manufacturer
2. Official Catalog
3. Official Certificates
4. Official Technical Documentation
5. Supplier Information
6. M99 Expert Knowledge
7. AI Generated Content (validated only)

---

## 🛣 Roadmap

Defined milestones:

- M0 Foundation
- M1 Puma Brand Library
- M2 Gold Master Product
- M3 Publishing Engine
- M4 Multi Brand Support
- M5 ERP Integration
- M6 AI Agents

---

## 🔜 Next Deliverables

- DATABASE.sql
- brand.schema.json
- product.schema.json
- technology.schema.json
- material.schema.json
- standard.schema.json

---

# Versioning

The project follows Semantic Versioning.

MAJOR.MINOR.PATCH

Examples

0.1.0

0.2.0

1.0.0

---

## Commit Convention

Example:

feat(database): initial schema

feat(puma): add brand knowledge

feat(product): add Velocity 2.0 Gold Master

docs: update roadmap

fix(schema): correct technology relation

---

## Status

Current Version

0.1.0 Alpha

Current Milestone

M0 – Foundation

Current Sprint

Sprint 0

Status

🟢 Active Development

---

© M99 Group

---

# [0.5.0] - 2026-08-08

## MoneyWork Migration & Dolibarr Adapter

### Added
- MoneyWork fixed-width ARTDATA parser
- MoneyWork customer/supplier CSV wrapper parser
- Migration quarantine for malformed legacy rows
- Counterparty normalization and conservative deduplication
- Unified CUSTOMER/SUPPLIER role clustering
- Dolibarr 44-column product exporter
- First nine M99 variants for M99-PM-000001

### Safety decisions
- MoneyWork IDs remain external mappings.
- ARTDATA opaque numeric tail is not interpreted as price.
- Unknown price/VAT/cost values remain blank.
- Real customer and supplier datasets are not committed to Git.

---

# [0.5.3] - 2026-08-09

## Dolibarr Compatibility Fix
- Fixed Dolibarr 20.0.2 error: `Column 'pmp' cannot be null`.
- New product exports initialize `p.pmp` to numeric `0`.
- This is a technical initial PMP, not an inferred purchase price or cost.
- Added regression test ensuring PMP is never NULL.


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


# v0.5.6.1 — Bultex parser hotfix

The v0.5.6 regression test correctly exposed a parser bug.

Cause:
The parser treated any decimal in the HTML as a possible price, so the
supplier variant code `06200368.39` was interpreted as `6200368.39`.

Fix:
- Purchase price is now parsed only from the labelled `Цена` field.
- Recommended price is parsed only from the labelled `Крайна цена` field.
- Supplier variant codes cannot be interpreted as prices.
- Regression coverage added.

No live-write capability is added.
