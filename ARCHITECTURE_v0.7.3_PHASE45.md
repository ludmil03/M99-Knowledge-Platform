# M99 v0.7.3 Phase 4.5 Revision 2 — Operator Product Quality Gate + Daily Sync Foundation

## Core rule
Real Write PASS is not Product Quality PASS.

## Successful real product lifecycle
Supplier source
→ M99 import
→ channel CREATE inactive/hidden
→ API READBACK
→ automated transport/content checks
→ OPERATOR REVIEW
→ APPROVED
→ KEEP PRODUCT
→ DAILY SYNC BASELINE
→ daily price/availability/variant observation
→ DIFF
→ controlled update/readback in the next sync-write milestone.

## Operator review
The operator verifies the actual product, including:
- product name / page H1;
- logical H2/H3/H4 hierarchy where justified;
- short/long descriptions;
- specifications and standards;
- price, category, manufacturer/brand;
- variants/sizes;
- images and ALT text;
- Meta Title / Meta Description;
- slug;
- all active languages;
- Back Office and Front Office rendering.

## Rejection
REJECT does not automatically delete evidence.
The product remains available for diagnosis.
Operator chooses FIX & RETEST or DELETE.

## Daily sync policy
Dynamic commercial fields:
- price;
- supplier availability;
- variants/sizes availability.

These are candidates for automatic synchronization after the write/readback sync gate is proven.

Content-governed fields:
- names;
- descriptions;
- specifications/features;
- images;
- SEO metadata;
- slugs.

Supplier changes to these fields create CONTENT CHANGE DETECTED → OPERATOR REVIEW.
They must not silently overwrite approved M99 content.

## Safety
The SAFE installer performs no external HTTP.
The REAL TEST launcher performs controlled live access.
A successful m99.eu product is retained for operator review and later monitoring.
Dolibarr remains disposable CRUD because the current Dolibarr target is a test environment.


## Revision 4 — Graphical Real Test Center

Operational real tests move into the M99 Admin UI.

Route:
`/operator/real-tests`

The operator can:
- run local persistence validation;
- run STENSO live read-only validation;
- create/read back a real inactive m99.eu product;
- run Dolibarr TEST CRUD;
- inspect real-test results;
- approve or reject the retained m99.eu product;
- see Daily Sync readiness.

Scripts remain implementation/backend tools only. They are not the target operator UX.
