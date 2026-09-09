# Phase 4.6 R4→R1 R5 Acceptance Checkpoint

Status: WINDOWS/RUNTIME ACCEPTED

Functional commit: `581827a99aaa2adac873ee95d19b88b0e5d541d7`

Acceptance evidence:
- R5 package-local JUnit self-test: 14 scenarios PASS.
- Dedicated bridge tests: 22 PASS.
- Maintained regression: 661 PASS / 6 known warnings.
- Exact governed poststate PASS.
- Live m99.eu write remains server-side LOCKED pending payload-adapter acceptance.
- CONTENT-EDITORIAL-001 active.
- Supplier reference, Manufacturer MPN and permanent M99 reference remain separate roles.
- Runtime durable sidecars are not committed.
