# Phase 4.6 R4 — Durable Canonical Draft → Publish Handoff

R4 adds an additive, atomic, checksum-verified durable enrichment store when the current ORM has no mapped evidence carrier. It does not mutate the DB schema and does not write to a sales channel. After exact manufacturer confirmation, the EN/BG/RU content bundle is written under `admin-platform/var/phase46_draft_enrichment/job-<id>.json`, read back and checksum verified. Only then is the operator offered a handoff to the existing R1 m99.eu Publish Review.

This is a governed transitional persistence layer. A later schema migration may move the same versioned record into the canonical DB without changing the R4 contract. R4 does not claim that the legacy R1 publisher consumes every multilingual field yet; the Publish Review remains the safety boundary before channel write.


## R4 FIX2 — frozen R3 contract preservation

R4 must be additive. The R3 statement that the current ImportJobItem ORM has no
mapped DRAFT evidence carrier remains true and is preserved verbatim for audit
and regression compatibility:

`NO_MAPPED_DRAFT_EVIDENCE_CARRIER`

R4 does not reinterpret this as a mapped ORM carrier. It adds a separate durable
sidecar persistence mechanism and records the upgrade as
`R4_DURABLE_DRAFT_SIDECAR`.


## R4 FIX3 — Context continuity invariant

Once supplier/manufacturer evidence has been resolved for the active operator
flow, downstream persistence MUST receive that resolved evidence explicitly.
A persistence function MUST NOT reconstruct the evidence context with empty
source identifiers.

Invariant:
`discover -> confirm -> exact evidence -> content -> durable save`
preserves the same supplier evidence and exact manufacturer reference.

## Content quality invariant

`Meta Description` and `Short Description` are separate content assets.
They may share verified facts but MUST NOT be identical or near-duplicates.
A normalized similarity >= 0.90 is rejected before durable persistence.


## R4 FIX4 — Multilingual field-purpose invariant
Meta Description and Short Description are independent canonical assets.
Release invariant for every generated language:
`normalized_similarity(meta_description, short_description) < 0.75`
The complete multilingual bundle is validated before durable persistence.


## R4 FIX5 — Success-path UI boundary invariant

An E2E simulation must include the *post-success render call*, not only the
business operation inside `try`. Helper keyword contracts are part of runtime
API compatibility.

Invariant:
all keyword arguments passed to `_review_context` from confirm are accepted by
its signature, and the final review render has a controlled failure boundary.


## R4 FIX5C — Monotonic regression-contract strengthening
A prior regression literal may be updated when a deliberate architecture rule
becomes strictly stronger. Such migration must preserve the test intent and
must not use skip/xfail.

Meta↔Short quality ceiling: 0.90 -> 0.75.
