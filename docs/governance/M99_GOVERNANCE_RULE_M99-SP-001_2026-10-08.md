# M99 Knowledge Platform — Architecture Decision M99-SP-001

**Date:** 2026-10-08  
**Status:** APPROVED BY OPERATOR — governance decision; implementation pending  
**Title:** Supplier On-Demand + Selective Persistence  
**Applies to:** All current and future supplier connectors, including Bultex99, Palltex and Calenda.

## Binding decision
M99 must not mirror or permanently store complete supplier catalogs. Supplier categories and product listings are retrieved on demand and held only in a bounded temporary cache. Persistent M99 records are created only for products selected for M99 processing (DRAFT or later), subject to existing identity, evidence and authorization gates.

## Mandatory controls
1. **On-demand extraction:** Request only the supplier category/product information needed for the operator's current task.
2. **Bounded temporary cache:** Enforce expiration, size limits and eviction; never treat cache content as permanent M99 product records.
3. **Selective persistence:** Persist canonical product information only for selected DRAFT/managed products; do not bulk-import supplier catalogs.
4. **Evidence-first:** Retain sufficient verified facts, provenance, timestamps and hashes for governed decisions, without unnecessary full-page duplication.
5. **No redundant requests:** PREPARE, Identity, Content Intelligence and DRAFT reuse validated data rather than re-fetching the same supplier page per screen.
6. **Supplier request control:** Rate-limit, deduplicate requests and honor HTTP 429 / Retry-After. Never bypass supplier verification or interpret 429 as success.
7. **DRAFT recovery:** Persist selected DRAFT state safely so operator work can resume after restart; temporary cache loss must not destroy accepted DRAFT data.
8. **Selective monitoring:** Check supplier prices/availability only for active managed M99 products and only as permitted by source policy; supplier availability is not physical M99 stock.
9. **Fail-closed:** Missing, expired, mismatched or insufficient evidence requires review or explicit re-extraction; no invented facts or implicit publish.
10. **Existing governance remains:** Supplier ≠ Manufacturer ≠ Brand; CREATE ≠ UPDATE; exact target authorization; explicit Publish; mandatory full readback; no unapproved database migration or Git mutation.

## Implementation milestone
**R7 R2.7 — SELECTIVE PRODUCT PERSISTENCE + SUPPLIER REQUEST CONTROL MAXSIM**.
First inspect existing DRAFT/evidence schema and active routes; reuse existing storage where suitable. Implement and simulate bounded cache, source request control, restart recovery, authorization and fail-closed behavior. Run regression before Windows ZIP. Do not commit/push until Windows and REAL M99 acceptance both pass.

## Status clarification
This file records the approved architecture decision; it does **not** claim that the code, repository README, database or remote GitHub has already been updated.
