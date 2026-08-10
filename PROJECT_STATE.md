

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


# v0.5.6.2 — Bultex Live Launcher Fix

Fixes the Windows launcher failure:

`ModuleNotFoundError: No module named 'integrations'`

## Cause
The live test script was started in a context where Python treated `scripts/`
as the import root. Therefore the repository root containing `integrations/`
was not guaranteed to be available on `sys.path`.

## Fix
- `RUN_BULTEX_LIVE_READ.bat` resolves and changes to the repository root.
- PowerShell runner explicitly sets the repository root in `PYTHONPATH`.
- Live test is started as a module:
  `py -3 -m scripts.test_bultex_live_read`
- `scripts/__init__.py` makes operational scripts an explicit package.
- Regression tests verify launcher behavior.

Credential behavior is unchanged:
credentials exist only in the current PowerShell process and are cleared after
the test.

No Dolibarr, basket, order or website write capability is added.


# v0.5.6.3 — Bultex Login Discovery Diagnostics

The live test reached the real B2B portal but discovery failed because the
portal did not expose a standard `<input type="password">` in the returned HTML.

This release adds a diagnostics-only mode.

## What it does
- GET `/pap/login.php`
- optionally preserves the portal's `CNum` URL shape
- lists form action/method
- lists field names and input types
- reports whether fields have values, but NEVER prints those values
- lists script sources
- lists inline JavaScript function names
- lists query parameter names with values redacted

## What it does NOT do
- no credential submission
- no login attempt
- no cookies/session IDs printed
- no basket/order/document writes
- no Dolibarr writes
- no website writes

Run after installation:

`scripts\RUN_BULTEX_LOGIN_DIAGNOSTICS.bat`

Send only the diagnostic output.


# v0.5.6.4 — Bultex Login JavaScript Discovery

The portal login diagnostics established:
- form method = GET
- action = /pap/login.php
- CNum is a named field
- username/password field names are dynamically generated
- both are type=text
- onsubmit = checkit()

This release inspects the login JavaScript only.
It reports ordered field names, visible labels, the checkit() function body,
referenced login field names and helper scripts checked.

No credentials are requested and no login is attempted.


# v0.5.6.5 — Bultex Safe Live Authentication

Login mechanism is now evidence-based from the real portal JavaScript:

- method: GET
- action: `/pap/login.php`
- client field: `CNum`
- username field: dynamically discovered `edaderpu_<hash>`
- password field: dynamically discovered `edaderpp_<hash>`
- submit action: `act=li`
- onsubmit validator: `checkit()`

The client discovers dynamic field names on every login attempt instead of
hard-coding their hashes.

After login, the client is allow-listed to read only:
`/pap/minfo.php?i=<numeric_product_id>`

There are no methods for basket, ordering, documents, Dolibarr writes or
website/channel writes.

Credentials remain process-only and are cleared after the test.


# M99 Knowledge Platform v0.6.0
## Multi-Channel Product Acquisition Pipeline

Canonical flow:

Manufacturer → Supplier Offer → M99 ProductGroup → ProductVariant → Dolibarr → Channel Assignment → Channel Content/SEO/Price → Publication

### Binding rules
- M99 is the canonical product identity.
- Human-readable M99 IDs use `M99 ` followed by digits.
- Existing MoneyWork, supplier, Dolibarr and website identifiers remain mappings and are preserved.
- ProductGroup lifecycle: `draft → active → paused → retired`.
- Deletion is exceptional and requires operator approval plus literal `DELETE`.
- Size/color/width/etc. are variants of one product model, not independent ProductGroups.
- Existing website URLs are protected.
- Existing SEO/content is replaced only when evidence shows the new version is better.
- New ProductGroup first publication requires operator approval.
- Supplier offers are separate from product identity and may coexist for multiple suppliers.
- Stenso target price: 1.5% below Stenso public price, never below the configured acquisition floor.
- Supplier availability may feed sellable availability; ownership rules remain separated from channel content.
- Dolibarr remains the operational stock/ERP target; M99 remains the product/knowledge master.

### Channel scope
- mela99.com: workwear, safety, medical, HORECA, hotel, restaurant, SPA/wellness, beauty and related professional categories.
- m99.eu: same broad professional scope.
- rabotni-drehi.com: workwear/safety plus medical clothing, clogs/shoes, HORECA, hotel, restaurant, SPA/wellness and beauty.
- medicinski-drehi.com: medical products only.
- laviro.ro: broad professional scope including medical and HORECA.
- alviro.ro: medical plus HORECA/hotel/restaurant/SPA/beauty; industrial-only products are excluded.

### Content
Each channel owns its own language, title, description, H1/H2/H3, metadata, FAQ, image ALT text and category mapping. Content is not copied blindly between sites.


# M99 Knowledge Platform v0.6.1
## Product Acquisition Preview Pipeline

Flow:
Structured Source JSON → validation → M99 ProductGroup draft → variants →
supplier offers → channel eligibility → channel preview → operator review.

This release is PREVIEW_ONLY. It performs no Dolibarr, supplier, or website
writes. Existing channel IDs and URLs are preserved in the preview. All channel
records remain REVIEW with publish_allowed=false until an operator approves
them. Sizes/colors remain variants of one ProductGroup.

The sample fixture is synthetic and exists only for smoke testing; it is not
supplier or manufacturer data.


# M99 Knowledge Platform v0.6.2
## Real Product Evidence Pipeline

First real product:
Diadora Utility GLOVE A.BOX LOW PRO S1PS
Manufacturer item: 701.183121_80013
Colour: BLACK
EU sizes: 35-48

The exact manufacturer page is authoritative identity evidence.

A public Stenso product with a similar GLOVE A.BOX LOW PRO name was found, but
it is classified S3S and uses supplier reference 06100768. It is therefore
stored only as a supplier candidate and MUST NOT auto-merge with the exact
Diadora S1PS product.

Rules introduced:
- exact manufacturer item match is authoritative;
- supplier near-match is candidate-only;
- conflicting protection class blocks auto-merge;
- operator review is mandatory for unresolved supplier mapping;
- no website or Dolibarr write is enabled.
