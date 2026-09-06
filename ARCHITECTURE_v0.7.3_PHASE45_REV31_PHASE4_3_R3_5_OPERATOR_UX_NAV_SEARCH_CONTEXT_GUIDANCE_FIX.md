# Revision 31 Phase 4.3 R3.5 — Operator UX: Navigation, Search, Category Context & Guidance

This revision addresses four operator acceptance findings.

## 1. Main-menu access
`Add Products` is inserted into the existing M99 left navigation by cloning the
native `Suppliers / Browse` anchor styling. The dashboard remains the normal
post-login landing page, but the operator no longer needs to type
`/add-products` manually.

## 2. Search
At supplier-category level, a search box filters the complete category list
already loaded by the source-specific connector.

After a category is selected, a second search box filters the loaded products
by:
- product name
- Supplier ref / SKU
- Calenda Product ID
- product URL

This removes manual page-by-page scanning of the M99 supplier view. It does not
pretend to be a remote full-text search API when the supplier has not exposed
one.

## 3. Selected-category context
Category selection now redirects to a stable GET URL:
`/add-products/category?source_uuid=...&category_url=...`

While browsing products and while reviewing hydration, the chosen category
remains the active context. The full category list is hidden until the operator
explicitly chooses `Смени категорията`.

## 4. Bulgarian operator guidance
`Product Hydration` is replaced in operator-facing UI by:
`Проверка на извлечените данни`

The screen explains that M99 has read supplier evidence and that the operator
must verify the extracted data. It explicitly states that no website write is
performed.

Operator buttons:
- `Назад към продуктите`
- `Смени категорията`
- visible but disabled `Продължи към Identity / DRAFT`

The final button is intentionally not wired in R3.5 because the next runtime
slice must connect the already-proven Identity -> DRAFT pipeline explicitly and
safely.

## Safety
- no DB migration
- no supplier write
- no target website write
- no stock write
- no commit/push
- installer external HTTP: NO
