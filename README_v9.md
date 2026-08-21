# M99 Knowledge Platform — README v9

> **Master System Constitution / Consolidated Project Specification / Current Development State**  
> **Status:** normative master document candidate  
> **Consolidated through:** 2026-08-22  
> **Supersedes when accepted:** README v8  
> **Current development line:** v0.7.3  
> **Next target:** v0.7.3 Phase 2 Revision 1 — Persistent ImportJob + Organization Registry + Live Supplier Browser + Daily Sync + Product Presence + Dolibarr External Availability Warehouses

---

## 0. Purpose and status of README v9

README v9 is the next consolidated Master System Constitution, Current Development State and implementation direction for M99 Knowledge Platform.

It inherits every still-valid normative decision from README v1-v8 and adds the decisions clarified after README v8, especially:
- generalized Operator Product Import Wizard;
- persistent Organization / Supplier / Manufacturer model;
- Live Supplier Browser contract;
- Existing Product Daily Sync contract;
- Product Presence reporting;
- supplier/manufacturer external availability warehouses in Dolibarr;
- strict separation of supplier availability from M99-owned physical stock;
- machine-readable anti-loop governance.

README v9 supersedes README v8 as the current human-readable project constitution once accepted and committed.

The anti-loop rule remains mandatory:
DECIDED is not the same as IMPLEMENTED.
A failed implementation or incomplete prototype does not reopen a DECIDED architecture rule.


## 1. Vision

M99 Knowledge Platform is the central identity, knowledge, evidence, organization, supplier/manufacturer, commercial intelligence, content, SEO, integration, synchronization, publishing and governance layer for the M99 ecosystem.

M99 is the Single Source of Truth for canonical identity and verified product knowledge.
External stores, ERP systems, supplier sites, B2B portals, APIs and legacy systems are sources, mappings, operational systems or destinations. They do not own canonical M99 identity.

Core principles:
- Single Source of Truth.
- Knowledge First.
- No Duplicate Data.
- Evidence Based.
- AI Native, not AI Invented.
- Historical observations are preserved.
- Market and Channel are separate concepts.
- Presence is not Stock.
- Supplier availability is not M99-owned physical stock.
- ERP operates the business but does not own canonical M99 knowledge.


## 2. Canonical product model

Canonical direction:

ProductGroup
→ ProductVariant
→ SupplierOffer / SupplierMapping
→ Evidence / Observations
→ ChannelPresence / ChannelMapping
→ ChannelContent
→ ChannelPrice
→ Inventory / ERP Mapping

External identifiers such as supplier SKU, manufacturer MPN/reference, EAN/GTIN, MoneyWork code, Dolibarr ID, website product ID and marketplace ID are mappings to canonical M99 entities.

Identity resolution:

External Record
→ Import / Observation
→ Normalize
→ Resolve
→ Match
→ Decision
→ Overrides
→ Operator Review
→ Final M99 Identity

Uncertain records must never silently change canonical identity.


## 3. ProductGroup lifecycle and identity

ProductGroup lifecycle is fixed:

draft → active → paused → retired

Physical/hard DELETE remains exceptional and requires explicit human authorization plus typed DELETE confirmation and audit logging.

M99 Reference format is fixed:
M99- + digits only

The permanent M99 identity is independent from:
supplier reference, manufacturer SKU/MPN, EAN/GTIN, MoneyWork code, Dolibarr ID, channel product ID, product title and URL.

Assigned M99 identity is never reused for another ProductGroup.

Identity Before Content:
SELECT → RESOLVE IDENTITY → LINK EXISTING or CREATE PERMANENT M99 ID → THEN CONTENT

Duplicate/identity states:
NEW / EXISTING / AMBIGUOUS / UNRESOLVED

AMBIGUOUS requires human review.


## 4. Organizations, suppliers, manufacturers and brands

Supplier and Manufacturer are roles of a canonical Organization, not mutually exclusive master entities.
One Organization may simultaneously have SUPPLIER and MANUFACTURER roles.

An Organization may own or expose:
- brands;
- public websites;
- B2B portals;
- APIs;
- feeds;
- catalogues;
- documents;
- price lists;
- stock/availability sources.

An operator may propose a new Supplier, Manufacturer or Brand.
The proposal enters:
PENDING_SUPER_ADMIN_APPROVAL

It is not generally visible to operators until approved.

Only Super Admin may:
APPROVE / REJECT / MERGE_WITH_EXISTING / ACTIVATE_ROLE

Brand remains a separate canonical object.


## 5. SupplierSource and connector capabilities

Each approved Organization may have one or more SupplierSource records.

Supported source classes include:
PUBLIC_WEBSITE
B2B_PORTAL
API
CSV
XLSX
XML
JSON
PDF_CATALOGUE
TECHNICAL_DOCUMENT
CERTIFICATE
PRICE_LIST
STOCK_FEED
SIZE_CHART
IMAGE_LIBRARY
MANUAL_VERIFIED_SOURCE

A source declares capabilities such as:
IDENTITY
TECHNICAL_FACTS
MPN
EAN_GTIN
IMAGES
DOCUMENTS
CATALOGUES
PRICE
PURCHASE_PRICE
AVAILABILITY
LEAD_TIME
VARIANTS
STOCK
ORDER_TERMS

B2B/source states:
NOT_CONFIGURED / CREDENTIALS_REQUIRED / CONNECTED / READY / AUTH_FAILED / SESSION_EXPIRED / BLOCKED / VERIFICATION_FAILED

One Organization may expose several sources with different authority. For example, a public website may be best for catalogue structure/images while a B2B source may be authoritative for purchase price and availability.


## 6. Evidence, observations and provenance

Every important fact must retain provenance.

Minimum provenance direction:
source
source_id
source_url or document reference
observed_at
verified_at
reviewer when applicable
conflict_state
document/page when applicable

Source observations do not automatically overwrite canonical truth.

Evidence priority:
exact official manufacturer
→ official documentation/catalogue/certificate
→ validated B2B source
→ exact supplier source
→ verified internal/legacy data
→ operator
→ AI over verified data

AI may transform verified facts but must not invent technical, stock or commercial claims.


## 7. Operator and Super Admin model

OPERATOR is a business user, not a programmer.

The operator must not need to understand:
Python, PowerShell, API, HTTP, JSON, XML, SQL, credentials, database internals or platform-specific technical details.

Operator-first UX is fixed.
One-decision-per-screen is the target interaction model.

Primary operator areas:
Dashboard
Add Products
Supplier Browser
My Tasks
Products
Product Presence
Prices and Availability
Problems to Review
History

SUPER ADMIN manages:
Users/Roles
Organizations
Supplier/Manufacturer approvals
Brands
B2B/Supplier Sources
Knowledge Sources
Channels/ERP
Languages
Pricing/VAT/FX
Identity Registry
Import Presets
Sync Rules
Content Revision Policies
Locked Fields
Quality Gates
Credentials Status
Audit/Logs/Diagnostics
Feature/Gap Registry

Diagnostics and secrets remain outside normal Operator UX.


## 8. Authentication and RBAC

The Admin Platform has its own authentication direction:
username or email + password,
secure password hashing,
session management,
logout,
failed-login throttling/lockout,
session timeout,
login/logout audit,
reset-password workflow,
future 2FA.

Credentials for channels and supplier/B2B systems are never shown to operators.

Permissions are enforced server-side, not only by hiding menu items.

Representative permissions:
product.read
product.create
product.update
product.activate
product.retire
product.delete_approve
import.create_job
import.execute
import.select_targets
supplier.browse
sync.view
sync.run_manual
pricing.view
pricing.approve
channel.<channel>.read
channel.<channel>.write
dolibarr.read
dolibarr.write
users.manage
roles.manage
settings.manage
audit.read


## 9. Generalized New Product Operator Workflow

The primary Add Products workflow is generalized and multi-channel. It is not a button dedicated to m99.eu or any single website.

Target workflow:

Login
→ Add Products
→ Choose Supplier / Manufacturer Organization
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

The normal operator workflow does not depend on URL copy/paste or BAT/Python scripts.


## 10. Direct Supplier Selection

The operator must be able to browse real supplier/manufacturer catalogue data through the M99 Admin Supplier Browser.

Selection modes:
- one exact supplier product;
- multiple selected products;
- one supplier category;
- multiple supplier categories;
- all products from selected category/source where supported;
- first N products;
- only products new to M99;
- manual selection.

The architecture must support 1, 2, 3, 20, 200 or all selected products through the same engine without per-product custom code.

Selection never bypasses:
identity resolution
evidence verification
duplicate/legacy matching
operator authorization
target scope
pricing/VAT
image gate
variant/default-combination gate
language/content gate
TEST/Draft policy
readback
Product Quality Gate


## 11. Live Supplier Browser Contract

A common Supplier Connector Contract is required so that the Admin UI is not redesigned for each supplier.

Conceptual contract:
connect / health_check
list_categories
list_products
get_product
get_variants
get_images
get_commercial_data

The installer does not crawl supplier sites.
The running M99 Admin runtime may perform controlled read-only access to configured SupplierSource records when an authorized operator browses or when scheduled synchronization runs.

Concrete supplier integrations are adapters to this contract, not separate architectures.
STENSO is the planned first reference connector because it has already been used for product/category validation, but the contract must remain generic for PALLTEX, BULTEX and other suppliers/manufacturers.


## 12. ImportJob as a first-class persistent object

Every new-product import is an auditable ImportJob.

Conceptual fields include:
job_id
created_at
created_by
operator_role
source_id
source_type
source_urls
source_categories
selected_products
selected_categories
product_count
requested_targets
authorized_targets
ready_targets
blocked_targets
pricing_policy
content_policy
image_policy
language_policy
dry_run
requires_confirmation
status
started_at
finished_at
result_per_product
result_per_target
audit_log

Repeated workflows may use presets, but a preset can never grant permissions the user does not already have.


## 13. Multi-channel target scope

For NEW PRODUCT IMPORT the operator chooses one or more authorized targets.

WRITE_TARGETS =
REQUESTED_TARGETS
∩ AUTHORIZED_TARGETS
∩ READY_TARGETS

Target states include:
NOT_SELECTED
SELECTED
UNAUTHORIZED
BLOCKED
READY
COMPLETED
FAILED
QUALITY_INCOMPLETE

NOT_SELECTED is different from BLOCKED.

Current web/business scope includes:
mela99.com
rabotni-drehi.com
m99.eu
medicinski-drehi.com
toplinka.com
laviro.ro
alviro.ro
Dolibarr ERP

Dolibarr is not merely another website. Web channels and ERP use different target adapters and different payload contracts.


## 14. Publishing Constitution

Publishing rules remain mandatory:

1. NEW → TEST/Draft first.
2. TEST category is resolved live.
3. Final category is operator-owned.
4. Existing approved Product Name + URL are locked in normal revision.
5. Approved M99 Product Name + URL are locked.
6. Unapproved TEST drafts may be repaired.
7. CREATE and UPDATE are different contracts.
8. Duplicate guard runs before CREATE.
9. Readback is mandatory.
10. HTTP 200/201 is not Product Quality PASS.
11. Front Office verification is required where applicable.
12. Activation requires authorization.
13. DELETE remains explicit human action.

Command-line tools are development/diagnostic tools; normal publishing is initiated from M99 Admin.


## 15. Content, SEO and language governance

A complete product package may contain:
Product Name
H1
short description
long description
H2/H3
technical specifications
materials
sizes
FAQ
Meta Title
Meta Description
SEO keywords
schema
internal links
images
localized ALT

Supplier prose is not copied verbatim. Content is adapted for each market, channel and language from verified facts.

Language Registry is dynamic. Known language scope includes BG, EN, RU, RO, GR and future languages.
Channel language IDs are discovered live rather than assumed.

Field lifecycle:
GENERATED → EDITED → SAVED → REVIEWED → APPROVED

A post-approval change invalidates only the affected field approval.
Image + ALT are reviewed together per language.


## 16. Image governance

Image source priority:
official manufacturer
→ verified supplier
→ verified cached original source

Another M99 channel is not the master image source merely because it already contains the correct image.

Pipeline:
Discover
→ Verify
→ Download
→ Relevance Check
→ Dedupe
→ Resize approximately 1200–1400 px
→ WebP
→ Localized ALT
→ Operator Review
→ Upload
→ Association
→ Readback

Theme assets, logos, cart/search/header icons and unrelated images must be rejected.


## 17. Existing Product Daily Sync — separate operational mode

NEW PRODUCT IMPORT and EXISTING PRODUCT DAILY SYNC are different operational classes and must remain separate.

For existing canonical products, the operator's new-product target selection does not govern daily synchronization.

Every scheduled sync:
1. selects canonical products with verified supplier/source mappings;
2. checks supplier/B2B price;
3. checks supplier availability;
4. checks variants/sizes;
5. checks changed/discontinued state;
6. compares with the last verified observation;
7. performs no write when there is no change;
8. on change, synchronizes only already-existing channel/ERP mappings according to ownership and pricing policies.

Daily Sync never creates a missing product in a channel merely because that channel exists.

DECIDED:
NO_CHANGE → NO_WRITE


## 18. Daily Sync change detection and failure semantics

Minimum change results:
NO_CHANGE
PRICE_CHANGED
AVAILABILITY_CHANGED
VARIANT_AVAILABILITY_CHANGED
PRODUCT_CHANGED
SUPPLIER_DISCONTINUED
VERIFICATION_FAILED

A failed supplier/API/site verification must never be interpreted automatically as:
quantity = 0,
OUT_OF_STOCK,
NOT_PRESENT,
or product discontinued.

The last verified state is preserved and the failure is recorded separately.

Writes are field-scoped and policy-controlled.


## 19. Daily Sync price pipeline

Price change handling follows the approved pipeline:

supplier/source price
→ approved pricing rule
→ market currency
→ channel/market VAT
→ target gross customer price
→ platform NET price if required by the target API
→ controlled API write
→ mandatory readback
→ Front Office gross-price verification where applicable

VAT is channel/market configuration and is not a universal hardcoded constant.

A material change may be routed to NEEDS REVIEW if it violates configured thresholds or approval policy.


## 20. Daily Sync dashboard and audit

Daily Sync is not an invisible script.

The business-first dashboard should expose at least:
Last run
Products checked
Supplier checks
Price changes
Availability changes
Variant changes
Channel writes
Dolibarr writes
NO_CHANGE count
Blocked count
Errors

Central audit/integration logs include:
timestamp
severity
user/system actor
module
operation
entity
supplier/channel
job_id or sync_run_id
result
message
correlation_id

Never log secret values.


## 21. Supplier observations and snapshots

Before a selected supplier record becomes canonical data or a sync write, M99 stores/references an observation/snapshot of what the source reported.

SupplierObservation direction:
source_id
organization_id
supplier_product_reference
supplier_variant_reference
source URL/key
observed_at
verified_at
price/currency when available
availability
exact_quantity when genuinely exposed
variant availability
discontinued state
changed fields
provenance/conflict metadata

This allows the system to explain what changed, when it changed and from which verified source.


## 22. Supplier availability versus physical stock

Supplier availability is distinct from M99-owned physical stock.

Visible size is not stock.
Supplier availability is not M99/Dolibarr physical stock.

M99 physical stock in Dolibarr follows operational warehouse events:
Supplier order → reception → physical stock increase.
Customer order → shipment → physical stock decrease.

Stock is variant-aware.

Supplier availability may be exact quantity or qualitative status. M99 must not invent a number when the source exposes only a status.


## 23. Dolibarr external supplier/manufacturer warehouses — new decision

For approved Supplier/Manufacturer Organizations, M99 may create and maintain dedicated external availability warehouses in Dolibarr.

Example:
M99 CENTRAL / M99 PHYSICAL
STENSO — EXTERNAL
PALLTEX — EXTERNAL
BULTEX — EXTERNAL
DIADORA — EXTERNAL
PUMA SAFETY — EXTERNAL

Warehouse ownership/type must distinguish at minimum:
M99_PHYSICAL
SUPPLIER_EXTERNAL
MANUFACTURER_EXTERNAL

A quantity in a SUPPLIER_EXTERNAL or MANUFACTURER_EXTERNAL warehouse represents the latest verified external supplier/manufacturer availability. It never means that M99 owns that quantity.

External warehouse availability is variant-aware.

If the supplier provides an exact quantity, the exact verified quantity may be reflected.
If the supplier provides only qualitative state, M99 stores the state without inventing a number.

Recommended qualitative states:
EXACT_QUANTITY
IN_STOCK
LOW_STOCK
OUT_OF_STOCK
ON_REQUEST
UNKNOWN
VERIFICATION_FAILED

If source verification fails, the previous verified external availability is retained and marked with verification failure; it is not automatically zeroed.


## 24. Multiple suppliers for one canonical product

One canonical M99 Product may have multiple SupplierMappings and ManufacturerMappings.

Example:
M99 Product
├─ STENSO mapping
├─ PALLTEX mapping
└─ official Manufacturer mapping

Therefore availability can differ by source:
STENSO EXTERNAL = 0
PALLTEX EXTERNAL = 17
M99 PHYSICAL = 2

The canonical identity remains one product.
Supplier mapping is not canonical identity.

Future procurement intelligence may use this structure for:
preferred supplier,
best purchase price,
backup supplier,
availability fallback,
purchase recommendation.

Those advanced procurement decisions remain later scope unless separately approved.


## 25. Product Presence Registry and channel mapping

Every canonical M99 product must answer:
In which website(s)/ERP is this product present, and where is it missing?

Presence is separate from stock availability.

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

Each Product ↔ Target mapping should retain:
M99 product ID
target/channel
channel product ID
channel variant IDs/mappings
URL
presence status
publication state
channel price
currency
stock representation/status
last_verified_at
last_sync_at
VAT/gross verification
sync ownership
readback state
Front Office verification
last error


## 26. Product Presence reports — new decision

M99 provides bidirectional Product Presence reporting.

A. Product → Channels / ERP
For one product, show every configured target and whether the product is present, missing, draft/test/active/paused/retired, last verified, last synced and whether there is an error.

B. Channel → Products
For one selected channel, show all mapped M99 products and their publication/presence state.

C. Missing mappings
Show products missing from one or more selected channels.

D. Dolibarr mapping report
Show products not mapped to Dolibarr and mapping/operational state.

The UI provides FAST and LIVE VERIFY modes.

FAST uses the last verified Product Presence Registry state.
LIVE VERIFY checks selected target systems in real time.

A temporary target/API failure must not convert a previously verified PRESENT record into NOT_PRESENT. It becomes PRESENT_LAST_VERIFIED / VERIFICATION_FAILED according to the exact condition.


## 27. Unified Product Availability view

A product detail view should combine, without mixing ownership:

WHERE IT IS SOLD
- per-channel Presence and publication status;

M99 OWN STOCK
- physical, variant-aware Dolibarr stock;

SUPPLIER/MANUFACTURER AVAILABILITY
- per external source / external Dolibarr warehouse;
- exact quantity when verified;
- otherwise qualitative availability status;
- last verified timestamp.

This gives operators one business view while preserving semantic separation between presence, owned stock and external availability.


## 28. Dolibarr role and target contract

M99 owns canonical identity, knowledge and governance.
Dolibarr is the operational ERP/CRM/warehouse representation.

Dolibarr is not treated as another web shop.

Web channel payload may include:
identity mapping
name/content/SEO
categories
images
variants
price/tax
publication state

Dolibarr payload may include:
canonical M99 identity
supplier mapping
supplier reference
EAN/GTIN
cost/purchase data
selling price policy
variants
warehouse master data
stock ownership
product lifecycle
counterparties/mappings

The orchestration engine chooses the target adapter based on target type.


## 29. Existing Product and Category Content Revision

Existing Product Content Revision is a distinct operational class.

Selection may include:
one product
multiple products
category
brand
weak-SEO products
incomplete-content products

Normally locked during ordinary content revision:
M99 ID
Product Name
URL/slug
Channel Product ID

Editable:
short/long descriptions
H2/H3
technical specifications
materials
FAQ
Meta Title
Meta Description
SEO keywords
schema
internal links
image ALT

Existing Category Content Revision supports:
one category
multiple categories
category + subcategories
all categories in a selected channel

Normally locked:
M99 Category ID
Channel Category ID
Existing Category Name
Existing URL/slug
Parent relationship

Structural/identity migrations are separate Super Admin operations.


## 30. Operational classes

M99 keeps these operational classes distinct:

A. NEW PRODUCT IMPORT
B. EXISTING PRODUCT DAILY SYNC
C. MANUAL / EXCEPTIONAL REPAIR
D. EXISTING PRODUCT CONTENT REVISION
E. EXISTING CATEGORY CONTENT REVISION
F. KNOWLEDGE / EVIDENCE ACQUISITION

Manual / exceptional repair is controlled:
exact target,
exact allowed fields,
explicit confirmation,
mandatory readback,
no broad side effects.


## 31. Product Quality Gate

Critical quality areas include:
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

A numeric quality score can never override a failed critical gate.


## 32. Variants and default combination

Sizes are variants when product logic requires them.

A variational product must have exactly one default combination.
For PrestaShop-like targets, cache_default_attribute must point to that default combination.

Failure blocks Product Quality PASS.

Universal Variant SKU standard and universal ProductGroup-versus-colour boundary remain OPEN unless resolved by a later ADR.


## 33. m99.eu verified integration state

m99.eu runs PrestaShop 9.1.5.

Verified classic Webservice endpoint:
https://m99.eu/api

Verified active languages:
1 = English
2 = Bulgarian
3 = Russian

Controlled test category currently used by the integration:
ID 26

Verified:
products GET permission = true
products POST permission = true

Minimal multilingual dry-run contract has been validated with:
numeric-only M99 reference,
category 26,
active = 0,
available_for_order = 0,
visibility = none,
EN/BG/RU localized fields,
category-only association,
no empty placeholder image/combination/stock associations.

This proves the adapter contract. It does not make m99.eu the central operator workflow.


## 34. Current development state

Verified milestones:

v0.7.1 SAFE Revision 7
- 234 tests passed.
- local commit: 8c3d2d7fc729f22001c320d1fa033528272eb21e.

v0.7.2 Phase 1 — Canonical Data Model Foundation
- full regression PASS.
- commit: 193b6bcc6c8f4b13439102a99f00d1b542b1851f.

v0.7.2 Phase 2 — SQLAlchemy + Alembic baseline
- persistence/migration gates PASS.
- real Admin DB intentionally not migrated by installer.

v0.7.2 m99.eu publisher line
- corrected to PrestaShop 9.1.5;
- Python import-path fix;
- live preflight PASS;
- multilingual minimal-payload dry run PASS;
- Revision 5.2 Fix 1 commit: 5705bff675224748f95f58cbf5860b0bb761f972.

v0.7.2 Phase 3 Fix 1
- Admin UI bridge technical prototype;
- Python 3.14 import-test compatibility;
- full regression PASS;
- commit: ec0cc276bdf235868f74df52aaf62c6421d3b32d.
- dedicated m99.eu screen is not final operator UX.

Governance Consolidation
- Decision Registry / Feature-Gap Registry / Current Context / ADR-0001 created;
- full regression PASS;
- commit: 5aec1b40ddcc6f1498512dde9eb7da6b0d18bca8.

v0.7.3 Operator Product Import Wizard Foundation
- generalized Add Products foundation;
- Supplier/Manufacturer proposal gate;
- one/many/all product/category selection foundation;
- one/many target selection;
- identity-before-content gate;
- no external write;
- full regression PASS;
- commit: e25e1e9a9623df6e418e89cf997e07ae653ddf3f.

v0.7.3 Phase 2 initial package
- persistence-oriented package was generated but its Supplier Browser scope was recognized as insufficient before adoption because it did not yet provide live supplier catalogue browsing.
- the design direction is superseded by Phase 2 Revision 1 scope described below.


## 35. v0.7.3 Phase 2 Revision 1 target scope

Target milestone:

M99 v0.7.3 Phase 2 Revision 1
Persistent ImportJob
+ Organization Registry
+ Live Supplier Browser Contract
+ Daily Existing Product Sync Contract
+ Product Presence Registry
+ Dolibarr External Supplier/Manufacturer Availability Warehouses

Core architecture:

Organization
→ SupplierSource
→ Connector
→ Categories / Products / Variants
→ Operator Selection
→ Source Snapshot / Observation
→ ImportJob
→ Identity Resolver
→ Target Scope
→ Preparation / Preflight
→ TEST/Draft publishing

Parallel scheduled path:

Verified Supplier Mapping
→ Daily live observation
→ Compare last verified state
→ ChangeSet
→ Pricing / availability / ownership policy
→ Existing channel/ERP mappings only
→ controlled write
→ readback
→ Front Office verify
→ audit

External availability path:

Supplier/Manufacturer Observation
→ Supplier/Manufacturer external Dolibarr warehouse mapping
→ exact quantity or qualitative availability
→ variant-aware readback
→ audit


## 36. Admin Platform direction

The Admin Platform remains the intended operator surface.

Visual language may be familiar to PrestaShop/commerce users, but the workflow is simpler and business-first.

UI requirements:
- hide API internals/credentials from operators;
- business decisions rather than transport details;
- progressive wizard steps;
- READY / BLOCKED / NEEDS REVIEW in plain language;
- one/many products/categories and one/many targets;
- Product Presence and supplier availability views;
- Daily Sync dashboard;
- diagnostics reserved for Super Admin;
- reuse tested service/adapter layers instead of duplicating integration logic in templates/routes.


## 37. SAFE development and Git governance

Controlled development remains mandatory:

known Git baseline
→ clean working tree
→ controlled patch/installer
→ dependency verification
→ Python compile
→ dedicated tests
→ full pytest regression suite
→ exact changed-file review
→ explicit COMMIT
→ no automatic Push
→ report review
→ Push
→ synchronization verification

Failed gates roll back to the known baseline.
Tests are not weakened merely to obtain a green release.


## 38. Machine-readable anti-loop governance

Before any new architecture proposal or reopening a design question:

DECISION_REGISTRY
→ M99_CURRENT_CONTEXT
→ PROJECT_STATE
→ latest master README
→ relevant ADR
→ relevant tests / implementation history
→ only then a new proposal

Interpretation:
DECIDED + NOT_IMPLEMENTED → implement; do not redesign.
IMPLEMENTED + NOT_TESTED → test; do not invent a new architecture.
TESTED → preserve until explicitly superseded.
SUPERSEDED → do not propose as current design.
OPEN / DEFERRED → may be discussed.
Failed implementation does not reopen DECIDED.

README v9 is accompanied by an updated replacement DECISION_REGISTRY.yaml containing previously missing decisions.


## 39. Fixed decisions newly added to Decision Registry by README v9

The updated registry explicitly records decisions that were present in README/history or were clarified after v8 but were not present in the first machine-readable registry.

Newly recorded areas include:
- server-side RBAC/action enforcement;
- operational class separation;
- manual repair contract;
- Product/Category content revision locks;
- dynamic language registry/live language IDs;
- content field lifecycle;
- full image pipeline;
- Product Quality critical-gate rule;
- web-channel versus Dolibarr target-contract separation;
- live Supplier Connector contract;
- SupplierSource observation/provenance;
- daily sync existing-mappings-only rule;
- daily change-state contract;
- verification-failure semantics;
- daily sync dashboard;
- price synchronization pipeline;
- bidirectional Product Presence reports;
- FAST versus LIVE VERIFY behavior;
- multiple supplier mappings per canonical product;
- Dolibarr supplier/manufacturer external availability warehouses;
- external warehouse stock-ownership separation;
- no invented supplier quantity;
- variant-aware supplier external availability.


## 40. Genuine OPEN / DEFERRED items

Remain open/deferred unless explicitly resolved later:
- universal ProductGroup versus colour-variant boundary;
- universal Variant SKU standard;
- exact Dolibarr parent/variant implementation;
- exact image-rights contract per source;
- production Vault deployment;
- exact WordPress commerce adapter details per site;
- 2FA rollout timing;
- supplier-specific technical connector mechanics beyond the common contract;
- advanced procurement recommendation / preferred supplier algorithm;
- exact policy thresholds for auto price update versus NEEDS REVIEW;
- production scheduling technology for Daily Sync;
- final production migration of new v0.7.3 persistence tables.


## 41. Next implementation priority

Do not build additional isolated site-specific screens.

Next implementation target is v0.7.3 Phase 2 Revision 1.

Priority:
1. Update machine-readable governance to README v9 decisions.
2. Persistent Organization / roles / approval registry.
3. Persistent SupplierSource registry.
4. Common Live Supplier Connector Contract.
5. First read-only reference connector (STENSO).
6. Direct category/product browse in Operator UI.
7. Persistent SupplierObservation / source snapshots.
8. Persistent ImportJob linked to observations.
9. Product Presence / Channel Mapping persistence and report.
10. Daily Existing Product Sync models and compare engine.
11. Dolibarr ExternalWarehouseMapping and availability ownership model.
12. Temporary DB/Alembic migration gate before any real production DB migration.
13. Super Admin approval/configuration screens.
14. Identity Resolver integration.
15. Live per-channel preflight.
16. Only after those gates: controlled TEST/Draft publishing from the generalized wizard.


## 42. Definition of success

Single product:
exact identity, evidence, supplier mappings, pricing/FX/VAT, localized content, technical facts, images/ALT, variants, TEST/Draft, readback, operator-ready and no invented claims/stock.

Bulk:
the same engine handles 10–20 products first, then 100–200 and larger selections without per-product custom code.

Supplier Browser:
a non-programmer chooses a supplier, browses real categories/products and selects them without copying URLs or running scripts.

Daily Sync:
existing mapped products are checked daily, NO_CHANGE causes NO_WRITE, changes are policy-controlled, missing channel products are not auto-created, verification failures do not become false zero/out-of-stock states.

Inventory:
M99-owned physical stock and supplier/manufacturer external availability are both visible but never semantically mixed.

Presence:
the system can answer Product → Channels and Channel → Products, including missing mappings and verification state.

Governance:
already-decided rules are not repeatedly reopened; implementation follows Decision Registry, Current Context, README, ADRs and tests.


## 43. Final architecture philosophy

M99 Knowledge Platform is one governed system:

KNOWLEDGE
+ EVIDENCE
+ IDENTITY
+ ORGANIZATIONS
+ BRANDS
+ SUPPLIER SOURCES
+ B2B
+ COMMERCIAL INTELLIGENCE
+ CONTENT
+ ERP / CRM
+ PHYSICAL STOCK
+ EXTERNAL SUPPLIER AVAILABILITY
+ PRODUCT PRESENCE
+ MULTI-CHANNEL PUBLISHING
+ DAILY SYNC
+ QUALITY GATES
+ AUDIT / LOGS
+ HUMAN GOVERNANCE
+ MACHINE-READABLE PROJECT MEMORY

Product truth once.
Customer truth once.
Verified everywhere.
Supplier availability visible without pretending it is owned stock.
Governed by humans.
Implemented without circular redesign.

---

**M99 Knowledge Platform — README v9 — Product truth once. Verified everywhere. Supplier availability visible without pretending it is owned stock. Governed by humans.**
