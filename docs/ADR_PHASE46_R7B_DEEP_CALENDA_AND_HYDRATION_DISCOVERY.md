# ADR Phase 4.6 R7B SAFE REBASE FINAL

This package is rebuilt from the Windows-accepted R7A package, not from failed R7B/FIX lineages.

Recovery policy:
- Git HEAD/origin/main must remain the accepted baseline.
- Runtime sidecars remain untouched and outside governed source state.
- Incoming governed state may be exact accepted R7A plus any subset of the known failed R7B
  additive paths. No other source drift is accepted.
- Known failed R7B additive residue is backed up and removed explicitly.
- Exact accepted R7A state is then proven by a maintained regression before R7B is applied.
- On any later failure, rollback target is exact R7A, not the incoming residue.

R7B contracts:
- Calenda `IDnnn` codes are internal/catalogue identifiers, not supplier reference or Manufacturer MPN.
- Numeric and PREFIX-number page codes are supplier-reference candidates only.
- Manufacturer MPN remains unresolved until exact manufacturer evidence is operator-confirmed.
- Supplier brand text is cut at generic page-section boundaries.
- Active Hydration remains untouched in R7B.
- Two read-only diagnostics gather the evidence required for later R7C integration.

JUnit acceptance:
- Machine-readable validation counts `<testcase>` nodes directly, including namespaced XML.
- Failure/error/skipped child elements are hard failures.
- Human stdout counts are not trusted for acceptance.

No DB migration, channel write, stock write, commit or push.
