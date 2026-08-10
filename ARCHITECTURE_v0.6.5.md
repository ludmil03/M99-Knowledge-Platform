# M99 Knowledge Platform v0.6.5
## Internal Existing Product Discovery

v0.6.5 is the final read-only discovery gate before the first controlled
publication version.

### Primary change

The owned channel catalogue is now authoritative for the question:
"Does this product already exist in this shop?"

Public search remains secondary evidence only.

Generic API:

`discover_existing_product(channel, canonical_product, candidates)`

The decision engine is platform-independent and supports:
- `EXISTING`
- `NEW`
- `POSSIBLE_DUPLICATE`
- `CONFLICT`
- `NOT_CONFIGURED`
- `ERROR`

### Matching hierarchy

High-confidence identity:
1. manufacturer item/reference;
2. EAN;
3. legacy identifier, including an old MoneyWork/site identifier stored as the
   channel reference/SKU.

Cautious similarity:
4. exact normalized model name + brand;
5. exact normalized model name.

A technical conflict on an exact identifier, such as a different protection
class, becomes `CONFLICT` and cannot be silently updated.

### Existing products

For `EXISTING`:
- existing product ID is preserved;
- existing URL is preserved;
- action becomes `UPDATE_EXISTING_PRESERVE_ID_AND_URL`.

### New products

For `NEW`:
- the result is only `CREATE_CANDIDATE`;
- publication is still disabled in v0.6.5.

### Read-only platform adapters

v0.6.5 adds generic GET-only discovery adapters for:
- ThirtyBees / PrestaShop-compatible Webservice;
- PrestaShop 1.6 Webservice;
- WordPress / WooCommerce REST.

The adapter interface intentionally contains no create/update/delete methods.

Configured channels:
- mela99.com;
- m99.eu;
- rabotni-drehi.com;
- laviro.ro.

Medical-only channels are not relevant for the current Diadora safety-shoe
test product and are therefore not queried by this test.

### Remaining content QA notes cleaned

The content baseline remains v0.6.4.1, but v0.6.5 adds:
- channel-specific meta descriptions rather than nearly identical metadata;
- FAQ question selection adapted to each channel profile/search intent;
- the existing evidence/claim policy remains unchanged.

### Safety

The installer does not perform live HTTP requests.

A separate optional live runner performs GET-only discovery:
`scripts\RUN_V065_LIVE_INTERNAL_DISCOVERY.bat`

Credentials are read only from environment variables and are never written by
this package.

No website writes.
No Dolibarr writes.
No supplier writes.
No publication.

### Next version

v0.6.6 is reserved for the first controlled publication test.

Before allowing a write, v0.6.6 must require:
- successful live internal discovery for the target channel;
- explicit operator approval;
- an exact CREATE-vs-UPDATE decision;
- URL preservation for updates;
- legacy identifier preservation;
- content status `CONTENT_READY`;
- pricing gate approval;
- a single-product scope and rollback/audit record.

The first publication test must not be a bulk publish.
