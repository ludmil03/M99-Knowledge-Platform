# M99 v0.5.5 — Bultex99 B2B Connector + Pricing + Availability

- Bultex99 B2B is modeled as an authenticated HTML supplier source.
- Product pages `/pap/minfo.php?i=...` provide supplier product ID, variant code,
  B2B purchase price, recommended price, warehouse stock, barcode and name.
- No credentials are stored in GitHub.
- Live login remains disabled until exact form field names are confirmed.
- Stenso public gross price is the competitor/reference price.
- Default target selling price = Stenso public gross price minus 1.5%.
- Never publish below Dolibarr acquisition cost.
- Profit floor can force operator review.
- Bultex B2B current purchase price never silently overwrites historical Dolibarr cost.
- Own stock master = Dolibarr.
- Supplier stock source = Bultex99 B2B.
- Availability is variant-level.
