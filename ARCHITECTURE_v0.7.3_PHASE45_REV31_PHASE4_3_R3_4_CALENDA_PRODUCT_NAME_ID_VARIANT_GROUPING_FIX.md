# Revision 31 Phase 4.3 R3.4 — Calenda Product Name, ID & Variant Grouping Fix

## Operator defect confirmed
Calenda category discovery returned both:
- canonical product URLs such as `/products/34408`
- color-specific URLs such as `/products/34408?color=317`

The previous list treated the color URLs as separate product rows. Because many
color swatch links have no human-readable anchor text, they appeared as
`Calenda product 34408`.

## R3.4 binding behavior
One Calenda path `/products/<ID>` represents one supplier product for listing
identity. Query parameter `?color=<code>` represents a variant of that product.

Example:
- Canonical Calenda Product ID: `34408`
- Supplier ref / SKU: `ID207`
- Name: `ТЕНИСКА ТИП ЛАКОСТА PREMIUM TIPPED POLO`
- Variant URLs:
  - `?color=317`
  - `?color=480`
  - `?color=485`
  - `?color=486`
  - `?color=488`

## UI
Product list shows:
- full product name
- Supplier ref / SKU when discoverable from category evidence
- explicit Calenda Product ID
- grouped color variants beneath the parent product
- Hydrate / Inspect for the parent
- optional Hydrate variant for a selected color URL

Hydration shows:
- Supplier ref / SKU
- Calenda Product ID
- selected color query code when applicable

## Evidence discipline
The connector does not invent a color name when Calenda only exposes the query
code. The fallback is `Color <code>`, e.g. `Color 317`.

## Out of scope for R3.4
R3.4 intentionally does not solve:
- missing Brand
- missing Availability
- image quality/filtering
- canonical identity/DRAFT/channel writes

Those remain separate hydration refinement work.

## Safety
- supplier runtime: GET/read-only
- installer external HTTP: NO
- DB migration: NO
- supplier write: NO
- website/channel write: NO
- stock write: NO
- commit/push: NO
