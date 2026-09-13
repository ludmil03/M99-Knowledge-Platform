# ADR Phase 4.6 R6 — Safe Rebase from Accepted R5

R6 is rebuilt directly from the accepted R5 source baseline instead of from the failed R6/R6.1 branches.

Compatibility-first rules:
- accepted R5 `build_content_bundle` tail is byte-for-byte preserved;
- historical static contracts remain present;
- Meta/Short `< 0.750` remains a hard gate;
- a generic second-pass Meta Description is additive only;
- gender inference is additive for arbitrary Calenda shirts;
- RIVER behavior remains compatible while arbitrary female/male/unisex products are supported;
- no DB/channel/stock write and no Git mutation.

Installer additionally discovers and runs all maintained repository tests that reference
`content_manufacturer_intelligence` before the full regression, so hidden historical
static contracts are exercised before the final gate.


## R6 SAFE R2 — repository-root import context

Windows acceptance reached the automatically discovered maintained R4 tests and
stopped during collection with `ModuleNotFoundError: No module named 'app'`.

The historical test is not changed. R2 keeps repository root as pytest CWD and
prepends the accepted `admin-platform` directory to `PYTHONPATH` only for
pytest/import subprocesses. Git subprocesses keep the normal environment.

Before any maintained pytest collection, the installer now executes a real
repo-root subprocess import probe for:
`app.services.v073_phase46.durable_draft_enrichment`.
