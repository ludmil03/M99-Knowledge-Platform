# M99-Knowledge-Platform
M99-Knowledge-Platform GPT version
# M99 Knowledge Platform

> Enterprise Knowledge Platform for Workwear, Safety Footwear, PPE and Industrial Supply

## Vision

M99 Knowledge Platform е корпоративна платформа за знания, разработена за групата M99.

Целта на проекта е да създаде единен източник на достоверна информация (Single Source of Truth), който захранва:

- онлайн магазини
- ERP системи
- CRM системи
- AI агенти
- мобилни приложения
- вътрешни инструменти
- SEO съдържание
- продуктови каталози
- бъдещи автоматизации

## Mission

Да изградим най-пълната база знания за:
- работно облекло
- защитни обувки
- лични предпазни средства (PPE)
- инструменти
- индустриални доставки

като всяка информация съществува само веднъж и се използва навсякъде.

## Core Principles

### 1. Single Source of Truth
Всеки факт се записва само веднъж.

### 2. Knowledge First
Първо се създават знанията, след което се генерират:
- продуктови описания
- SEO
- FAQ
- Product Master
- ERP записи
- CRM съдържание

### 3. No Duplicate Data
Технологиите, материалите и стандартите съществуват само веднъж и се свързват с продуктите.

### 4. Evidence Based
Приоритет на източниците:
1. Официален производител
2. Официални каталози
3. Сертификати
4. Доставчици
5. M99 Expert
6. AI (само върху проверени данни)

### 5. AI Native
AI използва проверената база знания, а не измислена информация.

## Repository Structure

```text
M99-Knowledge-Platform/
├── docs/
├── database/
├── schemas/
├── knowledge/
├── brands/
├── products/
├── technologies/
├── materials/
├── standards/
├── professions/
├── risks/
├── suppliers/
├── seo/
├── ai/
├── erp/
├── crm/
└── scripts/
```

## Current Status

- Version: 0.1 Alpha
- Sprint: 0
- Reference Product: PUMA VELOCITY 2.0 BLACK LOW S3S ESD
- Status: Foundation

## Roadmap

- Sprint 0 – Foundation
- Sprint 1 – Puma Brand Library
- Sprint 2 – Puma Technology Library
- Sprint 3 – Puma Velocity 2.0 Gold Master
- Sprint 4 – SEO Automation
- Sprint 5 – ERP Integration
- Sprint 6 – AI Agents

---

© M99 Group


# M99 Knowledge Platform

**Version:** 1.0
**Status:** Active Development
**Architecture:** Multi-market · Multi-channel · Product-centric · Evidence-driven
**Primary role:** Central knowledge, identity, market intelligence, SEO and publishing platform for the M99 ecosystem

---

# 1. Vision

**M99 Knowledge Platform** is the central intelligence and product knowledge system for the M99 business ecosystem.

Its purpose is to create a single, reliable source of truth for:

* product identity;
* product variants;
* manufacturers;
* suppliers;
* technical specifications;
* standards and certifications;
* product images and documents;
* market information;
* competitors;
* prices;
* SEO;
* content;
* customer knowledge;
* sales knowledge;
* field experience;
* historical observations;
* websites and sales channels.

The platform must not be tied to one website, one ERP system, one country or one product category.

The long-term architecture is:

```text
                    MANUFACTURERS
                         │
                    SUPPLIERS
                         │
                         ▼
              ┌─────────────────────┐
              │ M99 KNOWLEDGE       │
              │ PLATFORM            │
              └─────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 Product Identity   Product Knowledge   Market Intelligence
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                   M99 ENGINE
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
      Dolibarr          Sites         AI / SEO
        │
        ▼
 Inventory / CRM / Sales / Logistics
```

M99 must own the **product identity and accumulated knowledge**.

External systems such as MoneyWork, Dolibarr, supplier databases, manufacturer websites and marketplaces are sources, destinations or operational systems — not the master identity.

---

# 2. Core Architectural Principle

The fundamental rule is:

```text
External systems ≠ M99 Identity
```

Example:

```text
MoneyWork code
MW-0001842

        ↓

M99 Resolver / Matcher

        ↓

M99 Product
M99-PM-000001

        ↓

M99 Variant
M99-PV-000001
```

The MoneyWork product code must **not automatically become the M99 SKU**.

The same principle applies to:

* Dolibarr IDs;
* supplier SKUs;
* manufacturer SKUs;
* EAN/GTIN;
* competitor product IDs;
* website IDs;
* marketplace IDs.

They are mappings to an M99 entity.

---

# 3. M99 Product Identity

The M99 platform uses its own permanent product identity.

## Product Master

Example:

```text
M99-PM-000002
```

A Product Master represents the logical product/model.

Example:

```text
PUMA CONDOR MID S3L ESD
```

## Product Variant

Variants represent commercially or technically distinct combinations.

Example:

```text
PUMA CONDOR MID S3L ESD
│
├── Black / 39
├── Black / 40
├── Black / 41
├── ...
├── Brown / 39
├── Brown / 40
└── ...
```

Each variant can have:

```text
M99-PV-XXXXXX
```

Variants may contain:

* size;
* color;
* fit;
* material;
* voltage;
* power;
* capacity;
* configuration;
* manufacturer SKU;
* supplier SKU;
* EAN/GTIN;
* other category-specific attributes.

---

# 4. Identity Resolution Pipeline

External product records pass through a controlled identity pipeline.

```text
EXTERNAL RECORD
      │
      ▼
 importer.py
      │
      ▼
 normalization
      │
      ▼
 resolver.py
      │
      ▼
 matcher.py
      │
      ▼
 decision.py
      │
      ▼
 overrides.py
      │
      ▼
 OPERATOR REVIEW
      │
      ▼
FINAL M99 IDENTITY
```

Possible decisions:

```text
EXACT_MATCH
PROBABLE_MATCH
POSSIBLE_MATCH
NO_MATCH
CONFLICT
REQUIRES_REVIEW
```

No uncertain external record should silently modify M99 identity.

---

# 5. Evidence-Driven Knowledge

The platform distinguishes:

```text
FACT
```

from:

```text
EVIDENCE
```

Manufacturer information is generally the highest-priority technical source, but even manufacturer information should retain its source.

Possible evidence sources:

```text
manufacturer
supplier
official documentation
certificate
technical datasheet
ERP
website
competitor
customer
salesperson
field test
service technician
operator
AI inference
```

Example:

```json
{
  "claim": "Safety class S3L",
  "value": "S3L",
  "source_type": "manufacturer",
  "source_url": "...",
  "captured_at": "...",
  "confidence": 1.0
}
```

Knowledge must remain traceable.

---

# 6. Source Priority

Default evidence hierarchy:

```text
1. Official manufacturer documentation
2. Official manufacturer website
3. Certification / standards documentation
4. Official supplier information
5. Internal verified M99 data
6. ERP data
7. Customer / field observations
8. Competitor information
9. Search results
10. AI inference
```

This hierarchy may vary depending on the type of information.

For example, market price cannot be determined from manufacturer technical documentation, while technical safety class should not be inferred from competitor marketing text when official documentation exists.

---

# 7. Current M99 Websites

The platform is multi-channel.

A **channel** is not a market.

A website belongs to a market and exposes selected product groups.

---

# 8. Bulgarian Market

Market:

```text
MKT-BG
Country: Bulgaria
Language: Bulgarian
Currency: BGN / EUR according to operational requirements
```

## mela99.com

Product groups:

* workwear;
* safety footwear;
* personal protective equipment;
* medical clothing;
* medical footwear and clogs;
* hand hygiene products.

Channel ID:

```text
CH-MELA99
```

---

## rabotni-drehi.com

Product groups:

* workwear;
* safety footwear;
* personal protective equipment;
* medical clothing;
* medical footwear and clogs.

Suggested channel ID:

```text
CH-RABOTNI-DREHI
```

---

## m99.eu

Product groups:

* workwear;
* safety footwear;
* personal protective equipment;
* medical clothing;
* medical footwear and clogs;
* hand hygiene products;
* TOPMASTER tools;
* RAIDER tools;
* METABO tools.

Channel ID:

```text
CH-M99EU
```

---

## medicinski-drehi.com

Product groups:

* medical clothing;
* medical footwear;
* medical clogs.

Suggested channel ID:

```text
CH-MEDICINSKI-DREHI
```

---

## toplinka.com

Product groups:

* pellet boilers;
* pellet fireplaces;
* wood boilers;
* wood stoves;
* wood fireplaces;
* heat pumps;
* water heaters;
* buffer tanks;
* radiators;
* photovoltaic panels;
* photovoltaic inverters;
* photovoltaic batteries;
* installation services for supported systems.

Suggested channel ID:

```text
CH-TOPLINKA
```

Toplinka is architecturally important because it proves that M99 Knowledge Platform must not be designed exclusively around workwear and PPE.

The product model must support completely different technical categories.

---

# 9. Romanian Market

Market:

```text
MKT-RO
Country: Romania
Language: Romanian
Currency: RON
```

## laviro.ro

Product groups:

* workwear;
* safety footwear;
* personal protective equipment;
* medical clothing;
* medical footwear and clogs;
* hand hygiene products.

Channel ID:

```text
CH-LAVIRO
```

---

## alviro.ro

Product groups:

* medical clothing;
* medical footwear;
* medical clogs.

Suggested channel ID:

```text
CH-ALVIRO
```

---

# 10. Future Markets

Markets must never be hardcoded into the business logic.

The architecture must support:

```text
MKT-BG → Bulgaria
MKT-RO → Romania
MKT-DE → Germany
MKT-IT → Italy
MKT-GR → Greece
...
```

without redesigning the engine.

Each market may define:

```text
country
country_code
languages
currency
search_engines
channels
competitors
marketplaces
product terminology
SEO terminology
tax rules
commercial rules
shipping constraints
product availability
pricing
```

---

# 11. Dynamic Product Groups

Product groups must NOT be permanently hardcoded into websites.

They are dynamic entities.

A product group can be:

```text
ACTIVE
PAUSED
DISABLED
ARCHIVED
```

The platform must support:

```text
ADD PRODUCT GROUP
PAUSE PRODUCT GROUP
REACTIVATE PRODUCT GROUP
REMOVE FROM CHANNEL
ARCHIVE
```

without modifying core application code.

---

# 12. Product Group vs Channel

Product groups exist independently from websites.

Example:

```text
PG-SAFETY-FOOTWEAR
```

can be connected to:

```text
mela99.com
rabotni-drehi.com
m99.eu
laviro.ro
```

while:

```text
PG-MEDICAL-CLOTHING
```

can be connected to:

```text
mela99.com
rabotni-drehi.com
m99.eu
medicinski-drehi.com
laviro.ro
alviro.ro
```

The relation should therefore be:

```text
PRODUCT GROUP
      │
      ▼
CHANNEL PRODUCT GROUP MAPPING
      │
      ▼
CHANNEL
```

not:

```text
WEBSITE
   └── hardcoded categories
```

---

# 13. Proposed Channel Configuration

Example:

```json
{
  "channel_id": "CH-LAVIRO",
  "domain": "laviro.ro",
  "market_id": "MKT-RO",
  "language": "ro",
  "currency": "RON",
  "type": "ecommerce",
  "status": "ACTIVE"
}
```

Product group mapping:

```json
{
  "channel_id": "CH-LAVIRO",
  "product_group_id": "PG-SAFETY-FOOTWEAR",
  "status": "ACTIVE"
}
```

Another group may simultaneously be:

```json
{
  "channel_id": "CH-LAVIRO",
  "product_group_id": "PG-HAND-HYGIENE",
  "status": "PAUSED"
}
```

---

# 14. Product Taxonomy

A universal taxonomy is required.

Example:

```text
CATALOG
│
├── WORKWEAR
│
├── PPE
│
├── FOOTWEAR
│   ├── SAFETY FOOTWEAR
│   └── MEDICAL FOOTWEAR
│
├── MEDICAL
│   ├── MEDICAL CLOTHING
│   └── MEDICAL FOOTWEAR
│
├── HYGIENE
│
├── TOOLS
│   ├── POWER TOOLS
│   └── HAND TOOLS
│
├── HVAC
│   ├── BOILERS
│   ├── FIREPLACES
│   ├── HEAT PUMPS
│   ├── WATER HEATERS
│   ├── BUFFER TANKS
│   └── RADIATORS
│
└── SOLAR
    ├── PANELS
    ├── INVERTERS
    └── BATTERIES
```

Channel navigation can differ from the master taxonomy.

This allows SEO-specific and market-specific category structures without destroying product identity.

---

# 15. Product Knowledge Structure

Suggested product structure:

```text
knowledge/
└── products/
    └── M99-PM-000002/
        │
        ├── product.json
        ├── identity.json
        ├── variants.json
        ├── specifications.json
        ├── materials.json
        ├── technologies.json
        ├── standards.json
        ├── applications.json
        ├── certifications.json
        ├── images.json
        │
        ├── mappings/
        │   ├── manufacturer.json
        │   ├── suppliers.json
        │   ├── moneywork.json
        │   ├── dolibarr.json
        │   └── competitors.json
        │
        ├── evidence/
        │   ├── manufacturer/
        │   ├── supplier/
        │   ├── certificates/
        │   ├── technical/
        │   ├── market/
        │   └── internal/
        │
        ├── content/
        │   ├── bg/
        │   ├── ro/
        │   ├── en/
        │   └── ...
        │
        ├── market/
        │   ├── BG/
        │   ├── RO/
        │   └── ...
        │
        ├── feedback/
        │   ├── customers/
        │   ├── sales/
        │   ├── technicians/
        │   └── field_tests/
        │
        ├── documents/
        │   ├── product_knowledge.pdf
        │   ├── technical_dossier.pdf
        │   ├── market_intelligence.pdf
        │   └── seo_strategy.pdf
        │
        └── history/
```

---

# 16. Product Knowledge Lifecycle

Knowledge is not static.

```text
PRODUCT CREATED
      │
      ▼
MANUFACTURER DATA
      │
      ▼
SUPPLIER DATA
      │
      ▼
TECHNICAL DOCUMENTATION
      │
      ▼
MARKET RESEARCH
      │
      ▼
SEO / CONTENT
      │
      ▼
PRODUCT PUBLISHED
      │
      ▼
CUSTOMER FEEDBACK
      │
      ▼
SALES FEEDBACK
      │
      ▼
FIELD EXPERIENCE
      │
      ▼
UPDATED KNOWLEDGE
      │
      └───────────────┐
                      ▼
                 NEW VERSION
```

A product dossier becomes more valuable over time.

---

# 17. PDF Knowledge System

Each product may automatically generate living PDF documents.

Initial document types:

```text
Product Knowledge
Technical Dossier
Market Intelligence
SEO Content Strategy
```

Future documents may include:

```text
Customer Experience Report
Sales Knowledge Report
Field Test Report
Installation Guide
Service Knowledge
Product Comparison
Training Document
```

PDF files are outputs.

Structured M99 knowledge remains the source.

Therefore:

```text
JSON / Database Knowledge
          │
          ▼
     Document Engine
          │
          ▼
         PDF
```

not:

```text
PDF → source of truth
```

---

# 18. Market Intelligence Engine

Module:

```text
core/market_intelligence.py
```

The Market Intelligence Engine researches the market in which a channel operates.

It is market-aware, not website-hardcoded.

Pipeline:

```text
PRODUCT
   │
   ▼
MARKET
   │
   ▼
SEARCH TERMS
   │
   ▼
SERP
   │
   ▼
COMPETITORS
   │
   ▼
PRODUCT PAGES
   │
   ▼
CONTENT ANALYSIS
   │
   ▼
PRICE / AVAILABILITY
   │
   ▼
SEO SIGNALS
   │
   ▼
MARKET KNOWLEDGE
```

---

# 19. Market Crawler

Planned module:

```text
core/market_crawler.py
```

Its role is collection.

`market_intelligence.py` defines and analyses intelligence.

`market_crawler.py` discovers and collects evidence.

Conceptually:

```text
Market Intelligence
        │
        ▼
 Search Strategy
        │
        ▼
 Market Crawler
        │
        ├── Search engines
        ├── Competitors
        ├── Manufacturers
        ├── Suppliers
        └── Marketplaces
        │
        ▼
 Raw Evidence
        │
        ▼
 Intelligence Analysis
```

---

# 20. Competitor Intelligence

Competitor records must remain separate from M99 product identity.

```text
M99 PRODUCT
     │
     └── competitor mappings
              │
              ├── competitor A
              ├── competitor B
              └── competitor C
```

The system may observe:

* product name;
* URL;
* domain;
* price;
* currency;
* availability;
* position;
* title;
* meta description;
* H1;
* H2;
* H3;
* specifications;
* FAQ;
* images;
* schema;
* internal links;
* related products;
* reviews;
* delivery promises;
* commercial messaging.

Competitor content is **evidence**, not content to copy.

The objective is to understand why successful pages perform well and create better original M99 content.

---

# 21. Historical Market Intelligence

Market data must be timestamped.

Example:

```text
2026-08
Competitor X → Google position 7

2026-11
Competitor X → Google position 4

2027-02
Competitor X → Google position 2
```

The system can then ask:

```text
What changed?
```

Possible changes:

* content;
* title;
* headings;
* price;
* backlinks;
* reviews;
* structured data;
* page speed;
* product availability;
* images;
* FAQ;
* internal linking.

Snapshots are therefore a fundamental part of the architecture.

---

# 22. SEO Knowledge Engine

SEO should be generated from accumulated product and market knowledge.

```text
PRODUCT KNOWLEDGE
       +
MARKET KNOWLEDGE
       +
SEARCH INTENT
       +
COMPETITOR INTELLIGENCE
       +
M99 STYLE GUIDE
       │
       ▼
SEO ENGINE
```

Possible outputs:

* SEO title;
* meta description;
* H1;
* H2;
* H3;
* product description;
* short description;
* technical description;
* benefits;
* applications;
* FAQ;
* image ALT text;
* image title;
* structured data;
* category links;
* internal links;
* related products;
* comparison content;
* buying guides.

---

# 23. SEO Goal

The goal is not merely to create "SEO text".

The objective is to build the **best available product resource for the user's intent**.

For every important product page, M99 should aim to provide more useful and trustworthy information than large generic marketplaces.

This requires:

```text
Technical accuracy
+
Original knowledge
+
Market relevance
+
Excellent UX
+
Structured information
+
Images
+
Documentation
+
Real experience
+
Continuous improvement
```

No architecture can guarantee a #1 organic position, because rankings are controlled by search engines and competitors continuously change.

The system instead optimizes the factors M99 can control.

---

# 24. Multi-Language Content

Product identity is language-independent.

Content is language-dependent.

```text
M99-PM-000002
│
├── BG
│   └── Bulgarian content
│
├── RO
│   └── Romanian content
│
├── EN
│   └── English content
│
└── DE
    └── future German content
```

Translations should not blindly translate SEO copy.

Each market may require different:

* keywords;
* terminology;
* search intent;
* commercial language;
* category structure;
* FAQ;
* competitors;
* regulations;
* buying concerns.

---

# 25. Channel-Specific Content

Even within one language, channels may have different positioning.

Example:

```text
M99 Product Knowledge
        │
        ├── mela99.com
        │
        ├── rabotni-drehi.com
        │
        └── m99.eu
```

The platform should avoid creating unnecessary duplicate content across owned sites.

Each channel may define:

```text
audience
positioning
SEO strategy
category strategy
content depth
commercial message
canonical strategy
publication status
```

---

# 26. MoneyWork

MoneyWork is currently an operational source system.

Its data is imported through:

```text
MoneyWork
    │
    ▼
 importer.py
    │
    ▼
ExternalProductRecord
```

Example:

```text
source_type: moneywork
source_id: GENSOFT-MONEYWORK
identifier: MW-0001842
```

MoneyWork identifiers remain external mappings.

---

# 27. Dolibarr

Dolibarr is planned as the future operational ERP/CRM platform.

Expected responsibilities include:

* inventory;
* warehouses;
* purchases;
* suppliers;
* sales;
* customers;
* CRM;
* orders;
* deliveries;
* invoicing;
* logistics-related operations.

M99 Knowledge Platform should not duplicate all ERP functionality.

The separation should be:

```text
M99 KNOWLEDGE PLATFORM
        │
        │ identity / knowledge
        ▼
     DOLIBARR
        │
        │ operations
        ▼
Stock / Orders / CRM / Purchasing / Logistics
```

---

# 28. MoneyWork → Dolibarr Migration

Migration must not be:

```text
MoneyWork
    ↓
Dolibarr
    ↓
M99
```

Preferred architecture:

```text
MoneyWork
    │
    ▼
M99 Import / Identity Resolution
    │
    ▼
Confirmed M99 Identity
    │
    ├──────────► Dolibarr
    │
    ├──────────► mela99.com
    │
    ├──────────► m99.eu
    │
    ├──────────► laviro.ro
    │
    └──────────► other channels
```

This prevents legacy ERP identifiers from becoming permanent business identity.

---

# 29. Publishing Engine

Future publishing architecture:

```text
M99 PRODUCT
     │
     ▼
KNOWLEDGE VALIDATION
     │
     ▼
CHANNEL RULES
     │
     ▼
MARKET RULES
     │
     ▼
CONTENT GENERATION
     │
     ▼
SEO VALIDATION
     │
     ▼
OPERATOR REVIEW
     │
     ▼
PUBLISH
```

Possible publishing targets:

```text
mela99.com
rabotni-drehi.com
m99.eu
medicinski-drehi.com
toplinka.com
laviro.ro
alviro.ro
future marketplaces
future websites
```

---

# 30. Publication Status

Products and content should support lifecycle states such as:

```text
DRAFT
RESEARCHING
READY_FOR_REVIEW
APPROVED
READY_TO_PUBLISH
PUBLISHED
PAUSED
ARCHIVED
```

Product identity must remain even when publication is stopped.

Deleting a product from a website must not destroy its accumulated knowledge.

---

# 31. Image Knowledge

Images are part of product knowledge.

The system should store:

* source;
* copyright/licensing status where known;
* manufacturer image ID;
* image type;
* angle;
* color;
* variant;
* resolution;
* background;
* ALT recommendations;
* usage status;
* channel mappings.

Example image roles:

```text
hero
front
side
rear
top
sole
detail
technology
lifestyle
size_chart
technical_diagram
certificate
installation
```

---

# 32. Customer Knowledge

Future customer feedback can improve product knowledge.

Examples:

```text
comfort
fit
durability
weight
temperature
slip resistance
water resistance
maintenance
real sizing
common complaints
common praise
```

Customer statements should not automatically become verified technical facts.

They remain observations until validated.

---

# 33. Sales Knowledge

Salespeople often possess product knowledge that manufacturers do not publish.

The system should capture:

* common customer questions;
* objections;
* preferred alternatives;
* size observations;
* use cases;
* reasons for returns;
* competitor comparisons;
* successful recommendations.

This becomes an internal knowledge layer.

---

# 34. Field Tests

Products may accumulate real operational evidence.

Example:

```text
FIELD TEST
│
├── product
├── variant
├── environment
├── occupation
├── duration
├── conditions
├── observation
├── tester
├── evidence
└── result
```

This information can later improve:

* recommendations;
* product descriptions;
* FAQ;
* comparisons;
* sales training;
* purchasing decisions.

---

# 35. Human Review

AI is an assistant, not the final authority for critical identity decisions.

Human review should exist for:

```text
identity conflicts
supplier mapping conflicts
technical contradictions
certification conflicts
high-risk content
major SEO changes
publication approval
```

Operator decisions should themselves become recorded knowledge.

---

# 36. AI Layer

AI can assist with:

```text
normalization
classification
entity matching
content analysis
competitor analysis
translation
SEO generation
FAQ generation
comparison generation
market summaries
knowledge extraction
anomaly detection
recommendations
```

AI-generated claims should retain provenance where appropriate.

---

# 37. M99 Style Guide

All generated content should follow an M99 Style Guide.

It should control:

* brand voice;
* terminology;
* technical language;
* capitalization;
* units;
* safety wording;
* prohibited claims;
* SEO style;
* product naming;
* category naming;
* translation conventions;
* formatting.

Conceptually:

```text
Knowledge
   +
Market
   +
Channel
   +
M99 Style Guide
   │
   ▼
Content
```

---

# 38. Suggested Repository Structure

```text
m99-knowledge-platform/
│
├── README.md
│
├── requirements.txt
│
├── .env.example
│
├── .gitignore
│
├── config/
│   ├── markets/
│   ├── channels/
│   ├── product_groups/
│   ├── manufacturers/
│   ├── suppliers/
│   └── style_guides/
│
├── core/
│   ├── importer.py
│   ├── normalizer.py
│   ├── resolver.py
│   ├── matcher.py
│   ├── decision.py
│   ├── overrides.py
│   ├── taxonomy.py
│   ├── channel_manager.py
│   ├── market_intelligence.py
│   ├── market_crawler.py
│   ├── evidence.py
│   ├── knowledge_engine.py
│   ├── seo_engine.py
│   ├── content_engine.py
│   ├── document_engine.py
│   └── publishing_engine.py
│
├── integrations/
│   ├── moneywork/
│   ├── dolibarr/
│   ├── manufacturers/
│   ├── suppliers/
│   ├── search/
│   └── websites/
│
├── knowledge/
│   ├── products/
│   ├── categories/
│   ├── brands/
│   ├── manufacturers/
│   ├── standards/
│   └── technologies/
│
├── market/
│   ├── BG/
│   ├── RO/
│   └── ...
│
├── output/
│   ├── market_intelligence/
│   ├── seo/
│   ├── content/
│   ├── documents/
│   └── publishing/
│
├── snapshots/
│
├── tests/
│
└── scripts/
```

---

# 39. Configuration-First Architecture

Business configuration should live outside application logic whenever possible.

Instead of:

```python
if domain == "laviro.ro":
    market = "RO"
```

prefer configuration:

```json
{
  "channel_id": "CH-LAVIRO",
  "domain": "laviro.ro",
  "market_id": "MKT-RO"
}
```

This applies to:

* markets;
* websites;
* product groups;
* languages;
* currencies;
* suppliers;
* competitors;
* manufacturers;
* publishing rules.

---

# 40. Core Data Relationships

Conceptual model:

```text
MARKET
  │
  └── CHANNEL
        │
        └── CHANNEL_PRODUCT_GROUP
                  │
                  ▼
             PRODUCT_GROUP
                  │
                  ▼
               PRODUCT
                  │
             ┌────┴────┐
             │         │
          VARIANT   KNOWLEDGE
             │         │
             │      EVIDENCE
             │
             ├── Manufacturer Mapping
             ├── Supplier Mapping
             ├── MoneyWork Mapping
             ├── Dolibarr Mapping
             └── Channel Mapping
```

Market intelligence attaches to:

```text
PRODUCT + MARKET + TIME
```

SEO/content attaches primarily to:

```text
PRODUCT + MARKET + LANGUAGE + CHANNEL
```

---

# 41. Product Example — PUMA CONDOR MID

Current real development product:

```text
M99-PM-000002
PUMA CONDOR MID S3L ESD
```

This product is useful as an architecture test because source systems may disagree.

An official manufacturer record and supplier records may contain different:

* SKUs;
* naming;
* safety-class wording;
* legacy descriptions.

These differences must not be automatically merged.

They are resolved through:

```text
Evidence
   ↓
Resolver
   ↓
Matcher
   ↓
Decision
   ↓
Operator Review
```

---

# 42. Security and Data Integrity

The platform must protect:

```text
product identity
operator decisions
credentials
API keys
customer data
supplier commercial data
ERP access
publishing credentials
historical evidence
```

Secrets must never be committed to Git.

Use:

```text
.env
```

and commit only:

```text
.env.example
```

where appropriate.

---

# 43. Auditability

Important system actions should eventually be auditable.

Example:

```text
WHO
WHAT
WHEN
WHY
SOURCE
PREVIOUS VALUE
NEW VALUE
```

Especially for:

* identity changes;
* category changes;
* supplier mappings;
* product merges;
* publication;
* price rules;
* technical facts;
* operator overrides.

---

# 44. Product Merge Policy

Two M99 Product Masters must never be merged solely because their names are similar.

Merge decisions should consider:

```text
brand
manufacturer
manufacturer SKU
EAN
model
technical attributes
variants
documentation
supplier mappings
historical records
```

Potential merges require review.

---

# 45. Product Deletion Policy

Prefer:

```text
ARCHIVE
```

over physical deletion.

Why?

Because products may contain valuable:

* sales history;
* customer feedback;
* SEO history;
* supplier mappings;
* market observations;
* technical documentation;
* previous URLs.

Knowledge should survive the commercial lifecycle.

---

# 46. SEO History

SEO should also be versioned.

Example:

```text
2026-08-08
Title v1
H1 v1
Description v1

2026-10-15
Title v2
H1 v1
Description v2
```

This allows later comparison against:

```text
rankings
CTR
traffic
conversion
revenue
```

and creates an internal SEO learning system.

---

# 47. Closed Learning Loop

Long-term architecture:

```text
PRODUCT KNOWLEDGE
       │
       ▼
CONTENT
       │
       ▼
PUBLISH
       │
       ▼
SEARCH / TRAFFIC
       │
       ▼
SALES
       │
       ▼
CUSTOMER EXPERIENCE
       │
       ▼
MARKET INTELLIGENCE
       │
       ▼
LEARNING
       │
       └──────────────► PRODUCT KNOWLEDGE
```

This is the central strategic advantage of the platform.

The objective is not simply automation.

The objective is **cumulative organizational knowledge**.

---

# 48. Development Roadmap

## Phase 1 — Foundation

* Product Master;
* Product Variant;
* ExternalProductRecord;
* MoneyWork importer;
* normalization;
* resolver;
* matcher;
* decision engine;
* overrides;
* evidence model.

## Phase 2 — Catalog Architecture

* markets configuration;
* channels configuration;
* dynamic product groups;
* taxonomy;
* channel/product-group mappings;
* product/channel mappings.

## Phase 3 — Product Knowledge

* specifications;
* materials;
* technologies;
* standards;
* certifications;
* applications;
* images;
* manufacturer evidence;
* supplier evidence.

## Phase 4 — Market Intelligence

* `market_intelligence.py`;
* `market_crawler.py`;
* search discovery;
* competitor discovery;
* competitor product matching;
* SERP observations;
* price observations;
* historical snapshots.

## Phase 5 — SEO & Content

* search intent;
* keyword architecture;
* competitor content analysis;
* SEO scoring;
* content scoring;
* content generation;
* structured data;
* internal linking recommendations;
* channel differentiation.

## Phase 6 — Documents

* Product Knowledge PDF;
* Technical Dossier;
* Market Intelligence PDF;
* SEO Strategy PDF;
* versioned document generation.

## Phase 7 — Dolibarr

* Dolibarr connector;
* M99 ↔ Dolibarr mappings;
* product synchronization;
* variants;
* inventory mappings;
* supplier mappings;
* migration from MoneyWork.

## Phase 8 — Publishing

* mela99.com;
* rabotni-drehi.com;
* m99.eu;
* medicinski-drehi.com;
* toplinka.com;
* laviro.ro;
* alviro.ro.

## Phase 9 — Learning System

* customer feedback;
* salesperson knowledge;
* returns;
* product performance;
* field tests;
* SEO performance;
* sales performance;
* automated learning recommendations.

---

# 49. Immediate Development Priority

The architecture should now be stabilized before adding large amounts of scraping or generated content.

Recommended next implementation order:

```text
1. Move MARKETS out of market_intelligence.py
          ↓
2. Create market configuration
          ↓
3. Create channel configuration
          ↓
4. Create ProductGroup model
          ↓
5. Create ChannelProductGroup mapping
          ↓
6. Update Product Master schema
          ↓
7. Update Market Intelligence Engine
          ↓
8. Build market_crawler.py
          ↓
9. Test with M99-PM-000002
          ↓
10. Add Dolibarr integration
```

This prevents future modules from being built on hardcoded assumptions.

---

# 50. Initial Configuration Files

Recommended first configuration set:

```text
config/
├── markets/
│   ├── BG.json
│   └── RO.json
│
├── channels/
│   ├── mela99.com.json
│   ├── rabotni-drehi.com.json
│   ├── m99.eu.json
│   ├── medicinski-drehi.com.json
│   ├── toplinka.com.json
│   ├── laviro.ro.json
│   └── alviro.ro.json
│
└── product_groups/
    ├── workwear.json
    ├── safety-footwear.json
    ├── ppe.json
    ├── medical-clothing.json
    ├── medical-footwear.json
    ├── hand-hygiene.json
    ├── tools.json
    ├── boilers.json
    ├── fireplaces.json
    ├── heat-pumps.json
    ├── water-heaters.json
    ├── buffer-tanks.json
    ├── radiators.json
    ├── photovoltaic-panels.json
    ├── photovoltaic-inverters.json
    ├── photovoltaic-batteries.json
    └── installation-services.json
```

---

# 51. Design Rules

All future development should follow these rules.

### Rule 1

**M99 owns product identity.**

### Rule 2

External IDs are mappings, not M99 identity.

### Rule 3

Product knowledge and market knowledge are separate but connected.

### Rule 4

A website is a channel, not a market.

### Rule 5

Product groups are dynamic.

### Rule 6

Adding a market must not require rewriting the engine.

### Rule 7

Adding a website must not require redesigning product identity.

### Rule 8

Removing a product from a channel must not delete its knowledge.

### Rule 9

Evidence must be traceable.

### Rule 10

Competitor content is research evidence, not source text to copy.

### Rule 11

AI recommendations must not silently overwrite verified facts.

### Rule 12

Historical snapshots must be preserved.

### Rule 13

ERP systems operate the business but do not own M99 knowledge.

### Rule 14

SEO is market-specific and channel-aware.

### Rule 15

The system must learn over time.

---

# 52. Definition of M99 Knowledge Platform

The project can be summarized as:

> **M99 Knowledge Platform is the central product identity, knowledge, market intelligence, SEO and publishing layer connecting manufacturers, suppliers, ERP systems, markets and digital sales channels across the M99 ecosystem.**

Its purpose is to transform fragmented product data into a continuously improving business knowledge system.

The long-term flow is:

```text
DATA
  ↓
IDENTITY
  ↓
EVIDENCE
  ↓
KNOWLEDGE
  ↓
MARKET INTELLIGENCE
  ↓
CONTENT
  ↓
PUBLISHING
  ↓
SALES
  ↓
EXPERIENCE
  ↓
LEARNING
  ↓
BETTER KNOWLEDGE
```

---

# 53. Current Status

Current proven / started components:

```text
✓ M99 Product identity concept
✓ Product Master concept
✓ Product Variant concept
✓ MoneyWork ExternalProductRecord
✓ Importer v0.1
✓ Resolver / Matcher / Decision architecture
✓ PUMA real-product test
✓ M99-PM-000002 knowledge package concept
✓ Manufacturer evidence
✓ Supplier evidence
✓ Competitor evidence
✓ Market Intelligence Engine v0.1
✓ Romania/Bulgaria market concept
✓ Historical snapshot concept
✓ SEO Knowledge architecture
✓ PDF Knowledge architecture
```

Architecture requiring implementation next:

```text
→ Configuration-driven Markets
→ Channel Registry
→ Dynamic Product Groups
→ Channel/Product Group mappings
→ Universal taxonomy
→ Market Crawler
→ Automated competitor discovery
→ Automated evidence collection
→ Dolibarr integration
→ Publishing Engine
```

---

# 54. Next Milestone

## M99 Knowledge Platform v0.2 — Catalog Architecture

The next milestone should establish:

```text
config/markets
config/channels
config/product_groups

        +

Market Registry
Channel Registry
Product Group Registry

        +

Channel ↔ Market
Channel ↔ Product Group
Product ↔ Product Group
Product ↔ Channel
```

After this milestone, the platform will understand:

> **what the product is, where it can be sold, in which market it is being sold, on which website it appears, and which market intelligence must be collected for it.**

Only after this foundation is stable should automated crawling and publishing become the primary development focus.

---

**M99 Knowledge Platform**
**Master Architecture README — v1.0**
**Status: Active Development**

