# M99 v0.7.3 Phase 4.5 Revision 29R3
## Active Admin Runtime Route Repair + Supplier/Manufacturer Separation

Scope:
1. Canonical Preview route is owned by a dedicated runtime router.
2. app.main explicitly imports and includes that router.
3. installer verifies exact app.main.__file__, runtime router __file__, and app.routes.
4. manufacturer source must have a different host from supplier source.
5. STENSO remains supplier evidence only.
6. Canonical Preview remains supplier-only capable when no manufacturer URL exists.

Stable contracts preserved:
- /supplier-browser/inspect
- /supplier-browser/hydrate-product
- runHydrationQueue(4)
- exactly one /create-job form
- DRAFT supplier re-verification
- Preflight

No website write, migration, commit or push.
