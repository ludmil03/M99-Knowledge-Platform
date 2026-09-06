# Revision 31 Phase 4.3 R3.7 — Identity → DRAFT ImportJob → Targets → Canonical Preview

R3.7 connects the browser-accepted Add Products hydration to the already
existing stable identity, DRAFT ImportJob and canonical preview services.

Operator flow:
1. Hydrate supplier product in Add Products.
2. Explicit PREPARE button — read/verify only.
3. Show authorized first-live target (`m99eu`) and operational source bridge.
4. Explicit operator confirmation:
   - server rehydrates source evidence;
   - existing Identity Resolver runs first;
   - AMBIGUOUS/UNRESOLVED stops;
   - NEW/EXISTING may create exactly one DRAFT ImportJob;
   - no publish.
5. DRAFT-created screen.
6. Canonical Preview rehydrates through the approved source-specific connector
   and calls the existing `prepare_canonical_preview` service.

Safety:
- no hidden DRAFT on hydrate or PREPARE;
- exactly one selected product in this revision;
- only m99.eu is allowed as first-live target;
- no PrestaShop write/publish;
- no stock/Dolibarr write;
- supplier availability stays external supplier evidence;
- no DB migration;
- no automatic creation of source/Supplier bridge;
- if approved source cannot be mapped to an existing operational Supplier
  record by domain, DRAFT is blocked visibly;
- no commit/push.

This revision intentionally does not redesign proven Hydration, Identity,
DRAFT ImportJob or Canonical Preview semantics.
