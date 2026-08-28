# M99 v0.7.3 Phase 4.5 Revision 31 — Phase 1
## Supplier & Manufacturer Registry Governance Foundation

Governance baseline: README v11.
Frozen tested runtime baseline: Rev29R3.2R2.

This first Revision 31 slice deliberately implements the domain/governance contract
before persistence and GUI wiring.

Implemented contract:
- Operator can propose Supplier or Manufacturer.
- Proposal is non-operational until Super Admin approval.
- Only Super Admin approves/rejects.
- Rejected proposal is hidden from normal operator registry, retained as history,
  and may be proposed again as a NEW proposal linked to prior rejected history.
- Duplicate proposal for an already approved same-kind domain is blocked.
- Only Super Admin edits approved source domain and activation.
- Old domain history is preserved.
- Deactivated source is non-operational but not deleted.
- Operator Manufacturer <-> Supplier Product mapping actions produce mandatory audit records.
- Operator maps Supplier Category only to approved Canonical Category.
- New Canonical Categories are proposals requiring Super Admin approval.
- Bulk category discovery starts with ZERO selected and never directly publishes.

Not implemented in Phase 1:
- database persistence/migration for proposals;
- Super Admin approval queue UI;
- Supplier/Manufacturer Registry UI;
- category browser/search UI;
- category discovery connector runtime;
- manufacturer mapping persistence;
- canonical category persistence;
- website/channel writes.

Next after Phase 1 test acceptance:
Revision 31 Phase 2 — persistence schema + approval queue, still preserving the
frozen Hydration -> DRAFT -> Preflight -> Canonical Preview runtime.


## Revision 31 Phase 1 R1 — Python 3.14 compatibility
The Phase 1 governance/domain contract is unchanged.

The dedicated test module loader now registers the dynamically loaded service
module in `sys.modules` before `exec_module()`. Python 3.14 `dataclasses`
consults `sys.modules` while resolving postponed/string annotations during
class decoration. The previous test loader omitted that registration, causing
all dedicated tests to fail during import before governance logic executed.

This is a test/runtime-loading compatibility correction only. It does not
change source approval rules, category governance, mapping audit rules,
persistence, UI, migrations, or website/channel behavior.
