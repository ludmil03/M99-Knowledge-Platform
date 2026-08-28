# M99 v0.7.3 Phase 4.5 — Revision 31 Phase 2
## Persistence Schema + Super Admin Approval Queue Foundation

### Status
Implementation slice following the successful Revision 31 Phase 1 R1 governance contract.

### Governing baseline
- Governance v11 remains authoritative.
- Revision 31 Phase 1 R1 governance/domain contract remains unchanged.
- Frozen Rev29R3.2R2 product runtime remains untouched.
- DECIDED rules are not reopened by implementation failures.

### Purpose
Phase 2 provides durable persistence primitives and the Super Admin approval queue
service required by the operator source/category governance decided in v11.

It deliberately does **not** wire new routes into `app.main`, does not change the
existing Supplier Browser / Hydration / DRAFT / Preflight / Canonical Preview path,
and does not write to external websites.

### Persistence model
This slice uses a dedicated SQLAlchemy 2.x declarative metadata set:

- `m99_rev31_source_proposals`
- `m99_rev31_approved_sources`
- `m99_rev31_category_proposals`
- `m99_rev31_canonical_categories`
- `m99_rev31_source_audit`

No automatic `create_all()` is executed by application import.
Schema creation occurs only through an explicit bootstrap function or test/acceptance
harness. This keeps Phase 2 non-invasive until GUI/runtime integration is approved.

### Source proposal lifecycle
Operator:
- may propose SUPPLIER or MANUFACTURER;
- proposal status begins PROPOSED;
- proposal is not operational before approval.

Super Admin:
- may list pending proposals;
- may approve or reject;
- approval creates/updates an approved source record and audit entry;
- rejection records reviewer, time, decision note and audit entry.

Rejected proposal:
- remains historical evidence;
- is excluded from the normal pending queue;
- may later be re-proposed as a new proposal.

Approved source:
- has ACTIVE / DEACTIVATED activation state;
- historical domain changes are preserved in an audit record;
- operational use is only valid when approved and ACTIVE.

### Canonical Category lifecycle
Operator may propose a category.
Only Super Admin may approve/reject.
Approved canonical categories are the only categories eligible for mapping in later UI phases.

### Approval Queue
`source_registry_approval_queue.py` is an application service, not a route.
It enforces Super Admin authorization before listing/reviewing proposals.

Phase 3 will wire this service into the graphical admin UI.

### Acceptance test
The package includes a one-click acceptance harness that:
1. creates a temporary SQLite file database;
2. creates Phase 2 schema explicitly;
3. persists an operator Supplier proposal;
4. closes and reopens the DB session;
5. confirms Super Admin pending queue sees the proposal;
6. approves it;
7. closes and reopens the DB again;
8. confirms the approved source is ACTIVE;
9. confirms an approval audit record exists;
10. removes the temporary DB.

This validates real durable persistence, not an in-memory mock.

### Safety
- no website/channel writes;
- no PrestaShop/ThirtyBees/WordPress/Dolibarr write;
- no product publish;
- no migration of the existing application DB;
- no `app.main` wiring;
- no commit;
- no push;
- installer rolls back additive Phase 2 files on gate failure.

### Next slice
Revision 31 Phase 3 — Operator Source & Category Management GUI:
- operator proposal screens;
- Super Admin approval queue pages;
- approved source registry;
- category browse/search/proposal/approval;
- manufacturer ↔ supplier product mapping audit UI.
