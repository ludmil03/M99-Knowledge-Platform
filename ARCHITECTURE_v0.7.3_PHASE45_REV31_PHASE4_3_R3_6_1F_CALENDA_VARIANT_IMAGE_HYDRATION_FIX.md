# R3.6.1F — Calenda Variant Image Hydration Fix

Live R3.6.1F-DIAG proved that Calenda keeps the generic image in the initial
`#product_carousel`, but injects the selected textile color image through an
inline `add.owl.carousel` script and repeats it in `#textile-color-table`.

For SKU 93100 the live evidence is:
- 20 / color=7 -> 93100_20a.jpg
- 26 / color=206 -> 93100_26a.jpg
- 42 / color=211 -> 93100_42a.jpg
- 46 / color=231 -> 93100_46a.jpg

The connector now prefers selected-color evidence tied to both supplier
reference and visible color code. Generic/related images are not accepted as
variant evidence.

Scope is image hydration only. Availability/size-stock extraction is intentionally
left for a separate revision even though the diagnostic exposed such evidence.

No Identity/DRAFT activation, DB migration, external write, commit or push.
