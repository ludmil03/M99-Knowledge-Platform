# M99 v0.7.3 Phase 4.5 Revision 29
## Stable Baseline Lock + Canonical Product Preview

Baseline:
Revision 28R1 / proven Revision 24R2 runtime.

Existing runtime behavior intentionally unchanged:
- /supplier-browser/inspect
- progressive hydration queue concurrency = 4
- exactly one create-job form
- supplier URL re-verification before DRAFT
- Preflight flow
- manufacturer-start / manufacturer-review

Revision 29 adds only:
- pure canonical_preview service
- GET /supplier-browser/canonical-preview
- read-only Canonical Product Preview template
- one preview link visible only after product hydration PASS

Preview separates:
1. Supplier Evidence
2. M99 Canonical Draft
3. m99.eu Content/SEO Preparation
4. Quality Gate

Final English content is NOT generated in this revision.
Website write allowed = False.

No migration. No product/channel write. No commit. No push.
