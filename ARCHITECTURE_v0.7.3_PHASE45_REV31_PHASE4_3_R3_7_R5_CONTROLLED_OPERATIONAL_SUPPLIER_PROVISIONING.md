# R3.7R5 — Controlled Operational Supplier Provisioning

Super Admin-only explicit provisioning of an operational Supplier from an already approved Source.

Rules:
- no silent create;
- no duplicate;
- approved Source remains governance identity;
- created Supplier is only the legacy operational dependency;
- uniqueness re-check before commit;
- append-only audit record;
- provisioning itself does not create DRAFT or publish to a channel;
- no DB migration, Dolibarr/stock write, commit or push.
