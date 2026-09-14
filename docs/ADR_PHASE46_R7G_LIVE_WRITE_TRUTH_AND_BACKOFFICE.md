# ADR — Phase 4.6 R7G Live Write Truth Verification and Back Office Handoff

## Problem
R7D displayed `LIVE WRITE VERIFIED` after a POST + one API readback path. The operator then
searched PrestaShop Back Office for the reported product ID and saw no record. A single readback
path is therefore insufficient evidence for business acceptance.

## Decision
R7G separates API-resource verification from human Back Office acceptance.

API truth requires ALL of:
1. direct `GET /api/products/{id}` returns HTTP 200 and exact ID + canonical reference;
2. independent ID-filter query returns exactly the same ID + reference;
3. independent canonical-reference query returns exactly the same ID + reference;
4. hidden-state contract remains `active=0`, `available_for_order=0`, `visibility=none`;
5. optional expected category and price match.

R7G never labels this as full Back Office verification. Successful API verification is shown as
`API RESOURCE VERIFIED — BACK OFFICE ACCEPTANCE PENDING`.

## Back Office button
The private PrestaShop admin path is never hard-coded into source or Git. The operator pastes any
m99.eu Back Office Products URL once. M99 normalizes it to a `{id}` product URL template and stores
the template encrypted with Windows DPAPI. The result and truth-verification pages then expose
`OPEN PRODUCT IN m99.eu BACK OFFICE`.

## Safety
R7G installer and truth verifier are GET-only with respect to m99.eu. No website write, no DB
migration, no product mutation, no image upload, no stock change.


## R7G R2 — CWD-independent test import contract

R7G R1 failed safely during dedicated-test collection because the new test imported `app.*`
while pytest was launched from repository root; `admin-platform` was not on `sys.path`.

R2 treats pytest working directory as an external runtime variable. The dedicated test anchors
repository paths from `__file__`, and the installer also exports `PYTHONPATH=admin-platform`
to pytest subprocesses. A pre-pytest `runpy` import-path probe exercises this exact contract.
No runtime/product behavior or safety gate is weakened.


## R7G R3 — curl-safe filter serialization

All PrestaShop filter queries are serialized with `urlencode`, so curl receives no raw square
brackets. Transport exceptions are classified as blockers and yield `verified=False`.
This fixes the Windows curl exit-code-3 failure without weakening any truth gate.


## R7G R4 — test representation alignment

R3 correctly changed transport representation from raw PrestaShop filter syntax to percent-encoded
curl-safe URLs. Two historical mocks still matched the old raw URL substrings, so they no longer
exercised the intended empty-filter branches.

R4 changes only the test representation contract: mocks now match the percent-encoded runtime URL.
The production verifier and all truth gates remain unchanged. Additional regression tests and an
installer stale-literal audit prevent this class of test drift from recurring.


## R7G R5 — Back Office edit route and known-good structural diagnostics
The observed PrestaShop 9.1.5 Back Office edit route is `/sell/catalog/products/{id}/edit` with a dynamic `_token` query. R5 never persists the query/token. It normalizes only the private admin base plus the edit-route template and adds GET-only target-vs-known-good structural comparison. API truth and Back Office structural warnings remain separate states.
