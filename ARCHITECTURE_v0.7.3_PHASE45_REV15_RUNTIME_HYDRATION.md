# M99 v0.7.3 Phase 4.5 Revision 15 — STENSO Live Hydration Runtime Fix

Real runtime gate:
- active GUI must not show `(title pending product read)`;
- active GUI shows image, name, STENSO ref, price, availability, variants, specs and description;
- 0 products selected by default;
- hydration FAIL rows cannot be selected;
- DRAFT disabled until hydrated selection;
- create-job re-verifies selected supplier URL;
- manufacturer enrichment remains available after supplier hydration.

First live test: select exactly ONE hydrated STENSO product and compare it visually with the supplier page before DRAFT.
