# M99 Knowledge Platform — README v6

> **Master System Constitution / Consolidated Project Specification**  
> **Статус:** нормативен master документ / активна разработка  
> **Консолидирано:** README v1-v5 + решенията до 19.08.2026 г.  
> **Repository:** `M99-Knowledge-Platform`

---

## 0. Роля на README v6

README v6 не отменя валидните решения от README v1-v5. Той ги консолидира и добавя решенията за новата Admin Platform: Operator/Super Admin разделение, operator-first UX, permanent identity, Organization/Brand Registry, B2B connectors, Central Logs, Existing Product/Category Content Revision и Knowledge/Evidence Sources.

Статуси: `DECIDED`, `DECIDED/TESTED`, `IMPLEMENTED`, `FOUNDATION`, `PLANNED`, `OPEN`, `DEFERRED`.

**Anti-loop:** `DECIDED ≠ IMPLEMENTED`. Липсата на завършен код не връща вече решено правило в `OPEN`.

## 1. Визия и core principles

M99 Knowledge Platform е централният knowledge, product, commercial, operational и customer intelligence слой на M99 Group.

1. **Single Source of Truth** — canonical фактът се пази веднъж.
2. **Knowledge First** — verified knowledge преди content/publishing.
3. **No Duplicate Data** — materials, technologies, standards, organizations и brands са reusable entities.
4. **Evidence Based** — exact manufacturer > official docs/catalogues/certificates > validated B2B > exact supplier > verified internal data > operator > AI.
5. **AI Native, not AI Invented** — AI не измисля standards, stock, EAN/GTIN, MPN, materials или certifications.

## 2. Два основни профила

### OPERATOR

Операторът не трябва да знае Python, PowerShell, API, HTTP, JSON, SQL или platform internals.

```text
Табло
Добави продукти
Моите задачи
Продукти
Къде се продават
Цени и наличности
Проблеми за проверка
История
```

**OPERATOR-FIRST RULE:** M99 води оператора стъпка по стъпка.

**ONE-DECISION-PER-SCREEN RULE:** на всеки екран се показва основно решението, което операторът трябва да вземе.

### SUPER ADMIN

Super Admin управлява Users/Roles, Organizations, Manufacturers, Suppliers, Brands, B2B Portals, Knowledge Sources, Channels/ERP, Languages, Pricing/VAT/FX, Identity Registry, Import Presets, Sync Rules, Content Revision Policies, Locked Fields Policy, Quality Gates, Credentials Status, Audit/Logs/Diagnostics и Feature/Gap Registry.

## 3. Authentication / RBAC / Security

Login чрез username или email + password. Изисквания: secure password hashing, sessions/logout, timeout, failed-login throttling/lockout, reset-password workflow, login/logout audit, future 2FA. Operators never see channel/B2B credentials. No passwords/API keys/tokens/cookies in Git, logs or screenshots.

## 4. Organization Model

Supplier и Manufacturer не са взаимно изключващи се master entities.

```text
Organization
├── Roles
│   ├── SUPPLIER
│   ├── MANUFACTURER
│   └── future roles
├── Brands
├── Public Websites
├── B2B Portals
├── APIs
├── Feeds
├── Catalogues
└── Documents
```

**MULTI-ROLE ORGANIZATION RULE:** една Organization може едновременно да е `SUPPLIER` и `MANUFACTURER`.

Примери: STENSO и PALLTEX могат да бъдат едновременно Supplier и Manufacturer.

Operator може да предложи нов Manufacturer/Supplier, но статусът е `PENDING_SUPER_ADMIN_APPROVAL`. Само Super Admin може да `APPROVE`, `REJECT`, `MERGE_WITH_EXISTING` или `ACTIVATE_ROLE`.

## 5. Brand Registry

Brand е отделен canonical object с Brand ID, Name, Owner Organization, Manufacturer Organization(s), Official Website, Logos, Catalogues и Knowledge Sources. Operator може да предложи Brand; само Super Admin го одобрява.

## 6. B2B Portals

B2B portal принадлежи към **Organization**, а не само към Supplier. Manufacturer, Supplier или multi-role Organization може да има един или повече B2B portals.

```text
Organization
├── Public Website
├── B2B Portal A
├── B2B Portal B
├── API
├── CSV/XLSX/XML/JSON Feed
└── Documents
```

Всеки connector декларира capabilities: `IDENTITY`, `TECHNICAL_FACTS`, `MPN`, `EAN_GTIN`, `IMAGES`, `DOCUMENTS`, `CATALOGUES`, `PRICE`, `PURCHASE_PRICE`, `AVAILABILITY`, `LEAD_TIME`, `VARIANTS`, `STOCK`, `ORDER_TERMS`.

B2B states: `NOT_CONFIGURED / CREDENTIALS_REQUIRED / CONNECTED / READY / AUTH_FAILED / SESSION_EXPIRED / BLOCKED / VERIFICATION_FAILED`.

## 7. Knowledge / Evidence Sources

Supported source classes: `PUBLIC_WEBSITE`, `B2B_PORTAL`, `API`, `CSV`, `XLSX`, `XML`, `JSON`, `PDF_CATALOGUE`, `TECHNICAL_DOCUMENT`, `CERTIFICATE`, `PRICE_LIST`, `STOCK_FEED`, `SIZE_CHART`, `IMAGE_LIBRARY`, `MANUAL_VERIFIED_SOURCE`.

Manufacturer/Supplier files могат да се добавят като current evidence.

```text
Upload
→ File Inspection
→ Field Mapping
→ Identity Matching
→ Evidence Extraction
→ Conflict Detection
→ Review
→ Current Observation
```

Нов файл не презаписва canonical truth автоматично. Source lifecycle: `UPLOADED → IDENTIFIED → VERIFIED_SOURCE → CURRENT → SUPERSEDED → ARCHIVED`.

## 8. Technical Search / Provenance

Global Search търси по Product Name, M99 Reference, Supplier Reference, Manufacturer Reference/MPN, EAN/GTIN, Brand, Model, Material, Technology, Standard, Certification, Size, Colour, Supplier, Manufacturer, Catalogue, Document и B2B source.

Всеки важен факт пази provenance: source, observed_at, verified_at, document/page когато е налично, reviewer и conflict state.

## 9. Canonical Product / Identity

```text
ProductGroup
├── Permanent M99 Identity
├── Brand
├── Manufacturer
├── MPN / Manufacturer Ref
├── EAN/GTIN
├── Supplier Mappings
├── Evidence
├── Facts
├── Assets
├── Channel Mappings
└── Variants
```

Lifecycle: `draft → active → paused → retired`. Physical DELETE — само след operator approval + explicit typed `DELETE`.

M99 Reference: `M99-` + digits only. Identity е независима от supplier ref, manufacturer SKU, EAN, channel ID, Dolibarr ID, legacy ref, title или URL.

**Identity Before Content:** `SELECT → RESOLVE IDENTITY → LINK EXISTING or CREATE PERMANENT M99 ID → THEN CONTENT`.

Duplicate states: `NEW / EXISTING / AMBIGUOUS / UNRESOLVED`. `AMBIGUOUS` изисква human decision.

## 10. Variants / Default Combination / Stock

Размерите са variants, когато product logic не налага друго. Visible size ≠ stock. Supplier availability ≠ M99/Dolibarr physical stock.

Variational product трябва да има точно една default combination и `cache_default_attribute` трябва да сочи към нея. Failure блокира Quality PASS.

## 11. Images

Source priority: official manufacturer → verified supplier → verified cached original source. Друг M99 channel не е master image source.

Pipeline: `Discover → Verify → Download → Relevance → Dedupe → Resize ~1200–1400 → WebP → Localized ALT → Operator Review → Upload → Readback`.

## 12. Content / SEO / Languages

Complete product package: Product Name, H1, short description, long description, H2/H3, technical specifications, materials, sizes, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links, images и localized ALT.

Channel prose се адаптира по market/language. Supplier prose не се копира verbatim. Language Registry е dynamic: BG, EN, RU, RO, GR + future languages.

## 13. Field-Level Review

За всяко content field и required language: `GENERATED → EDITED → SAVED → REVIEWED → APPROVED`.

Operator може да редактира и записва всяко поле поотделно. Промяна след approval инвалидира само approval-а на засегнатото поле. Image + ALT се преглеждат заедно за всеки language.

## 14. New Product Operator Workflow

```text
1. Избери доставчик
2. Избери директно product(s)/category(ies) от supplier source
3. Identity / Duplicate Review
4. Target Channels / ERP
5. M99 подготвя product data
6. Content + SEO + Image ALT Review
7. Final Confirmation
8. TEST / Draft Import
9. Readback
10. Quality Report
11. Activation according to permission
```

Target UX **не използва URL copy/paste** като основен операторски процес.

New product scope: `WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`.

## 15. ImportJob / Presets

Всеки new-product import е auditable `ImportJob`.

Preset `MEDICINSKI / STENSO`: Source Stenso, Target medicinski-drehi.com, Mode New Product Import, Initial state TEST/Draft.

Preset `PALLTEX / ALL CHANNELS + ERP`: Source Palltex, enabled web channels + Dolibarr, channel pricing policy и standard-market VAT. Preset не може да разширява permissions.

## 16. Existing Product Daily Sync

Daily checks: supplier/B2B price, availability, variants/sizes, product changes, discontinuation.

Results: `NO_CHANGE / PRICE_CHANGED / AVAILABILITY_CHANGED / VARIANT_AVAILABILITY_CHANGED / PRODUCT_CHANGED / SUPPLIER_DISCONTINUED / VERIFICATION_FAILED`.

**NO_CHANGE → NO_WRITE**. Daily sync обновява само already-existing mappings и не създава product в missing channel.

## 17. Product Presence

Presence != Stock.

Presence states: `NOT_PRESENT / PRESENT_DRAFT / PRESENT_TEST / PRESENT_ACTIVE / PRESENT_PAUSED / PRESENT_RETIRED / PRESENT_LAST_VERIFIED / UNKNOWN / VERIFICATION_FAILED`.

Product Presence UI показва target, presence, publication, channel product ID, stock, price, last verified, last sync и errors. Modes: `FAST` и `LIVE VERIFY`.

## 18. Pricing + VAT

Target selling price е крайна клиентска **gross / VAT-included** цена. Standard VAT е channel/market configuration, не hardcoded constant. Back Office/API price alone не е sufficient. След write се изисква readback и Front Office gross-price verification, когато е приложимо.

## 19. Existing Product Content Revision

Отделен operational class. Може да се избира one product, multiple products, category, brand, products with weak SEO или incomplete content.

Locked при normal revision: `M99 ID`, `Product Name`, `URL / slug`, `Channel Product ID`.

Editable: short/long descriptions, H2/H3, technical specifications, materials, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links, image ALT. Identity migration е отделна Super Admin operation.

## 20. Existing Category Content Revision

Категориите следват същия controlled-review принцип. Може да се избира one category, multiple categories, category + subcategories или all categories in selected channel.

Locked: `M99 Category ID`, `Channel Category ID`, `Existing Category Name`, `Existing URL / slug`, `Parent relationship`.

Editable: short description, long description, SEO content, Meta Title, Meta Description, FAQ, H2/H3, internal links, category image ALT, structured data. Structural migration е отделен Super Admin process.

## 21. Content Revision Workflow

`Select entity/entities → Select channels → Load current content → Load verified evidence → Generate proposed revision → CURRENT vs PROPOSED → Operator edits every field/language → Save → Review → Approve → Controlled UPDATE → Readback → Quality Report`.

## 22. Central Logs — Super Admin

Минимум:
1. **Audit Log** — кой user какво е направил.
2. **System Log** — какво е направила системата.
3. **Supplier/B2B & Channel Integration Logs** — connector operations.
4. **Security Log** — login/logout/failures/lockout/security events.

Minimum fields: `timestamp, severity, user, module, operation, entity, supplier/channel, job_id, result, message, correlation_id`.

Never log secret values.

## 23. Publishing Constitution

1. NEW → TEST/Draft first.
2. TEST category resolved live.
3. Final category operator-owned.
4. Existing name + URL locked.
5. Approved M99 name + URL locked.
6. Unapproved TEST draft may be repaired.
7. CREATE != UPDATE.
8. Duplicate guard before CREATE.
9. Mandatory readback.
10. HTTP 200/201 != Quality PASS.
11. Front Office verification where applicable.
12. Activation requires authorization.
13. DELETE remains explicit human action.

## 24. Product Quality Gate

Critical areas: `IDENTITY / MANUFACTURER_EVIDENCE / SUPPLIER_MATCH / PRICE / VAT / CURRENCY / LANGUAGES / CONTENT / SEO / TECHNICAL_FACTS / IMAGES / ALT / VARIANTS / DEFAULT_COMBINATION / TEST_DRAFT / READBACK / FRONT_OFFICE / NO_INVENTED_CLAIMS / NO_UNVERIFIED_STOCK`.

Numeric score cannot override a failed critical gate.

## 25. Dolibarr / Migration / CRM

M99 = canonical truth. Dolibarr = operational ERP/CRM/warehouse representation.

Supplier order → reception → physical stock increase. Customer order → shipment → physical stock decrease. Stock is variant-aware.

MoneyWork/site migration: `Inspect → Normalize → Deduplicate → Identity Map → Supplier/Customer Map → Dry Run → Import → Reconcile → Audit`.

CRM foundation: `Първо обаждане → Оферта → Второ обаждане`. Customer 360 remains planned after product platform stabilization.

## 26. Operational Classes

```text
A. NEW PRODUCT IMPORT
B. EXISTING PRODUCT DAILY SYNC
C. MANUAL / EXCEPTIONAL REPAIR
D. EXISTING PRODUCT CONTENT REVISION
E. EXISTING CATEGORY CONTENT REVISION
F. KNOWLEDGE / EVIDENCE ACQUISITION
```

## 27. Feature / Gap Registry

Всеки significant feature има два independent statuses: `normative_status` и `implementation_status`. Това е постоянният anti-loop механизъм.

## 28. Decisions fixed — do not reopen

- Operator-first UX.
- Operator vs Super Admin split.
- Identity Before Content.
- Permanent numeric M99 ID; no reuse.
- Supplier/Manufacturer are Organization roles; one Organization may have both.
- New organizations and brands require Super Admin approval.
- Manufacturer and Supplier organizations may both have B2B portals.
- B2B connector declares capabilities.
- Direct Supplier Selection is target UX.
- New Product target scope is selective.
- Existing products sync daily; NO_CHANGE → NO_WRITE.
- Presence != Stock.
- Existing Product Name + URL locked during content revision.
- Existing Category Name + URL locked during content revision.
- Product and Category content can be revised.
- Every field is reviewed per language; Image + ALT together.
- CSV/XLSX/XML/JSON/PDF/API/catalogues can be evidence sources.
- Technical search includes Manufacturer/Supplier knowledge.
- Central logs accessible to Super Admin.
- New products publish TEST/Draft first.
- Target selling price is VAT-included gross.
- Exactly one default combination.

## 29. Open / Deferred

Remain genuinely OPEN/DEFERRED: universal ProductGroup vs colour-variant boundary; universal Variant SKU standard; exact Dolibarr parent/variant implementation; exact image-rights contract per external source; production Vault deployment; exact WordPress commerce adapter details per site; 2FA rollout timing; final technical mechanism for direct supplier browser selection.

## 30. Next implementation priority

Build one complete operator workflow end-to-end before adding more isolated technical screens:

`Login → Add Products → Choose Supplier → Direct Supplier Selection → Identity → Permanent M99 ID / Existing Match → Targets → Prepare Product → Content/SEO/Image ALT Review → Operator Approval → TEST/Draft → Readback → Quality Report`.

Parallel Super Admin priorities: Organization/Brand Registry, B2B Connectors, Knowledge Sources, Central Logs, Existing Product Content Revision, Existing Category Content Revision и Daily Sync.

## 31. Repository Governance

```text
README.md
README_v2.md
README_v3.md
README_v4.md
README_v5.md
README_v6.md

docs/history/README_v1.md
...
docs/history/README_v6.md
```

`README.md` не се презаписва автоматично. Ако v6 трябва да стане landing README, това е отделно operator-approved действие.

## 32. Final Architecture Philosophy

```text
KNOWLEDGE
+ EVIDENCE
+ IDENTITY
+ ORGANIZATIONS
+ BRANDS
+ B2B
+ COMMERCIAL INTELLIGENCE
+ CONTENT
+ ERP / CRM
+ MULTI-CHANNEL PUBLISHING
+ DAILY SYNC
+ AUDIT / LOGS
+ HUMAN GOVERNANCE
```

**M99 Knowledge Platform — README v6 — Product truth once. Customer truth once. Verified everywhere. Governed by humans.**
