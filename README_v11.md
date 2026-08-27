# M99 Knowledge Platform — README v11
Date: 2026-08-27
Governance Checkpoint v11 — Operator Source Registry, Discovery and Canonical Category Governance

## Frozen baseline
Rev29R3.2R2 remains the frozen tested runtime baseline. Revision 30 passed automated installer gates but is not promoted to the frozen tested baseline here. This checkpoint changes governance documents only: no runtime, migration, DB, website, channel, commit or push.

## Next milestone
M99 v0.7.3 Phase 4.5 Revision 31 — Supplier & Manufacturer Registry + Category/Search Browser Foundation.

Target operator flow:
Approved Supplier -> Browse Categories OR Search Products -> Discover one/many/all -> Hydrate -> Select -> Manufacturer Match/Enrichment -> Canonical Preview -> Operator Approval -> DRAFT/target preparation.

## SRC-APPROVAL-001
Operators may PROPOSE Suppliers and Manufacturers. Until Super Admin APPROVES, nobody may use them operationally. Super Admin alone APPROVES/REJECTS. REJECTED proposals are hidden from normal operators, retained in audit, and may be proposed again as a NEW proposal linked to history. Duplicate proposals for an already APPROVED source are blocked.

## SRC-ADMIN-001
Only Super Admin may edit an APPROVED Supplier/Manufacturer, change its domain, activate or deactivate it. Domain changes preserve history and require validation. DEACTIVATED is not deleted: evidence/mappings/audit remain; no new operational source use starts; channel products are not automatically deactivated.

## MAP-MFG-001
Every Operator may create, correct or remove Manufacturer <-> Supplier Product links. Every change is audited with actor, time, operation, supplier product, manufacturer/product, previous/new value, result and correlation identifier. Ambiguous matches remain REVIEW_REQUIRED. Super Admin retains override authority.

## CAT-GOV-001
Operators may map Supplier Categories only to APPROVED M99 Canonical Categories. Operators may PROPOSE a new Canonical Category, but only Super Admin creates/approves it for general use. Rejected proposals are hidden from normal selection, retained in audit and may be proposed again. Supplier taxonomy and canonical taxonomy remain separate.

## DISCOVERY-001
Approved supplier workflow supports category/subcategory browsing and product search by available title/name, supplier SKU/reference, EAN/GTIN, manufacturer model/code, keyword and URL. Operators can discover one, many or all products from a category.

## BULK-001
All-products-in-category is discovery/selection, never direct publishing:
Discover Category -> show scope/count -> hydrate/list -> explicit individual/many/Select All -> operator confirmation -> ImportJob preparation.
Default selection remains ZERO. First live validation of new connector/behavior remains exactly ONE product.

## Product/source rules
One canonical M99 product may have multiple supplier mappings/offers. A Supplier Product normally resolves to one exact Manufacturer Product; competing matches stay REVIEW_REQUIRED. Official manufacturer/documentation governs technical evidence; supplier governs supplier price, availability and offered variants; provenance is preserved.

## Revision 30 boundary
Useful Rev30 concepts remain: source-role separation, provenance, conflict -> REVIEW_REQUIRED, no AI fact invention, final EN/SEO gated by evidence, website write blocked. Manual manufacturer URL entry is not the target primary operator workflow; Revision 31 integrates evidence into approved registries/discovery.

## Carry-forward README v10
All 14 v10 mandatory clarifications remain in force with their real prior implementation/test states. Rev29R3.2R2 remains frozen; zero-selection, one-product validation, hydration-before-selection, STENSO supplier-only semantics, read-only Canonical Preview, supplier evidence != canonical truth, evidence/image/content gates, Daily Sync separation and machine-readable governance remain protected.

## Anti-loop
DECISION_REGISTRY -> M99_CURRENT_CONTEXT -> PROJECT_STATE -> README_v11 -> ADR -> tests/history -> implementation.
DECIDED but not implemented means implement it, not redesign it. TESTED behavior remains protected until explicitly superseded.

Governance files: README_v11.md, DECISION_REGISTRY.yaml, M99_CURRENT_CONTEXT.yaml, FEATURE_GAP_REGISTRY.yaml, PROJECT_STATE.md, CHANGELOG.md.
