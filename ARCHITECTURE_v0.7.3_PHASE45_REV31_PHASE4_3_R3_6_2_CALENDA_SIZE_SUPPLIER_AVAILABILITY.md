# R3.6.2 — Calenda Size & Supplier Availability Evidence Fix

Scope: read-only supplier evidence.

For each selected Calenda textile color page, parse `#textile-color-table` and
capture each size row with the exact published supplier quantities:
- Varna warehouse quantity
- delivery 1–2 working days quantity
- delivery 7–10 working days quantity

Each row is stored under the color variant as `sizes`, with a
`supplier_availability` evidence object. Variant-level summary values are exact
sums of the published size rows.

Critical governance rule:
Supplier availability is external supplier evidence. It NEVER counts as
M99-owned physical stock. The payload marks this explicitly with:
`evidence_scope = SUPPLIER`
`counts_as_m99_owned_stock = False`

Top-level hydration availability semantics are not repurposed. No Dolibarr
stock write, no DB migration, no Identity/DRAFT activation, no channel write,
no commit/push.
