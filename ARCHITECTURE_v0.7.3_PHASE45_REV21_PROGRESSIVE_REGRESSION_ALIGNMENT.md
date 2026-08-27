# M99 v0.7.3 Phase 4.5 Revision 21 — Progressive Hydration Regression Alignment

## Revision 20 result
Dedicated tests stopped on one obsolete Revision 15 assertion.

The old contract expected the Jinja template to contain:
`hydration_status != 'PASS'`

Revision 20 intentionally moved this gate to progressive runtime behavior:
- category renders immediately;
- product row starts WAITING;
- checkbox starts disabled;
- browser hydrates the product through `/supplier-browser/hydrate-product`;
- checkbox becomes enabled only when returned hydration status is PASS.

## Revision 21
No functional performance logic changes.

This revision:
- updates the old Revision 15 regression test to the progressive runtime contract;
- adds a dedicated Revision 21 guard for:
  - WAITING -> disabled;
  - PASS -> enabled;
  - 4-worker hydration queue;
  - local hydrate endpoint;
  - 10-minute runtime cache;
  - zero selected by default;
  - DRAFT supplier URL re-verification.

## Expected result
Dedicated tests, compile and full regression should pass without reverting the
Revision 20 performance architecture.
