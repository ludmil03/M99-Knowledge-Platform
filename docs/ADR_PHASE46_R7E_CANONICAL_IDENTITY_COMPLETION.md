# ADR Phase 4.6 R7E — Canonical Identity Completion

Observed on Job #19 / BROOK after R7D acceptance:
- permanent canonical M99 reference missing;
- R4 durable enrichment missing.

R7E fixes the identity half without weakening the live gate.

A Super Admin may explicitly confirm `CREATE PERMANENT M99 ID`.
R7E then either reuses an already linked canonical Product or creates a new Product with the next
available `M99-<digits>` reference, lifecycle `draft`, links ImportJobItem.matched_product_id,
commits and reads back. Supplier Reference and Manufacturer MPN remain separate roles.

`canonical_reference_from_draft()` is extended monotonically: if no embedded M99 identity exists,
it may read the already-linked canonical Product through the SQLAlchemy object session. It still
never synthesizes a provisional/fallback M99 reference.

R4 durable Manufacturer/content evidence is intentionally not fabricated. After identity completion,
the operator reconfirms the exact Manufacturer product through the existing Manufacturer Intelligence
flow; that existing confirmed action recreates the durable sidecar.

No website write occurs during installation. The accepted R7D live adapter remains unchanged.
No DB migration. No stock write. No Git commit/push.


## SAFE R2 — SQLAlchemy mapped-session compatibility guard

Windows acceptance of R7E proved the accepted R7D baseline (`700 passed`) and all first R7E
dedicated tests (`5 passed`). The only failure occurred in related regression when
`canonical_reference_from_draft()` called `object_session()` on a `SimpleNamespace`.

SAFE R2 handles the ORM lookup as an optional carrier:
- mapped attached ORM item: linked canonical Product may be resolved;
- detached/unmapped/test-double item: behaves as no Session and follows the historical safe block;
- valid embedded `M99-<digits>` remains valid;
- Supplier Reference / Manufacturer MPN never become canonical identity.

The historical test is not changed or skipped; a new regression reproduces the exact
`SimpleNamespace(detection={"reference":"SUP-1"})` failure.
