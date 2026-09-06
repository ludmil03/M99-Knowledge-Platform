# R3.7R5C — Supplier Code Required Fix

Live GUI provisioning exposed the real persistence contract:
`suppliers.code` is NOT NULL.

R3.7R5C preserves the accepted provisioning design and adds only the missing
required operational Supplier code.

Rules:
- derive deterministic code from approved source domain;
- `calenda.bg` -> `CALENDA-BG`;
- never overwrite an existing code;
- if occupied, use `-2`, `-3`, ... suffix;
- pass `code=` explicitly to Supplier(...);
- rollback the SQLAlchemy session on flush/commit failure;
- no DRAFT creation;
- no channel publish;
- no Dolibarr/stock write;
- no migration;
- no commit/push.
