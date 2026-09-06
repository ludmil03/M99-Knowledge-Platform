# R3.7R3 — Variant Evidence Hydration Gate Fix

Browser acceptance exposed a mismatch:
RIVER 31809 had 24 accepted exact Color x Size rows, but the old product-level
hydration gate still blocked R3.7 because Calenda does not publish one
top-level price/availability value.

R3.7R3:
- keeps exact Color x Size evidence canonical;
- derives an operator summary price `FROM <minimum EUR>` only when exact
  size-level `price_eur` evidence exists;
- derives `AVAILABLE BY VARIANT` / `OUT OF STOCK BY VARIANT` only when exact
  supplier availability buckets exist;
- does not convert supplier quantities into M99-owned stock;
- keeps products without exact size evidence blocked;
- uses AIFOS 39943 as the live negative control;
- changes no Identity/DRAFT/Target/Canonical Preview write behavior.

No channel publish, Dolibarr/stock write, DB migration, commit or push.
