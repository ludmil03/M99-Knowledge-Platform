# M99 v0.7.2 Phase 3 — Admin UI → m99.eu PrestaShop Publisher

Browser
→ M99 Admin Panel
→ FastAPI product_publish router
→ m99eu_publish_service
→ existing integrations/m99eu_prestashop
→ PrestaShop 9 Webservice

Operator flow:
Products → m99.eu → PREFLIGHT → DRY RUN → explicit approval
→ CREATE INACTIVE → READBACK → result.

The UI reuses the existing Admin design and the existing tested publisher.

Safety:
- fail-closed authentication check;
- explicit operator approval;
- exact CREATE_INACTIVE confirmation;
- active=0;
- TEST category;
- live language discovery;
- numeric-only M99 reference;
- mandatory readback;
- installer itself performs no network call.

Phase 3 Fix 1:
The production implementation is unchanged in behavior.
Only the offline import test harness is adapted for Python 3.14 by registering
the dynamically loaded module in sys.modules before exec_module().
