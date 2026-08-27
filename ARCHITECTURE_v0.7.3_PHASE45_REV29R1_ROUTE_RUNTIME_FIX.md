# Revision 29R1 — Canonical Preview Route Runtime Fix

Observed live defect:
GET /supplier-browser/canonical-preview returned HTTP 404 even though Revision 29
source/static tests contained the route.

Fix:
- add a dedicated canonical_preview_runtime router;
- explicitly register that router in app.main;
- verify the route from the imported FastAPI app.routes table after install;
- keep Rev28R1 hydration, DRAFT, Preflight and manufacturer flows unchanged.

No website write. No migration. No commit. No push.
