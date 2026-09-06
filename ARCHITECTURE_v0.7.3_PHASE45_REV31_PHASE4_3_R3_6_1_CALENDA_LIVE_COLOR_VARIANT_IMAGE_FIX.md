# Revision 31 Phase 4.3 R3.6.1 — Calenda Live Color Variant Detection Fix

Control product: Calenda 31809 / SKU 93100 / МЪЖКА РИЗА RIVER.

Operator evidence confirms four colors: 20 бял, 26 черно, 42 тъмно-синьо, 46 небесно-синьо.
Each color/variant has its own product image.

R3.6.1:
- detects ordinary ?color= links and JS/data-driven color controls;
- keeps same-product identity only;
- stores `image_url` per color variant;
- if the selector lacks a direct image, performs a read-only GET of that variant URL and captures its own product image;
- never substitutes another variant's image when evidence is missing;
- emits `VARIANT_IMAGE_NOT_FOUND` as a warning when needed;
- preserves R3.6 brand, product-image filtering and UNKNOWN availability semantics.

No Identity/DRAFT, DB migration, site/stock write, commit or push.
