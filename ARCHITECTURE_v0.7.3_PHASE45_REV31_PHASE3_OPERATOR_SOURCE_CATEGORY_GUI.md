# Revision 31 Phase 3 — Operator Source & Category Management GUI

## Scope
GUI wiring on top of accepted Revision 31 Phase 1 governance and Phase 2 persistence.

## Screens
- `/rev31-governance` — dashboard.
- `/rev31-governance/sources` — approved source registry + operator proposal form.
- `/rev31-governance/categories` — approved canonical categories + operator proposal form.
- `/rev31-governance/approvals` — Super Admin-only approval queue.

## Rules
- Operator may propose Supplier/Manufacturer.
- Proposal remains unusable until Super Admin approval.
- Operator may propose Canonical Category.
- Only Super Admin may approve/reject.
- Rejection remains historical and disappears from pending queue.
- Existing frozen Supplier Browser/Hydration/DRAFT/Preflight/Canonical Preview path is not redesigned.
- No external website write is introduced.
- No product publish is introduced.
- Phase 3 uses the Phase 2 persistence service and existing authenticated user identity.
- Runtime registration is additive: one router include only.

## Acceptance
A local GUI acceptance test verifies:
1. app imports;
2. router is registered once;
3. operator-facing pages respond;
4. Super Admin queue authorization is enforced by service;
5. proposal/approval round-trip is tested through Phase 2 services;
6. no external channel write primitives exist.

The first real browser/operator acceptance follows installer PASS.

## R5 R2 runtime acceptance correction
Phase 2 intentionally proved persistence against a temporary SQLite database and did not
modify the live M99 Admin database. Phase 3 GUI requires those tables in the local Admin DB.

R5 R2 therefore performs an explicit, create-only bootstrap of the five `m99_rev31_*`
tables in the local SQLite Admin DB after taking a file backup. It refuses non-SQLite DBs,
does not alter existing tables, and does not write to any external channel.

The installer also removes non-ASCII navigation glyphs introduced by R5/R5 R1.

## R5 R4 native Admin layout correction
Real browser acceptance showed that a standalone Governance layout isolated the operator
from the normal M99 Admin navigation. R5 R4 removes that standalone shell.

All Rev31 Governance pages now inherit the existing M99 Admin `base.html` and render
inside its normal content block. This preserves Dashboard and the existing sidebar.
The installer restores the tracked main `base.html` to the Phase 2 R2 baseline and does
not patch global navigation. Entry into Governance remains explicit from `/suppliers`.

No decorative Unicode glyphs are added by Revision 31.

## R5 R5 browser-acceptance correction
Native base inheritance was rejected after real browser testing because the existing M99
Admin base expects additional route context not supplied by the Rev31 routes.

The known-working standalone Governance shell is restored. It now includes explicit
Dashboard and Suppliers/Browse return links.

The existing `/suppliers` template is restored from Git before patching. A Python UTF-8
patch helper inserts the Governance CTA before the complete `Open Supplier Browser`
control. PowerShell no longer decodes/re-encodes that template.
