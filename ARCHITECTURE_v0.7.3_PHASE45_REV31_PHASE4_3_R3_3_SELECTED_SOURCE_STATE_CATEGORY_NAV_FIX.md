# Revision 31 Phase 4.3 R3.3 — Selected Source State & Category Navigation Fix

## Defect confirmed during operator acceptance
Calenda was correctly classified as `CALENDA_PUBLIC / READY`, but:
1. `/add-products/source` loaded categories only for `PALLTEX_PUBLIC`.
2. Clicking the top `Add Products` navigation opened a clean `/add-products`
   and therefore dropped the selected supplier context.

## R3.3 correction
- Source selection is validated and redirected to:
  `/add-products?source_uuid=<approved-source-uuid>`
- GET `/add-products` accepts the selected source query state.
- Every connector with `state == READY` uses `list_source_categories`.
- The top Add Products link preserves `source_uuid` while a source is selected.
- Category and hydration actions continue carrying `source_uuid` in hidden fields.
- Calenda remains `CALENDA_PUBLIC / READY`.
- Existing Palltex and STENSO behavior is preserved.

## Safety
No DB migration.
No supplier write.
No target website write.
No stock write.
No commit/push.
Installer performs no external HTTP.

## Acceptance
1. Open `/add-products`.
2. Click `Календа -> Open source`.
3. Browser URL becomes `/add-products?source_uuid=...`.
4. Calenda remains selected.
5. Real `Supplier Categories` are visible immediately.
6. Clicking the top `Add Products` link keeps Calenda selected.
7. Choose one category, then one product, then Hydrate / Inspect.
