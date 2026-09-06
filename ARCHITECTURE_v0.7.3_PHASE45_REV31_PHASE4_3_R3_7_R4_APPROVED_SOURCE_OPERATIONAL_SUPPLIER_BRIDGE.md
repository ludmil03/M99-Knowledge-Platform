# R3.7R4 — Approved Source → Operational Supplier Bridge

Purpose:
Allow the approved governance Source used by Add Products to reuse the already
existing operational Supplier runtime required by the stable DRAFT ImportJob
service.

Binding safety:
- no Supplier row is created;
- no Supplier row is edited, activated, deactivated or duplicated;
- matching is deterministic by normalized domain/base URL;
- only active + browser-enabled operational Suppliers are eligible;
- exactly one match => bridge READY;
- zero matches => visible BLOCKED;
- multiple matches => visible AMBIGUOUS/BLOCKED;
- no silent choice;
- the approved Source remains the governance identity;
- the Supplier remains only the operational runtime dependency.

R3.7 PREPARE remains read-only.
Identity and DRAFT remain behind explicit operator confirmation.
No channel publish, Dolibarr/stock write, DB migration, commit or push.
