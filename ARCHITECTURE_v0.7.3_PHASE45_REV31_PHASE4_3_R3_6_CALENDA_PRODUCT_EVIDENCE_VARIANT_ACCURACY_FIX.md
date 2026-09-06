# Revision 31 Phase 4.3 R3.6 — Calenda Product Evidence & Variant Accuracy Fix

## Purpose
Correct the live Calenda hydration defects observed on product 31809 / supplier SKU 93100.

## Binding behavior
- Product images are evidence-scoped, not global-page images.
- Same-product gallery images may be retained.
- Header/footer logos, icons, banners, related-product images and similar-product images are excluded.
- Explicit `Марка:` evidence is extracted as brand/manufacturer evidence. For the control product this should resolve to `PROMO STARS`.
- Same-product `?color=` links become color variants.
- Supplier availability absent from the public page becomes `UNKNOWN`, never zero or out-of-stock.
- Missing public availability is warning-level and does not by itself block identity/DRAFT readiness.
- No Identity/DRAFT, channel write, PrestaShop write, stock write, DB migration, commit or push is performed by this revision.

## Control product
Calenda Product ID: 31809
Supplier SKU: 93100
Name: МЪЖКА РИЗА RIVER
Expected visible color variants from operator evidence: 20 бял, 26 черно, 42 тъмно-синьо, 46 небесно-синьо.
