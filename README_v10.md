# M99 Knowledge Platform — README v10

> **Master System Constitution / Consolidated Project Specification / Current Development State**  
> **Status:** normative master document / active development  
> **Consolidated:** README v1-v9 + governance + verified v0.7.3 Phase 4.5 runtime decisions through 2026-08-26  
> **Repository:** `M99-Knowledge-Platform`  
> **Current development line:** `v0.7.3`  
> **Frozen tested runtime baseline:** `v0.7.3 Phase 4.5 Revision 29R3.2R2`  
> **Next implementation target:** `Manufacturer Evidence + Canonical Content Foundation`

---

## 0. Role of README v10

README v10 is the consolidated Master System Constitution, Current Development State and Operational Contract for M99 Knowledge Platform.

It supersedes README v9 as the current human-readable master while preserving every still-valid decision from README v1-v9. It also incorporates the governance consolidation, v0.7.3 Operator Product Import Wizard Foundation, and the latest decisions for Live Supplier Browser, Existing Product Daily Sync, Product Presence and supplier/manufacturer external availability warehouses in Dolibarr.

Anti-loop rule:
DECIDED != IMPLEMENTED.

A missing implementation, failed experiment, incomplete connector or temporary runtime defect does not reopen a DECIDED architectural rule. A rule changes only through an explicit superseding decision with recorded rationale.

Mandatory context order before architecture proposals:
DECISION_REGISTRY -> M99_CURRENT_CONTEXT -> PROJECT_STATE -> latest master README -> relevant ADR -> relevant tests / implementation history -> only then a new proposal.


## 1. Vision and purpose

M99 Knowledge Platform is the central identity, product knowledge, supplier/manufacturer knowledge, evidence, commercial intelligence, content, SEO, publishing, synchronization, ERP/CRM integration and governance layer for the M99 ecosystem.

M99 is the Single Source of Truth for canonical identity and verified knowledge. External systems are sources, channels, destinations or operational systems. They do not own canonical M99 identity.

Core principles:
- Single Source of Truth.
- Knowledge First.
- No Duplicate Data.
- Evidence Based.
- AI Native, not AI Invented.
- Historical observations are preserved.
- Market and Channel are separate concepts.
- ERP operates the business but does not own canonical M99 knowledge.
- Removing a product from a channel must not destroy accumulated product knowledge.
- Observation is not automatically canonical truth.


## 2. Current ecosystem and channel scope

Current M99 channel / system scope includes:

- mela99.com — ThirtyBees 1.7 / PrestaShop 1.7 family; BG + EN target language scope.
- m99.eu — PrestaShop 9.1.5; current verified active languages EN, BG, RU.
- rabotni-drehi.com — WordPress; BG content, with channel-specific wording.
- medicinski-drehi.com — medical clothing channel, managed operationally through M99 workflows.
- laviro.ro — PrestaShop 1.6.1.24; Romanian market/content.
- alviro.ro — Romanian market channel.
- toplinka.com — heating / photovoltaic service channel.
- Dolibarr — operational ERP / CRM / warehouse target, not a web shop.
- MoneyWork / legacy exports — migration and reconciliation sources, not canonical masters.

Channels are configuration-driven mappings. Adding or removing a channel must not redesign product identity.


## 3. Canonical data model direction

The canonical chain is:

ProductGroup -> ProductVariant -> SupplierOffer / SupplierMapping -> Evidence / Observation -> ChannelPresence -> ChannelContent -> ChannelPrice -> InventoryMapping

External identifiers are mappings, not canonical identity:
supplier reference / SKU, manufacturer reference / MPN, EAN/GTIN, MoneyWork code, Dolibarr ID, website product ID, marketplace ID, legacy reference, title and URL.

Identity resolution:
External Record -> Import -> Normalize -> Resolve -> Match -> Decision -> Overrides -> Operator Review -> Final M99 Identity

Uncertain records never silently modify canonical identity.


## 4. ProductGroup and identity governance

ProductGroup lifecycle is fixed:

draft -> active -> paused -> retired

Hard DELETE is exceptional. It requires explicit operator approval, typed DELETE confirmation and audit logging.

M99 Reference is fixed and tested:

M99- + digits only

Assigned M99 identity is never reused for another ProductGroup.

Identity Before Content:

SELECT -> RESOLVE IDENTITY -> LINK EXISTING or CREATE PERMANENT M99 ID -> THEN CONTENT

Duplicate / identity states:
NEW / EXISTING / AMBIGUOUS / UNRESOLVED

AMBIGUOUS requires human decision.


## 5. Organization, Supplier, Manufacturer and Brand model

Supplier and Manufacturer are roles of one canonical Organization, not mutually exclusive master tables. One Organization may be both SUPPLIER and MANUFACTURER.

An Organization may own:
- brands;
- public websites;
- B2B portals;
- APIs;
- feeds;
- catalogues;
- price lists;
- technical documents;
- certificates;
- image libraries.

An operator may propose a new Supplier, Manufacturer or Brand. The proposal enters PENDING_SUPER_ADMIN_APPROVAL and is not generally visible to operators.

Only Super Admin may APPROVE, REJECT, MERGE_WITH_EXISTING or ACTIVATE_ROLE.

Brand is a separate canonical object linked to owner/manufacturer organizations and official evidence sources.

A canonical M99 product may have multiple verified SupplierMappings and multiple SupplierSources. The system must not assume one product = one supplier.


## 6. Evidence, provenance and source priority

Every important fact must retain provenance where applicable:
source, observed_at, verified_at, document/page, reviewer, confidence/conflict state and relationship to the canonical entity.

Evidence priority:
1. exact official manufacturer;
2. official manufacturer documentation / catalogue / certificate;
3. validated B2B source;
4. exact supplier source;
5. verified internal / legacy data;
6. operator verified fact;
7. AI over verified evidence only.

Supplier or competitor observations are useful evidence but must not silently replace stronger verified manufacturer truth.

Historical observations are preserved so M99 can explain what changed, when it changed and which source reported it.


## 7. SupplierSource and Live Connector Contract

Each approved Organization may have one or more SupplierSources.

Supported source classes include:
PUBLIC_WEBSITE, B2B_PORTAL, API, CSV, XLSX, XML, JSON, PDF_CATALOGUE, TECHNICAL_DOCUMENT, CERTIFICATE, PRICE_LIST, STOCK_FEED, SIZE_CHART, IMAGE_LIBRARY and MANUAL_VERIFIED_SOURCE.

Each source declares capabilities, for example:
IDENTITY, TECHNICAL_FACTS, MPN, EAN_GTIN, IMAGES, DOCUMENTS, CATALOGUES, PRICE, PURCHASE_PRICE, AVAILABILITY, LEAD_TIME, VARIANTS, STOCK and ORDER_TERMS.

B2B / connector states:
NOT_CONFIGURED / CREDENTIALS_REQUIRED / CONNECTED / READY / AUTH_FAILED / SESSION_EXPIRED / BLOCKED / VERIFICATION_FAILED

Generic connector contract direction:
connect / health_check -> list_categories -> list_products -> get_product -> get_variants -> get_images -> get_commercial_data

The SAFE installer does not crawl suppliers. The running M99 Admin runtime may perform controlled read-only live access to approved SupplierSources when an authorized operator opens the Supplier Browser or when scheduled Daily Sync runs.

Supplier-specific adapters implement the common contract. The operator UI must not change for every supplier.

STENSO is the preferred first reference connector for proving the contract; this is an implementation priority, not a change to the generic architecture.


## 8. Operator and Super Admin profiles

OPERATOR is a business user, not a programmer.

The operator must not need Python, PowerShell, API, HTTP, JSON, XML, SQL, credentials or platform internals.

Operator-first UX and one-decision-per-screen are fixed.

Primary operator navigation direction:
Dashboard
Add Products
My Tasks
Products
Where They Are Sold
Prices and Availability
Problems to Review
History

SUPER ADMIN manages:
Users/Roles, Organizations, Suppliers, Manufacturers, Brands, B2B Portals, Knowledge Sources, Channels/ERP, Languages, Pricing/VAT/FX, Identity Registry, Import Presets, Sync Rules, Content Revision Policies, Locked Fields, Quality Gates, Credential Status, Audit/Logs/Diagnostics, Product Presence configuration and Feature/Gap Registry.


## 9. New Product Operator Workflow

The primary workflow is generalized Add Products. It is not a dedicated uploader for m99.eu or any other single channel.

Target workflow:

Login
-> Add Products
-> Choose Supplier / Manufacturer Organization
-> Direct Supplier Selection
-> Identity / Duplicate Review
-> Permanent M99 ID or Existing Match
-> Choose Target Channels / ERP
-> Prepare Product
-> Pricing / VAT
-> Content / SEO / Languages
-> Images + localized ALT
-> Variants + Default Combination
-> Preflight
-> Operator Confirmation
-> TEST / Draft Import
-> Readback
-> Quality Report
-> Activation according to permission

The primary operator workflow does not use URL copy/paste or BAT/Python scripts.


## 10. Product and category selection scope

Direct Supplier Selection must support the same workflow engine for:
- one exact product;
- multiple selected products;
- one supplier category;
- multiple supplier categories;
- all products in a selected category or source where supported;
- first N products;
- only products new to M99;
- manual selection.

The architecture must support 1, 2, 3, 20, 200 or all selected products without product-specific code.

Selection never bypasses identity resolution, evidence verification, duplicate/legacy matching, authorization, target scope, pricing/VAT, image gate, variant/default-combination gate, language/content gate, TEST/Draft policy, readback or Product Quality Gate.


## 11. ImportJob as first-class auditable object

Every new-product import is an auditable ImportJob.

Minimum conceptual fields:
job_id, created_at, created_by, operator_role,
source_organization_id, source_id, source_type, source_urls, source_categories,
selection_mode, selected_products, selected_categories, product_count,
requested_targets, authorized_targets, ready_targets, blocked_targets,
pricing_policy, content_policy, image_policy, language_policy,
dry_run, requires_confirmation,
identity status,
status, started_at, finished_at,
result_per_product, result_per_target,
audit_log and source snapshot references.

Import presets simplify recurring work but never grant permissions the user does not already have.


## 12. Target selection and multi-channel publishing

For NEW PRODUCT IMPORT the operator selects one or more authorized target channels / ERP destinations.

WRITE_TARGETS = REQUESTED_TARGETS intersect AUTHORIZED_TARGETS intersect READY_TARGETS

Target states include:
NOT_SELECTED / SELECTED / UNAUTHORIZED / BLOCKED / READY / COMPLETED / FAILED / QUALITY_INCOMPLETE

NOT_SELECTED is different from BLOCKED.

m99.eu is one target channel among multiple authorized targets. Dolibarr is a different target type with its own adapter and payload.


## 13. Publishing Constitution

Publishing rules remain mandatory:

1. NEW -> TEST/Draft first.
2. TEST category is resolved live.
3. Final category is operator-owned.
4. Existing approved Product Name + URL are locked during normal revision.
5. Approved M99 name + URL are locked.
6. Unapproved TEST draft may be repaired.
7. CREATE and UPDATE are different contracts.
8. Duplicate guard before CREATE.
9. Mandatory readback after write.
10. HTTP 200/201 does not equal Product Quality PASS.
11. Front Office verification is required where applicable.
12. Activation requires authorization.
13. DELETE remains an explicit human action.

Command-line scripts remain development/diagnostic tools. Normal publishing is initiated through M99 Admin workflows.


## 14. Content, SEO and languages

A complete product package may include:
Product Name, H1, short description, long description, H2/H3, technical specifications, materials, sizes, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links, images and localized ALT.

Supplier prose is not copied verbatim. Facts may be shared, but prose/SEO is adapted per market, channel and language to avoid mechanical duplicate content.

Language Registry is dynamic. Known scope includes BG, EN, RU, RO, GR and future languages. Channel language IDs are discovered live, not assumed.

Each content field / language follows:
GENERATED -> EDITED -> SAVED -> REVIEWED -> APPROVED

A post-approval edit invalidates only the affected field approval. Image + ALT are reviewed together per language.


## 15. Image governance

Image source priority:
official manufacturer -> verified supplier -> verified cached original source.

Another M99 channel is not the master image source merely because it already contains the correct image.

Image pipeline:
Discover -> Verify -> Download -> Relevance Check -> Dedupe -> Resize approximately 1200-1400 px -> WebP -> Localized ALT -> Operator Review -> Upload -> Association -> Readback

Theme assets, logos, header/cart/search icons and unrelated images must be rejected.


## 16. Variants, default combination and stock semantics

Sizes are variants when product logic requires them.

Visible size != stock.

Supplier availability != M99-owned physical stock.

A variational product must have exactly one default combination and cache_default_attribute must point to it where the channel uses that concept. Failure blocks Product Quality PASS.

Dolibarr stock is variant-aware.

M99 must preserve three distinct concepts:
- supplier/manufacturer external availability;
- M99-owned physical stock in Dolibarr;
- channel-published availability / sellability.

These must never be silently conflated.


## 17. Product Presence Registry and channel report

Every canonical M99 product must answer:
"In which site(s) is this product present, and where is it missing?"

Presence is separate from stock.

Presence states:
NOT_PRESENT
PRESENT_DRAFT
PRESENT_TEST
PRESENT_ACTIVE
PRESENT_PAUSED
PRESENT_RETIRED
PRESENT_LAST_VERIFIED
UNKNOWN
VERIFICATION_FAILED

Product Presence must support both directions:
- Product -> Channels / ERP
- Channel -> Products

It must also support reports for:
- products present by channel;
- products missing in selected channels;
- products not mapped to Dolibarr;
- presence verification failures.

Minimum presence data direction:
m99_product_id, channel/target, external product ID, external variant ID when applicable, presence_status, publication_state, channel_price, currency, last_verified_at, last_sync_at, readback status, front-office verification status, sync_enabled and last_error.

Operator actions should include FAST VERIFY, LIVE VERIFY, open channel product and view sync history where supported.


## 18. Existing Product Daily Sync

NEW PRODUCT IMPORT and EXISTING PRODUCT DAILY SYNC are separate operational classes with different permissions and write contracts.

Daily Sync is scheduled and is not controlled by the operator's new-product target selection.

Every day M99 must:
1. load canonical products with verified Supplier / Source mappings;
2. verify supplier/B2B price;
3. verify supplier availability;
4. verify variants / sizes;
5. verify product changed/discontinued state;
6. compare with the last verified observation;
7. produce NO_CHANGE or a ChangeSet;
8. write only changed fields according to ownership and pricing policies;
9. update all already-existing channel/ERP mappings that are allowed for sync;
10. perform readback and Front Office verification where applicable;
11. audit the result.

Daily Sync never creates a product in a channel where no ProductPresence / mapping already exists.

NO_CHANGE -> NO_WRITE.


## 19. Daily Sync change states and failure semantics

Minimum Daily Sync result states:
NO_CHANGE
PRICE_CHANGED
AVAILABILITY_CHANGED
VARIANT_AVAILABILITY_CHANGED
PRODUCT_CHANGED
SUPPLIER_DISCONTINUED
VERIFICATION_FAILED

A supplier/source outage or parsing failure is VERIFICATION_FAILED. It must never be interpreted automatically as OUT_OF_STOCK or quantity zero.

The last verified observation remains valid until a new verified observation supersedes it, subject to freshness rules.


## 20. Supplier observations and commercial history

SupplierObservation / SupplierAvailabilityObservation records should preserve:
source_id,
supplier/manufacturer organization,
source product reference,
source variant reference,
source URL or resource ID,
observed_at,
verified_at,
price,
currency,
availability state,
exact quantity when reliably supplied,
variant availability,
lead time where available,
discontinued/changed state,
changed_fields,
verification result,
provenance/conflict state.

Observations are historical evidence. They are not automatically canonical truth and are not automatically physical stock.


## 21. Pricing and VAT synchronization contract

Target selling price is customer-facing gross / VAT-included price.

Standard VAT is channel/market configuration, not a universal hardcoded constant.

Price change pipeline:
supplier price
-> approved pricing rule
-> market currency
-> market/channel VAT
-> target gross selling price
-> platform NET representation if required
-> channel API write
-> readback
-> Front Office gross-price verification where applicable

Price updates outside policy limits may be blocked for review instead of written automatically.

Back Office/API price alone is not sufficient proof of customer-facing price correctness.


## 22. Dolibarr role and warehouse architecture

M99 owns canonical identity, knowledge and governance.
Dolibarr is the operational ERP/CRM/warehouse representation.

Normal M99-owned physical stock:
Supplier order -> reception -> physical stock increase.
Customer order -> shipment -> physical stock decrease.

New decided extension:
For approved Supplier and/or Manufacturer Organizations, M99 may create linked EXTERNAL availability warehouses in Dolibarr named after the organization.

Warehouse ownership/type must distinguish at least:
M99_PHYSICAL
SUPPLIER_EXTERNAL
MANUFACTURER_EXTERNAL

An external supplier/manufacturer warehouse represents the latest verified external availability and is never automatically interpreted as M99-owned physical stock.

Example:
M99 Central Warehouse — M99_PHYSICAL
STENSO — SUPPLIER_EXTERNAL
PALLTEX — SUPPLIER_EXTERNAL
DIADORA — MANUFACTURER_EXTERNAL

External warehouse availability must be variant-aware where the source provides variant-level information.


## 23. Exact quantity versus availability-only supplier data

Supplier sources do not always expose a trustworthy numeric quantity.

M99 must never invent stock numbers such as 30, 999 or any other placeholder to represent "in stock".

External availability states may include:
EXACT_QUANTITY
IN_STOCK
LOW_STOCK
OUT_OF_STOCK
ON_REQUEST
UNKNOWN
VERIFICATION_FAILED

A numeric quantity may be written to a Dolibarr external availability warehouse only when the SupplierSource provides a reliable numeric quantity and the mapping is verified.

When the source provides only a status, M99 stores the status observation and does not fabricate a physical-style number.


## 24. Multiple suppliers and combined Product Availability view

One canonical M99 product may be mapped to multiple suppliers and/or manufacturers.

Example:
M99 Product
- STENSO mapping
- PALLTEX mapping
- manufacturer mapping

The Product Availability view should combine:
- Product Presence by web channel / ERP;
- M99-owned physical stock;
- supplier/manufacturer external availability by source;
- variant-level availability;
- last verified timestamp;
- last sync result;
- errors / verification failures.

This enables future supplier comparison, backup sourcing and purchasing recommendations without changing canonical product identity.


## 25. Daily Sync operational dashboard

Daily Sync must be visible as a business-first module, not only as an invisible background script.

Minimum dashboard metrics:
Last run
Products checked
Supplier checks
Price changes
Availability changes
Variant changes
Product/discontinued changes
Channel writes
Dolibarr writes
NO_CHANGE count
Blocked count
Errors
Verification failures

Dashboard attention cards may include:
Price/VAT gate failures
Missing default combination
Image failures
Language failures
Supplier ambiguity
Presence verification failures
Daily Sync failures
Products missing in selected channels
Products not mapped to Dolibarr


## 26. Existing product and category content revision

Existing Product Content Revision is separate from Daily Sync and New Product Import.

Selection may include one product, multiple products, category, brand, weak-SEO products or incomplete-content products.

Normally locked:
M99 ID, Product Name, URL/slug, Channel Product ID.

Normally editable:
short/long descriptions, H2/H3, technical specifications, materials, FAQ, Meta Title, Meta Description, SEO keywords, schema, internal links and image ALT.

Existing Category Content Revision may target one category, multiple categories, category + subcategories or all categories in a selected channel.

Normally locked for category revision:
M99 Category ID, Channel Category ID, existing Category Name, existing URL/slug and parent relationship.

Structural / identity migrations are separate Super Admin operations.


## 27. Product Quality Gate

Critical areas:
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


## 28. Dolibarr payload versus web-channel payload

Dolibarr is not "another website".

Web channel payload may include:
identity mapping, name, content, SEO, categories, images, variants, price, tax and publication state.

Dolibarr payload may include:
canonical M99 identity, supplier mapping, supplier reference, EAN/GTIN, cost/purchase data, selling price policy, variants, warehouse master data, stock ownership, product lifecycle and counterparty mappings.

The orchestration engine selects the correct target adapter by target type.


## 29. MoneyWork / legacy migration and CRM boundaries

MoneyWork and legacy sites are sources to reconcile, not masters of M99 identity.

Preferred migration:
Inspect -> Normalize -> Deduplicate -> Identity Map -> Supplier/Customer Map -> Dry Run -> Import -> Reconcile -> Audit

Legacy identity/history must be preserved through mappings.

CRM foundation:
First call -> Offer -> Second call

Customer 360 remains planned after product-platform stabilization.


## 30. Authentication, RBAC, security and logs

Login direction:
username or email + password.

Required security:
secure password hashing, sessions/logout, session timeout, failed-login throttling/lockout, reset-password workflow, login/logout audit and future 2FA.

Operators never see channel/B2B credentials.
No passwords, API keys, tokens or cookies in Git, logs or screenshots.

Permissions are enforced server-side, not only through menu visibility.

Representative capabilities:
product.read/create/update/activate/retire/delete_approve
import.create_job/import.execute/import.select_targets
supplier.browse
sync.view/sync.run_manual
pricing.view/pricing.approve
channel.<channel>.read/write
dolibarr.read/write
users.manage/roles.manage/settings.manage/audit.read

Central logs for Super Admin:
Audit Log
System Log
Supplier/B2B & Channel Integration Logs
Security Log

Minimum log fields:
timestamp, severity, user, module, operation, entity, supplier/channel, job_id, result, message, correlation_id.

Never log secret values.


## 31. m99.eu verified integration state

m99.eu runs PrestaShop 9.1.5.

Verified API base:
https://m99.eu/api

Verified active language mapping:
1 = English
2 = Bulgarian
3 = Russian

Current controlled test category used by the integration:
ID 26

Verified:
products GET permission = true
products POST permission = true

Dry Run successfully produced a minimal multilingual inactive product payload with numeric-only M99 reference, category 26, active=0, available_for_order=0, visibility=none, EN/BG/RU localized fields and minimal associations.

This proves the adapter contract. It does not make m99.eu the central operator workflow.


## 32. Development history and current implementation state

Stable recovery baseline:
M99 v0.7.1 Revision 7
234 tests passed
commit: 8c3d2d7fc729f22001c320d1fa033528272eb21e

v0.7.2 milestones:
- Phase 1 Canonical Data Model Foundation; commit 193b6bcc6c8f4b13439102a99f00d1b542b1851f.
- Phase 2 SQLAlchemy Persistence + Alembic temporary migration baseline; full regression PASS; real Admin DB intentionally not migrated by installer.
- Phase 2.5 m99.eu PrestaShop 9 integration corrections.
- Revision 5.1 import-path fix and successful live preflight.
- Revision 5.2 Fix 1 minimal multilingual payload / legacy test alignment; commit 5705bff675224748f95f58cbf5860b0bb761f972.
- Phase 3 Fix 1 Admin bridge / Python 3.14 test compatibility; full regression PASS; commit ec0cc276bdf235868f74df52aaf62c6421d3b32d.
- Governance Consolidation created DECISION_REGISTRY, FEATURE_GAP_REGISTRY, M99_CURRENT_CONTEXT and ADR-0001; local commit reported as 5aec1b40ddcc6f1498512dde9eb7da6b0d18bca8.
- README v8 was uploaded to GitHub.

v0.7.3:
- Operator Product Import Wizard Foundation completed with compile, dedicated tests and full regression PASS; local commit reported as e25e1e9a9623df6e418e89cf997e07ae653ddf3f.
- Phase 2 persistence/browser package was drafted but its initial no-live-contact Supplier Browser scope was deemed insufficient before execution and is superseded by the Revision 1 scope in this README.

Push/synchronization status of local commits must be verified from Git before the next SAFE installer; README does not assume an unreported Push.


## 33. M99 v0.7.3 Phase 2 Revision 1 target scope

Next target:

M99 v0.7.3 Phase 2 Revision 1
Persistent ImportJob + Organization Registry + Live Supplier Browser Contract + Daily Existing Product Sync Contract + Product Presence + Dolibarr External Availability Warehouses

Required foundation entities / contracts:
Organization
OrganizationRole
Brand
SupplierSource
SupplierProductMapping
SupplierVariantMapping
SupplierObservation
SupplierAvailabilityObservation
ImportJob
ImportJobTarget
ProductPresence
ChannelProductMapping
ExternalWarehouseMapping
ExternalWarehouseStockObservation
DailySyncRun
DailySyncItem
ChangeSet

Core runtime path:
Organization -> SupplierSource -> Live Connector -> Categories -> Products -> Selection -> Source Snapshot -> Identity Resolver -> ImportJob

Daily path:
Verified SupplierMapping -> Daily Observation -> Compare Last Verified -> Change Detection -> Policy -> Existing Presence Mappings Only -> Write Changed Fields -> Readback -> Front Office Verify -> Audit

Dolibarr external availability path:
Verified Supplier/Manufacturer availability -> external warehouse mapping -> variant-aware external availability update -> readback/audit

The installer remains SAFE and does not crawl external systems automatically. Live access occurs through authorized runtime actions and scheduled sync services.


## 34. Operational classes

A. NEW PRODUCT IMPORT
- operator initiated;
- direct supplier selection;
- selective targets;
- authorization;
- TEST/Draft first;
- no assumption of all channels.

B. EXISTING PRODUCT DAILY SYNC
- scheduled;
- canonical products with verified supplier mappings;
- all already-existing allowed channel/ERP mappings;
- no automatic creation in missing channels;
- NO_CHANGE -> NO_WRITE.

C. MANUAL / EXCEPTIONAL REPAIR
- controlled exact target;
- exact allowed fields;
- explicit confirmation;
- mandatory readback;
- no broad side effects.

D. EXISTING PRODUCT CONTENT REVISION

E. EXISTING CATEGORY CONTENT REVISION

F. KNOWLEDGE / EVIDENCE ACQUISITION


## 35. Fixed decisions — do not reopen without explicit superseding decision

The following are fixed unless explicitly superseded:

- M99 is the canonical Single Source of Truth.
- Knowledge First.
- No Duplicate Data.
- Evidence Based.
- AI Native, not AI Invented.
- Historical observations are preserved.
- Market != Channel.
- External IDs are mappings, not canonical identity.
- Identity Before Content.
- Permanent M99 identity; no reuse.
- M99 Reference = M99- + digits only.
- ProductGroup lifecycle draft -> active -> paused -> retired.
- DELETE is exceptional and explicit.
- Supplier/Manufacturer are Organization roles; one Organization may have both.
- One product may have multiple verified supplier/manufacturer mappings.
- New Supplier/Manufacturer/Brand requires Super Admin approval before general operator availability.
- B2B/SupplierSource belongs to Organization and declares capabilities.
- Operator-first UX.
- One-decision-per-screen.
- Operators do not need programming/API knowledge.
- Direct Supplier Selection is target UX.
- Operator can select one/many/all products/categories where supported.
- New-product targets are operator-selectable within permissions.
- m99.eu is one target, not the central Add Product workflow.
- Every new-product import is an auditable ImportJob.
- WRITE_TARGETS = REQUESTED intersect AUTHORIZED intersect READY.
- New products publish TEST/Draft first.
- TEST category is resolved live.
- Final category is operator-owned.
- CREATE != UPDATE.
- Duplicate guard before CREATE.
- Mandatory readback.
- HTTP success != Quality PASS.
- Front Office verification where applicable.
- Activation requires authorization.
- Content is market/channel/language aware.
- Supplier prose is not copied verbatim.
- Dynamic Language Registry.
- Every content field is reviewed per language; Image + ALT together.
- Manufacturer/supplier evidence is the image source priority.
- Variational product has exactly one default combination.
- Presence != Stock.
- Visible size != stock.
- Supplier availability != M99-owned physical stock.
- Existing products sync daily.
- Daily Sync uses already-existing mappings; it does not create missing channel products.
- NO_CHANGE -> NO_WRITE.
- Verification failure is not interpreted as zero/out-of-stock.
- Price sync uses approved pricing rule, market currency, VAT, write, readback and Front Office verification.
- Dolibarr is operational ERP/CRM/warehouse; M99 remains canonical.
- Dolibarr physical stock is variant-aware.
- Supplier/manufacturer external availability warehouses may exist in Dolibarr but remain logically separate from M99-owned physical stock.
- Numeric external stock is recorded only when the source provides reliable exact quantity; status-only sources do not receive invented numbers.
- Product Presence provides Product -> Channels and Channel -> Products reporting, including missing mappings.
- Permissions are enforced server-side.
- Operators never see secrets.
- SAFE development/test/commit/push workflow is mandatory.
- README plus machine-readable governance is mandatory before architectural proposals.


## 36. Genuine OPEN / DEFERRED items

The following remain genuinely open/deferred unless a later ADR resolves them:
- universal ProductGroup versus colour-variant boundary;
- universal Variant SKU standard;
- exact Dolibarr parent/variant implementation;
- exact Dolibarr production stock-decrease configuration per deployment;
- exact image-rights contract per external source;
- production Vault deployment;
- exact WordPress commerce adapter details per site;
- 2FA rollout timing;
- supplier-specific implementation details for every Live Supplier Connector;
- exact freshness/expiry thresholds for supplier observations by source type;
- exact Super Admin UI for supplier/manufacturer external warehouse policy;
- final purchasing recommendation / preferred-supplier algorithm;
- browser extension workflow remains deferred until embedded Supplier Browser and authorization are stable.


## 37. Definition of success

Single product:
exact identity, evidence, supplier mappings, pricing/FX/VAT, localized content, technical facts, images/ALT, variants/default combination, TEST draft, readback, operator-ready, no invented claims or stock.

Bulk:
the same engine supports 10-20 products first, then 100-200 and larger selections without per-product custom code.

Supplier Browser:
a non-programmer chooses an approved supplier, browses real categories/products and selects products without copying URLs.

Daily Sync:
verified supplier observations are compared daily, only real changes generate writes, all writes are read back, failures do not erase last verified truth.

Presence:
for every canonical product M99 can report exactly where it exists, where it is missing, its external IDs, publication state, last verification and last sync.

Warehouse:
M99-owned physical stock and supplier/manufacturer external availability are visible together but never confused.

Governance:
already-decided rules are implemented or tested, not repeatedly redesigned.


## 38. Final architecture philosophy

M99 Knowledge Platform is not merely a scraper, uploader, translator, SEO generator, ERP bridge or website integration.

It is one governed system:

KNOWLEDGE
+ EVIDENCE
+ IDENTITY
+ ORGANIZATIONS
+ BRANDS
+ SUPPLIER/B2B CONNECTORS
+ COMMERCIAL OBSERVATIONS
+ CONTENT
+ PRODUCT PRESENCE
+ DAILY SYNC
+ ERP / CRM
+ PHYSICAL + EXTERNAL AVAILABILITY
+ MULTI-CHANNEL PUBLISHING
+ QUALITY GATES
+ AUDIT / LOGS
+ HUMAN GOVERNANCE
+ MACHINE-READABLE PROJECT MEMORY

Product truth once. Customer truth once. Verified everywhere. Governed by humans. Implemented without circular redesign.

---

## 39. Governance Checkpoint — 2026-08-26

This section supersedes older "current state / next target" statements where they conflict with the verified runtime state below. It does not supersede still-valid architecture or governance rules.

### 39.1 Frozen tested runtime baseline

The current frozen tested runtime baseline is:

`M99 v0.7.3 Phase 4.5 Revision 29R3.2R2`

Verified checkpoint evidence:
- PowerShell AST validation: PASS;
- synchronized Git baseline verification: PASS at installer start;
- stable Hydration/DRAFT baseline recognized;
- payload path validation: PASS;
- app.main router registration safety check: PASS;
- Python compile: PASS;
- dedicated tests: PASS;
- full regression: PASS;
- active FastAPI app exposes exactly one Canonical Preview GET route: PASS;
- Supplier / Manufacturer source-role separation: PASS;
- runtime exit code: 0;
- no website write, no migration, no commit, no push from the revision installer.

**Freeze rule:** Rev29R3.2R2 is preserved as the stable recovery/runtime checkpoint. Future work is additive unless an explicit superseding decision authorizes a runtime change. Experimental Rev25-Rev27 performance/content branches are not the baseline.

### 39.2 Current proven operator path

The proven read/prepare path is:

`Supplier Browser -> Live Hydration -> Operator Selection -> DRAFT ImportJob -> Preflight -> Canonical Product Preview`

Canonical Product Preview is a read-only/operator-review layer. It does not authorize website publishing by itself.

## 40. Phase 4.5 mandatory clarifications — decision status

The following decisions are now part of project memory and must not be silently reopened:

| ID | Mandatory clarification | Governance status | Implementation/test state |
|---|---|---|---|
| GOV-V10-001 | Rev29R3.2R2 is the frozen tested runtime baseline. | DECIDED_TESTED | TESTED |
| UX-V10-001 | Supplier Browser starts with zero products selected. | DECIDED_TESTED | IMPLEMENTED + TESTED |
| TEST-V10-001 | First live validation of a new connector/behavior uses exactly one product before batch use. | DECIDED | OPERATIONAL RULE |
| SRC-V10-001 | A product is selectable only after hydration exposes minimum supplier evidence: title, supplier ref/SKU, URL, price, images, description/specifications, variants/sizes and availability. | DECIDED_TESTED | IMPLEMENTED + TESTED for STENSO |
| STENSO-V10-001 | STENSO disabled/faded-grey size means unavailable; active size means available. This is connector-specific, not universal. | DECIDED_TESTED | IMPLEMENTED + TESTED |
| SRC-V10-002 | In the STENSO workflow STENSO is supplier evidence only; manufacturer evidence must come from a separate approved official manufacturer source. | DECIDED_TESTED | IMPLEMENTED + TESTED |
| PREVIEW-V10-001 | Canonical Preview may render supplier-only evidence; missing manufacturer evidence is a warning/quality state, not a route/runtime failure. | DECIDED_TESTED | IMPLEMENTED + TESTED |
| PREVIEW-V10-002 | Canonical Product Preview is read-only: publishable NO and website write NO until later approval gates pass. | DECIDED_TESTED | IMPLEMENTED + TESTED |
| PREVIEW-V10-003 | Supplier evidence and M99 Canonical Draft are distinct layers; a hydrated supplier statement is not automatically canonical truth. | DECIDED_TESTED | IMPLEMENTED + TESTED at preview separation level |
| EVID-V10-001 | Manufacturer enrichment is multi-source and provenance-aware; conflicts prefer authoritative manufacturer/official documentation for technical truth while supplier price/availability remain supplier commercial evidence. | DECIDED | NOT_IMPLEMENTED / NEXT FOUNDATION |
| IMG-V10-001 | Canonical image QA must dedupe repeated images and reject broken/empty/non-product images before approval. | DECIDED | PARTIAL / NOT FULLY ENFORCED |
| CNT-V10-001 | Final EN/channel content is generated only after evidence foundation is sufficient; missing final EN content remains an explicit warning until generation/review exists. | DECIDED_TESTED | WARNING/GATE IMPLEMENTED; GENERATION NOT YET IMPLEMENTED |
| SYNC-V10-001 | Daily Sync reuses verified supplier mappings/variant semantics but remains operationally separate from New Product target selection. | DECIDED | FOUNDATION PRESENT; PRODUCTION DAILY SYNC NOT YET COMPLETE |
| GOV-V10-002 | Current stable state and fixed decisions must be written to machine-readable governance, not README alone. | DECIDED_TESTED | IMPLEMENTED BY THIS GOVERNANCE CHECKPOINT |

Interpretation remains:
- DECIDED + NOT_IMPLEMENTED -> implement it; do not redesign it.
- IMPLEMENTED + NOT_TESTED -> test it.
- TESTED -> preserve until explicitly superseded.
- SUPERSEDED -> do not reuse as current design.
- OPEN/DEFERRED -> may be discussed.
- A failed implementation attempt does not reopen a DECIDED rule.

## 41. Current Canonical Product Preview proof

The current STENSO/Melbourne proof demonstrates that the Canonical Preview can show, before any website write:
- supplier identity and source URL;
- supplier reference / SKU;
- supplier price and currency;
- supplier-level availability;
- description/source evidence;
- specifications/material evidence;
- variants/sizes with availability;
- source images;
- M99 Canonical Draft state;
- target channel context;
- content/SEO preparation state;
- Quality Gate warnings and blockers.

Current expected warnings before the next foundation stage include:
- `MANUFACTURER_EVIDENCE_NOT_ATTACHED`;
- `FINAL_EN_CONTENT_NOT_GENERATED`.

These warnings are intentional and must not be hidden by fabricated data.

## 42. Next implementation target after Governance Checkpoint

The next runtime feature is **not** another rewrite of Hydration, DRAFT, Preflight or Canonical Preview routing.

Next target:

`Manufacturer Evidence + Canonical Content Foundation`

Required additive direction:
1. attach an approved official manufacturer product URL/source to the supplier product review;
2. hydrate manufacturer evidence independently from supplier evidence;
3. retain provenance per fact/source;
4. compare supplier and manufacturer facts and surface conflicts;
5. apply evidence priority without deleting lower-priority observations;
6. prepare canonical technical facts only from verified evidence;
7. dedupe/validate images before content approval;
8. generate final channel/language content only after the evidence gate;
9. keep website write disabled until explicit publish workflow gates are implemented and approved.

## 43. Governance checkpoint file set

This checkpoint updates the project-memory set without changing application runtime:
- `README_v10.md` — normative human-readable master;
- `DECISION_REGISTRY.yaml` — fixed decision states including Phase 4.5 clarifications;
- `M99_CURRENT_CONTEXT.yaml` — current verified runtime and next target;
- `FEATURE_GAP_REGISTRY.yaml` — normative versus implementation/test status;
- `PROJECT_STATE.md` — current concise project state;
- `CHANGELOG.md` — append-only governance checkpoint record.

No application runtime file is part of this checkpoint.


---

**M99 Knowledge Platform — README v10 — Product truth once. Customer truth once. Verified everywhere. Governed by humans. Implemented without circular redesign.**
