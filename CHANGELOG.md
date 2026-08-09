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
