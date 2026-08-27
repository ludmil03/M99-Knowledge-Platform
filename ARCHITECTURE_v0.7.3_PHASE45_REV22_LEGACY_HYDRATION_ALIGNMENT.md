# M99 v0.7.3 Phase 4.5 Revision 22 — Legacy Hydration Contract Alignment

## Revision 21 full regression result
One legacy Revision 12 test still required eager category hydration:
category inspect -> hydration_pass == 1.

That is no longer the intended architecture.

## Current progressive contract
1. Read category once.
2. Discover product URLs.
3. Return category UI immediately.
4. Each product starts as WAITING.
5. Browser requests product hydration separately.
6. Product becomes PASS/FAIL independently.
7. Checkbox is enabled only on PASS.

## Revision 22
No production/runtime performance logic changes.

The old Revision 12 test is rewritten to preserve the original guarantee:
- category discovery finds the product;
- category inspection performs no product HTTP read;
- product starts WAITING;
- separate product hydration reads the product URL;
- hydrated product returns PASS with verified supplier reference and title.

This aligns regression coverage with the progressive architecture rather than
removing the historical test.
