# M99 Knowledge Platform — README v8

> **Master System Constitution / Consolidated Project Specification / Current Development State**  
> **Status:** normative master document / active development  
> **Consolidated:** README v1-v7 + M99 v0.7.2 decisions and implementation evidence through 2026-08-21  
> **Repository:** `M99-Knowledge-Platform`  
> **Current development line:** `v0.7.2`  
> **Latest Phase 3 Fix 1 commit created:** `ec0cc276bdf235868f74df52aaf62c6421d3b32d`

---


## 0. Role of README v8

README v8 is the next consolidated Master System Constitution and Current Development State for M99 Knowledge Platform. It inherits all still-valid decisions from README v1-v7 and adds the decisions and implementation evidence accumulated through 21 August 2026.

The governing rule is anti-loop: DECIDED is not the same as IMPLEMENTED. A missing implementation, failed experiment, or temporary integration defect does not reopen a previously accepted architectural decision. A decision is reopened only by an explicit superseding decision with recorded rationale.

README v8 is both a human-readable master map and a bridge toward machine-readable project governance.


## 1. Vision and purpose

M99 Knowledge Platform is the central identity, product knowledge, supplier/manufacturer knowledge, commercial intelligence, content, SEO, publishing, integration and governance layer for the M99 ecosystem.

M99 is the Single Source of Truth for canonical identity and verified product knowledge. External systems are sources, channels, destinations or operational systems. They do not own canonical M99 identity.

Core principles:
- Single Source of Truth.
- Knowledge First.
- No Duplicate Data.
- Evidence Based.
- AI Native, not AI Invented.
- Historical observations are preserved.
- Market and Channel are separate concepts.
- ERP operates the business but does not own M99 knowledge.
- Product knowledge survives removal from any individual channel.


## 2. Current canonical data model direction

The canonical chain is:

ProductGroup → ProductVariant → SupplierOffer → Evidence → ChannelPresence → ChannelContent → ChannelPrice → InventoryMapping

External identifiers such as supplier SKU, manufacturer reference/MPN, EAN/GTIN, MoneyWork code, Dolibarr ID, website ID and marketplace ID are mappings to M99 entities.

Identity resolution is controlled:

External Record → Import → Normalize → Resolve → Match → Decision → Overrides → Operator Review → Final M99 Identity

Uncertain records must never silently change canonical identity.


## 3. ProductGroup governance and M99 identity

ProductGroup lifecycle is fixed:

draft → active → paused → retired

Hard deletion remains possible only as an exceptional governed action after explicit operator approval and typed confirmation DELETE, with audit logging.

M99 Reference is fixed and tested:

M99- + digits only

The M99 identity is independent from supplier reference, manufacturer SKU/MPN, EAN/GTIN, MoneyWork code, Dolibarr ID, channel product ID, title and URL. Assigned M99 identity is not reused for another ProductGroup.

Identity Before Content:

SELECT → RESOLVE IDENTITY → LINK EXISTING or CREATE PERMANENT M99 ID → THEN CONTENT

Duplicate states:
NEW / EXISTING / AMBIGUOUS / UNRESOLVED

AMBIGUOUS requires a human decision.


## 4. Organization, supplier, manufacturer and brand model

Supplier and Manufacturer are Organization roles, not mutually exclusive master entities. One Organization may simultaneously have SUPPLIER and MANUFACTURER roles and may own brands, public websites, B2B portals, APIs, feeds, catalogues and documents.

An operator may propose a new Supplier, Manufacturer or Brand. The proposed object is not made generally available to operators immediately. It enters PENDING_SUPER_ADMIN_APPROVAL.

Only Super Admin can APPROVE, REJECT, MERGE_WITH_EXISTING or ACTIVATE_ROLE. After approval, the organization/brand becomes available according to permissions.

Brand is a separate canonical object with Brand ID, name, owner organization, manufacturer organization(s), official website, logos, catalogues and knowledge sources.


## 5. B2B connectors and evidence sources

A B2B portal belongs to an Organization. Supplier, Manufacturer or multi-role Organization may have one or more B2B portals.

Each connector declares capabilities such as:
IDENTITY, TECHNICAL_FACTS, MPN, EAN_GTIN, IMAGES, DOCUMENTS, CATALOGUES, PRICE, PURCHASE_PRICE, AVAILABILITY, LEAD_TIME, VARIANTS, STOCK, ORDER_TERMS.

B2B states:
NOT_CONFIGURED / CREDENTIALS_REQUIRED / CONNECTED / READY / AUTH_FAILED / SESSION_EXPIRED / BLOCKED / VERIFICATION_FAILED

Supported evidence/source classes include:
PUBLIC_WEBSITE, B2B_PORTAL, API, CSV, XLSX, XML, JSON, PDF_CATALOGUE, TECHNICAL_DOCUMENT, CERTIFICATE, PRICE_LIST, STOCK_FEED, SIZE_CHART, IMAGE_LIBRARY, MANUAL_VERIFIED_SOURCE.

Evidence priority:
exact official manufacturer → official documentation/catalogue/certificate → validated B2B → exact supplier → verified internal/legacy data → operator → AI over verified data.

New source observations do not automatically overwrite canonical truth.


## 6. Operator and Super Admin profiles

OPERATOR is a business user, not a programmer. The operator must not need to understand Python, PowerShell, API, HTTP, JSON, XML, SQL, credentials or platform internals.

Operator-first UX is fixed. M99 guides the operator step by step. One-decision-per-screen is the target rule.

Primary operator navigation:
Dashboard
Add Products
My Tasks
Products
Where They Are Sold
Prices and Availability
Problems to Review
History

SUPER ADMIN manages:
Users/Roles, Organizations, Suppliers, Manufacturers, Brands, B2B Portals, Knowledge Sources, Channels/ERP, Languages, Pricing/VAT/FX, Identity Registry, Import Presets, Sync Rules, Content Revision Policies, Locked Fields, Quality Gates, Credential Status, Audit/Logs/Diagnostics and Feature/Gap Registry.


## 7. New Product Operator Workflow — fixed target UX

The operator workflow is not a button dedicated to one site. m99.eu is one selectable target among authorized channels.

Target end-to-end workflow:

Login
→ Add Products
→ Choose Supplier
→ Direct Supplier Selection
→ Identity / Duplicate Review
→ Permanent M99 ID or Existing Match
→ Choose Target Channels / ERP
→ Prepare Product
→ Pricing / VAT
→ Content / SEO / Languages
→ Images + localized ALT
→ Variants + Default Combination
→ Preflight
→ Operator Confirmation
→ TEST / Draft Import
→ Readback
→ Quality Report
→ Activation according to permission

The main operator flow must not rely on copying/pasting URLs or launching BAT/Python scripts.


## 8. Product and category selection scope

Direct Supplier Selection must support:
- one exact supplier product;
- multiple selected products;
- one supplier category;
- multiple supplier categories;
- all products from a selected category or source where supported;
- first N products (for example 10 or 20);
- only products new to M99;
- manual selection.

The architecture must support 1, 2, 3, 20, 200 or all selected products through the same engine, without product-specific code.

Selection never bypasses:
identity resolution, evidence verification, duplicate/legacy matching, authorization, target scope, pricing/VAT, image gate, variants/default combination gate, language/content gate, TEST/Draft policy, readback or Product Quality Gate.


## 9. Target channel selection and multi-channel publishing

Operators choose one or more authorized destinations for each ImportJob. The system computes:

WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY

An operator may select one website, several websites, all authorized websites, and/or ERP where the workflow permits it. A blocked target is visible and diagnosable; a READY target may continue according to the publishing contract.

Current channel scope includes:
mela99.com
rabotni-drehi.com
m99.eu
medicinski-drehi.com
toplinka.com
laviro.ro
alviro.ro

Channels are configuration-driven targets; M99 product identity does not change when a channel is added or removed.


## 10. ImportJob and presets

Every new-product import is an auditable ImportJob.

Minimum conceptual fields include:
job_id, created_at, created_by, operator_role,
source_id, source_type, source_urls, source_categories,
selected_products, product_count,
requested_targets, authorized_targets, ready_targets, blocked_targets,
pricing_policy, content_policy, image_policy, language_policy,
dry_run, requires_confirmation, status, started_at, finished_at,
result_per_product, result_per_target, audit_log.

Presets simplify recurring work but never grant permissions the user does not already have.

Examples:
MEDICINSKI / STENSO
PALLTEX / ALL CHANNELS + ERP


## 11. Publishing Constitution

The publishing constitution remains mandatory:
1. NEW → TEST/Draft first.
2. TEST category is resolved live.
3. Final category is operator-owned.
4. Existing approved name + URL are locked in normal revision.
5. Approved M99 name + URL are locked.
6. Unapproved TEST drafts may be repaired.
7. CREATE and UPDATE are different contracts.
8. Duplicate guard runs before CREATE.
9. Readback is mandatory.
10. HTTP 200/201 is not Product Quality PASS.
11. Front Office verification is required where applicable.
12. Activation requires authorization.
13. DELETE remains an explicit human action.

Publishing should be initiated from the M99 Admin workflow, while command-line tools remain diagnostic/development tools.


## 12. Content, SEO and language governance

A complete product package may contain:
Product Name, H1, short description, long description, H2/H3, technical specifications, materials, sizes, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links, images and localized ALT.

Supplier prose is not copied verbatim. Content is adapted for each market, channel and language from verified facts.

Language Registry is dynamic. Known language scope includes BG, EN, RU, RO, GR and future languages. Channel language IDs are discovered live rather than assumed.

Every content field and required language follows:
GENERATED → EDITED → SAVED → REVIEWED → APPROVED

Operator may edit fields individually. A post-approval edit invalidates only the affected field's approval. Image + ALT are reviewed together per language.


## 13. m99.eu current verified integration state

m99.eu runs PrestaShop 9.1.5.

The classic PrestaShop Webservice endpoint is operational for the current integration:
https://m99.eu/api

Verified current m99.eu language mapping:
1 = English (en / en-US)
2 = Bulgarian (bg / bg-BG)
3 = Russian (ru / ru-RU)

All three languages are active.

The controlled test category currently used by the integration is ID 26.

Preflight has verified products GET and POST permissions. Dry Run successfully produced a minimal multilingual payload with:
- numeric-only M99 reference;
- category 26;
- active = 0;
- available_for_order = 0;
- visibility = none;
- EN/BG/RU localized name, slug, descriptions and meta fields;
- category-only associations;
- no empty image/combination/stock placeholder associations.

This proves the m99.eu adapter contract, but the target operator UX is multi-channel and must not be reduced to a dedicated 'Add to m99.eu' screen.


## 14. Current v0.7.2 implementation progress

v0.7.2 development has progressed beyond the v0.7.1 stable baseline.

Completed/verified milestones include:
- Phase 1 — Canonical Data Model Foundation. Commit created: 193b6bcc6c8f4b13439102a99f00d1b542b1851f.
- Phase 2 — SQLAlchemy Persistence + Alembic Migration Baseline. Persistence and temporary migration gates passed; real Admin DB was intentionally not migrated by the installer.
- Phase 2.5 — m99.eu API Preflight & Sandbox Publisher, corrected from an initial wrong WooCommerce assumption to PrestaShop 9.
- Revision 5.1 — Python import-path correction and successful real PrestaShop preflight.
- Revision 5.2 Fix 1 — minimal multilingual payload and legacy-test alignment. Commit: 5705bff675224748f95f58cbf5860b0bb761f972.
- Phase 3 Fix 1 — Admin UI bridge to m99.eu publisher and Python 3.14 import-test compatibility. Full regression suite PASS. Commit: ec0cc276bdf235868f74df52aaf62c6421d3b32d.

Important correction: the Phase 3 dedicated m99.eu screen is treated as a technical prototype/adapter proof, not the final operator workflow. The final UI must implement the generalized Add Products wizard described in this document.


## 15. Admin Platform direction

The Admin Platform is the intended operator surface. It is based on a familiar commerce/PrestaShop-like visual language but must remain simpler than a technical Back Office.

The Admin UI must:
- hide API internals and credentials from operators;
- show business decisions, not transport details;
- use progressive wizard steps;
- show READY / BLOCKED / NEEDS REVIEW states in plain language;
- support one or many products/categories and one or many targets;
- keep diagnostics for Super Admin;
- reuse the same tested service/publisher layer rather than duplicating publishing logic in UI code.


## 16. Product Presence and daily sync

Presence is not stock.

Presence states:
NOT_PRESENT / PRESENT_DRAFT / PRESENT_TEST / PRESENT_ACTIVE / PRESENT_PAUSED / PRESENT_RETIRED / PRESENT_LAST_VERIFIED / UNKNOWN / VERIFICATION_FAILED

Product Presence UI should show target, publication state, channel product ID, stock, price, last verified, last sync and errors, with FAST and LIVE VERIFY modes.

Existing product daily sync checks supplier/B2B price, availability, variants/sizes, product changes and discontinuation.

NO_CHANGE → NO_WRITE.

Daily sync updates only already-existing mappings and does not create a missing channel product automatically.


## 17. Pricing, VAT, variants and stock

Target selling price is customer-facing gross / VAT-included price. Standard VAT is channel/market configuration, not a hardcoded universal constant.

Back Office/API price alone is not sufficient. Readback and Front Office gross-price verification are required where applicable.

Sizes are variants when product logic requires them. Visible size is not stock. Supplier availability is not M99/Dolibarr physical stock.

A variational product must have exactly one default combination and cache_default_attribute must point to it. Failure blocks Product Quality PASS.

Dolibarr remains the operational stock/warehouse layer:
Supplier order → reception → physical stock increase.
Customer order → shipment → physical stock decrease.
Stock is variant-aware.


## 18. Images

Image source priority:
official manufacturer → verified supplier → verified cached original source.

Another M99 channel is not the master image source merely because it already contains the correct image.

Pipeline:
Discover → Verify → Download → Relevance Check → Dedupe → Resize approximately 1200–1400 px → WebP → Localized ALT → Operator Review → Upload → Association → Readback

Theme assets, logos, cart/search/header icons and unrelated images must be rejected.


## 19. Existing product and category content revision

Existing Product Content Revision is a separate operational class. Selection can be one product, multiple products, category, brand, weak-SEO products or incomplete-content products.

Normally locked for product revision:
M99 ID, Product Name, URL/slug, Channel Product ID.

Editable:
short/long descriptions, H2/H3, technical specifications, materials, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links, image ALT.

Existing Category Content Revision supports one category, multiple categories, category + subcategories or all categories in a selected channel.

Normally locked:
M99 Category ID, Channel Category ID, Existing Category Name, Existing URL/slug, Parent relationship.

Structural/identity migrations are separate Super Admin operations.


## 20. Product Quality Gate

Critical areas include:
IDENTITY
MANUFACTURER_EVIDENCE
SUPPLIER_MATCH
PRICE
VAT
CURRENCY
LANGUAGES
CONTENT
SEO
TECHNICAL_FACTS
IMAGES
ALT
VARIANTS
DEFAULT_COMBINATION
TEST_DRAFT
READBACK
FRONT_OFFICE
NO_INVENTED_CLAIMS
NO_UNVERIFIED_STOCK

A numeric score can never override a failed critical gate.


## 21. Dolibarr, MoneyWork, migration and CRM boundaries

M99 = canonical identity, knowledge and governance.
Dolibarr = operational ERP/CRM/warehouse representation.

Preferred migration:
Inspect → Normalize → Deduplicate → Identity Map → Supplier/Customer Map → Dry Run → Import → Reconcile → Audit

MoneyWork and legacy sites are sources to reconcile, not masters of M99 identity.

CRM foundation remains:
First call → Offer → Second call

Customer 360 remains planned after product-platform stabilization.


## 22. Security, audit and credentials

Login uses username or email + password. Required direction includes secure password hashing, sessions/logout, timeout, failed-login throttling/lockout, reset-password workflow, login/logout audit and future 2FA.

Operators never see channel/B2B credentials.

No passwords, API keys, tokens or cookies may be committed to Git, written into logs or exposed in screenshots.

Central logs for Super Admin include:
Audit Log, System Log, Supplier/B2B & Channel Integration Logs, Security Log.

Minimum log fields:
timestamp, severity, user, module, operation, entity, supplier/channel, job_id, result, message, correlation_id.

Never log secret values.


## 23. SAFE development and Git governance

Controlled development remains mandatory:

Known Git baseline
→ clean working tree
→ controlled patch/installer
→ dependency verification
→ Python compile
→ dedicated tests
→ full pytest regression suite
→ exact changed-file review
→ explicit COMMIT
→ no automatic Push
→ Push only after report review
→ synchronization verification

Failed gates roll back to the known baseline. Tests are not weakened merely to obtain a green release.


## 24. Operational classes

A. NEW PRODUCT IMPORT
B. EXISTING PRODUCT DAILY SYNC
C. MANUAL / EXCEPTIONAL REPAIR
D. EXISTING PRODUCT CONTENT REVISION
E. EXISTING CATEGORY CONTENT REVISION
F. KNOWLEDGE / EVIDENCE ACQUISITION

These classes must remain distinct because their identity, permissions and write contracts differ.


## 25. Anti-loop governance — new mandatory decision

README remains the normative human-readable constitution, but README alone is no longer considered sufficient project memory.

Before proposing architecture or reopening a design question, the project must consult context in this order:

DECISION_REGISTRY
→ M99_CURRENT_CONTEXT
→ PROJECT_STATE
→ latest master README
→ relevant ADR
→ relevant tests / implementation history
→ only then a new proposal

Planned machine-readable governance files:
- DECISION_REGISTRY.yaml — decision ID, statement, status, date, supersedes, references.
- FEATURE_GAP_REGISTRY.yaml — normative_status and implementation_status per significant feature.
- M99_CURRENT_CONTEXT.yaml — current channels, platforms, languages, roles, stable/current commits, active milestone, fixed decisions and OPEN/DEFERRED items.
- docs/ADR/ — Architecture Decision Records for major choices.
- ROADMAP.md — current priorities only.
- CHANGELOG.md — actual implementation history.

Interpretation rules:
- DECIDED + NOT_IMPLEMENTED → implement it; do not redesign it.
- IMPLEMENTED + NOT_TESTED → test it; do not invent a new architecture.
- TESTED → preserve until explicitly superseded.
- SUPERSEDED → do not reuse as current design.
- OPEN/DEFERRED → may be discussed.
- A failed implementation attempt does not reopen a DECIDED rule.

This governance protocol is mandatory for future proposals to prevent circular discussion and repeated design work.


## 26. Decisions fixed — do not reopen without explicit superseding decision

- Operator-first UX.
- One-decision-per-screen target UX.
- Operator vs Super Admin separation.
- Operators do not need programming/API knowledge.
- Identity Before Content.
- Permanent numeric M99 identity; no reuse.
- M99 reference format is M99- plus digits only.
- ProductGroup lifecycle draft → active → paused → retired.
- DELETE is exceptional and explicit.
- Supplier/Manufacturer are Organization roles; one Organization may have both.
- New suppliers/manufacturers/brands require Super Admin approval before general operator availability.
- B2B portal belongs to Organization and declares capabilities.
- Direct Supplier Selection is target UX.
- New Product scope is selective and supports one/many/all products/categories as applicable.
- Target channels are operator-selectable within permissions; one or many channels may be selected.
- m99.eu is a target channel, not the central Add Product workflow.
- Every new product ImportJob uses requested/authorized/ready/blocked target scope.
- New products publish TEST/Draft first.
- TEST category is resolved live.
- Final category is operator-owned.
- Duplicate guard before CREATE.
- Mandatory readback.
- HTTP success is not Quality PASS.
- Activation requires authorization.
- Presence != Stock.
- Existing products sync daily; NO_CHANGE → NO_WRITE.
- Existing Product Name + URL are locked during normal content revision.
- Existing Category Name + URL are locked during normal content revision.
- Product and Category content may be revised.
- Every content field is reviewed per language; Image + ALT together.
- Source images come from manufacturer/supplier evidence, not another M99 channel by default.
- Target selling price is VAT-included gross.
- Exactly one default combination for variational products.
- M99 is canonical; Dolibarr is operational ERP/CRM/warehouse.
- SAFE installer/test/commit/push workflow remains mandatory.
- README plus machine-readable governance is mandatory before future architectural proposals.


## 27. Genuine OPEN / DEFERRED items

The following remain genuinely open/deferred unless a later ADR resolves them:
- universal ProductGroup vs colour-variant boundary;
- universal Variant SKU standard;
- exact Dolibarr parent/variant implementation;
- exact image-rights contract per external source;
- production Vault deployment;
- exact WordPress commerce adapter details per site;
- 2FA rollout timing;
- final technical implementation of direct supplier browser selection for every supplier;
- final production design of the generalized multi-channel Operator Add Products wizard.


## 28. Next implementation priority

Do not add more isolated technical screens before implementing the generalized operator workflow.

Next target:
M99 v0.7.3 — Operator Product Import Wizard Foundation

Priority sequence:
1. Consolidate governance files: DECISION_REGISTRY.yaml, FEATURE_GAP_REGISTRY.yaml, M99_CURRENT_CONTEXT.yaml.
2. Replace the narrow m99.eu prototype entry point with the generalized Add Products wizard.
3. Choose Supplier / Organization.
4. Direct browse and select one/many products or categories.
5. Create auditable ImportJob.
6. Identity/Duplicate Review and permanent M99 identity.
7. Select one/many authorized channels/ERP targets.
8. Prepare pricing, languages, content, SEO, images and variants.
9. Show simple operator preflight summary with READY/BLOCKED/NEEDS REVIEW.
10. Operator confirmation.
11. TEST/Draft write through channel adapters.
12. Mandatory readback and Quality Report.
13. Activation only according to permissions.

Parallel Super Admin priorities:
Organization/Brand Registry, approval queues, B2B Connectors, Knowledge Sources, Central Logs, Existing Product/Category Revision and Daily Sync.


## 29. Definition of success

Single product:
exact identity, evidence, supplier mapping, pricing/FX/VAT, localized content, technical facts, images/ALT, variants, TEST draft, readback, operator-ready and no invented claims/stock.

Bulk:
the same engine handles 10–20 products first, then 100–200 and larger selections without per-product custom code.

Multi-channel:
each target has independent preflight/status. Blocked targets are visible and diagnosable; ready targets proceed under the publishing contract.

Operator UX:
a non-programmer can complete the workflow without understanding APIs, scripts, XML/JSON, database internals or credentials.

Governance:
previously decided rules are not repeatedly reopened; implementation work is driven by decision state, current state, ADRs and tests.


## 30. Final architecture philosophy

M99 Knowledge Platform is not merely a scraper, uploader, translator, SEO generator, ERP bridge or website integration.

It is one governed system:

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
+ MACHINE-READABLE PROJECT MEMORY

Product truth once. Customer truth once. Verified everywhere. Governed by humans. Implemented without circular redesign.


---

**M99 Knowledge Platform — README v8 — Product truth once. Customer truth once. Verified everywhere. Governed by humans. Implemented without circular redesign.**
