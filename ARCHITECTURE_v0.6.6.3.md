# M99 Knowledge Platform v0.6.6.3
## Duplicate Resolution & Existing Master Selection

Target product:
- Diadora Utility GLOVE A.BOX LOW PRO S3S
- M99 100017
- manufacturer item 701.183119_80013
- channel mela99.com

v0.6.6.2 found three live internal candidates:
- 2076
- 2100
- 2147

v0.6.6.3 does not auto-merge and does not auto-delete.

### GET-only duplicate analysis

The system reads the complete current product XML for each candidate and
summarizes:
- product ID;
- current reference;
- EAN;
- active state;
- price;
- default category;
- date_add/date_upd;
- BG/EN names;
- BG/EN link_rewrite;
- descriptions;
- category associations;
- combination count;
- image count.

These signals are added to the review ranking only. Ranking never confirms
identity automatically.

### Master selection

Before a candidate may become the update target, an operator must choose its
product ID and type the exact confirmation:

`CONFIRM MASTER <PRODUCT_ID> M99 100017 MELA99`

After confirmation the selected candidate becomes:
`EXISTING_CONFIRMED`.

Protected master identity:
- product ID: KEEP;
- current product name: KEEP_BY_DEFAULT;
- slug/link_rewrite: KEEP;
- URL: KEEP;
- current reference: KEEP_AS_LEGACY_UNLESS_OPERATOR_MIGRATES.

A later operator-approved proven-better name may change the displayed name,
but never changes the preserved URL automatically.

### Other duplicate candidates

All non-master candidates become:
`DUPLICATE_REVIEW`.

They are not automatically:
- deleted;
- disabled;
- retired;
- redirected;
- merged.

Any future deletion still requires the existing M99 literal DELETE operator
policy. SEO redirect/retirement decisions require a separate review.

### Safety

This version performs GET-only duplicate analysis and local master selection.
No website write.
No Dolibarr write.
No supplier write.

After the master is confirmed, the next controlled action may be a
WRITE_DRAFT update only against that confirmed master.
