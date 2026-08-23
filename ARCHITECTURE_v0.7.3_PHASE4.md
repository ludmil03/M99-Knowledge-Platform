# M99 v0.7.3 Phase 4
## Production Persistence + Identity Resolver + Super Admin Organization Configuration

Preserves README v9 / Decision Registry v002:
- canonical M99 identity is independent from external IDs;
- Identity Before Content;
- NEW / EXISTING / AMBIGUOUS / UNRESOLVED;
- AMBIGUOUS requires human review;
- Supplier/Manufacturer are Organization roles;
- Super Admin approval is mandatory;
- multiple supplier/manufacturer mappings are allowed;
- Supplier Browser remains read-only.

Identity priority:
verified exact EAN/GTIN -> verified exact Manufacturer Reference -> verified exact Supplier Reference.
The resolver does not invent identity from title similarity.

Phase 4 provides a formal Alembic migration artifact but the SAFE installer does not apply it.
Production migration requires M99_ADMIN_DATABASE_URL, M99_PHASE4_MIGRATION_CONFIRM=APPLY_V073_PHASE4 and typed APPLY.

Super Admin actions:
APPROVE / REJECT / MERGE_WITH_EXISTING / ACTIVATE_ROLE.
SupplierSource configuration is audited and remains read-only.

Installer safety:
no production migration, no external HTTP, no supplier/channel writes, no automatic Push.
