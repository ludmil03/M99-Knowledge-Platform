# M99 v0.7.3 Phase 4.6 R1 FINAL RC3 — Architecture-Preserving E2E m99.eu Pilot

## Frozen R37 boundary

Phase 4.3 R37 remains unchanged and owns only:
Approved Source -> Supplier Category -> Product/Variant -> Hydration -> Identity -> DRAFT -> Canonical Preview.

The following existing safety contracts are mandatory and are regression-tested by RC3:
- `r37_add_products_flow.py` contains no publish write path.
- `r37_prepare.html` retains `Потвърди Identity и създай DRAFT` and bridge-ready gating.

## Phase 4.6 control plane

Phase 4.6 is an additive post-DRAFT operator control plane under the already registered
m99.eu operator publisher router:
`/operator-publish/m99eu/r1-final`.

The installer makes one minimal additive registration patch to
`operator_single_product_publish.py` using marker `M99_PHASE46_R1_FINAL_INCLUDE`.
It does not modify R37 router or R37 prepare template.

## Live-write gates
- Super Admin only.
- DRAFT only.
- m99eu requested + authorized.
- exactly one selected ImportJobItem.
- permanent canonical `M99-<digits>` must be discoverable from DRAFT/Identity snapshot.
- no `M99-900...` fallback.
- exact `PUBLISH ONE PRODUCT` confirmation.
- env enable + 32-char API key + positive category.
- duplicate guard.
- target category preflight.
- active=1, visibility=none, available_for_order=0.
- extended read-back.
- AuditLog.
- no batch, no automatic retry.

If DRAFT does not expose permanent identity or price evidence, live write stops safely.
The fix must then be made in the canonical DRAFT/Identity persistence contract rather than bypassed in R37.
