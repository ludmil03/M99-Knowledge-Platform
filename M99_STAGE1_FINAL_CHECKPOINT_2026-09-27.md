# M99 Stage 1 — Consolidation Map / Final Checkpoint

Date: 2026-09-27
Parent checkpoint: `07fea4b6f3b334d76f575bc4a49dd0433d9ece69`
Stage: 1 / 5
Runtime change: **NO**

## Windows-accepted characterization

- Repository inventory: PASS
- Relevant files: 213
- Router registrations: 26
- Python files scanned: 378
- Focused dependency edges: 902
- Golden flows: 3
- Final classified components: 210
  - AUTHORITATIVE: 4
  - REUSE: 47
  - LEGACY: 81
  - DEPRECATE: 18
  - TEST-HISTORY: 60
- Retirement dependencies: 18
- Destinations: 8
- Repository remained clean after every characterization pass.

## Binding architecture decisions

1. `/operator/add-products` is the AUTHORITATIVE normal operator entry.
2. Do not create a fourth importer.
3. Bultex99, Calenda and Palltex retain supplier-specific acquisition adapters.
4. Downstream governance converges on one canonical intake pipeline:
   `Selection → Hydration → Evidence → Identity → Canonical → Content → Price/VAT → QA → Targets`.
5. Publishing converges on:
   `M99 Knowledge UI → Publish Service → Channel Adapter → API → Readback → Audit`.
6. Historical parallel publish routes are not deleted in Stage 1. They retire only after golden-flow equivalence.
7. `WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`.
8. `toplinka.com` is a WordPress/WooCommerce publishing channel, status READY_TO_PROVE until adapter/auth/languages/VAT/readback are proven.
9. Dolibarr remains an ERP destination with separate semantics.
10. Publishing remains an explicit M99 Knowledge UI action; CMD is only for install/update/test/checkpoint work.

## Golden regression flows

- **Bultex99 / Panda UNO LOW** — selection, public/B2B separation, canonical evidence, 8 selection modes.
- **Calenda variant evidence** — color/size/image ownership and evidence-contamination rejection.
- **Palltex / BWolf / M99 100018** — identity, durable evidence, duplicate protection, strict readback and audit.

## Stage 2 handoff

Stage 2 creates the **Unified Supplier Adapter Contract**. Supplier adapters must return one canonical `SupplierProductEvidence` shape covering:

- identity facts
- technical facts
- images
- price
- availability
- variants
- commercial evidence

Supplier acquisition stays supplier-specific. Identity/content/price/VAT/QA/target/publish governance must not be reimplemented independently per supplier.

## V17 binding release discipline

`STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE → COMMIT → PUSH → REMOTE_VERIFY`

A missing or failed gate means NOT_RELEASEABLE. A failed revision never becomes stable.
