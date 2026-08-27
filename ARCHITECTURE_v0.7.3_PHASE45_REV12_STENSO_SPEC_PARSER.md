# M99 v0.7.3 Phase 4.5 Revision 12 — STENSO Live Product Hydration

## Real defect found
Live category inspection returned product URLs, but rows were shown as
`(title pending product read)` with empty supplier references. The operator
could not make an informed selection.

## Fix
For STENSO category/product inspection M99 hydrates each discovered product URL
before selection and exposes:
- verified product name;
- supplier reference / article number;
- source URL;
- price text;
- product images;
- description;
- extracted specifications;
- size/variant availability;
- product-level availability derived from variants.

## STENSO size availability
A size is OUT_OF_STOCK when the live control has semantic unavailable evidence:
disabled / aria-disabled, unavailable/out-of-stock CSS state, explicit stock
data=false, pointer-events:none or low inline opacity. A selectable size control
without disabled evidence is IN_STOCK.

This implements the operator-observed STENSO behavior where pale/disabled size
controls are unavailable, while active controls are available, without relying
on screenshot color alone.

## Operator safety
- 0 products selected by default.
- Failed hydration rows cannot be selected.
- First real test should select exactly 1 product.
- Product details are visible before selection.
- DRAFT button is disabled until at least one product is selected.
- Create-job does not trust hidden title/ref fields.
- Selected URLs are re-read from the supplier and identity fields are verified
  immediately before DRAFT Import Job creation.
- No website/channel write occurs in this fix.


## Revision 12 fix
- Parses inline STENSO technical labels such as `САЯ:` and `ПОДПЛАТА:` even when the supplier HTML exposes them in a single text node.
- Keeps UTF-8 Cyrillic test fixtures and validates exact specification name/value pairs.
- Preserves zero products selected by default and the existing size availability rule.
