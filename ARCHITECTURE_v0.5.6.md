# M99 v0.5.6 — Bultex99 B2B Read-Only Live Test

This release adds a safe live-read harness.

## Scope
- Discover the actual login form field names from `/pap/login.php`.
- Authenticate only if the three identity fields are safely mapped.
- Read only `/pap/minfo.php?i=<numeric id>`.
- Parse the control product and compare current values with the values manually
  verified in Chrome DevTools.

## Control product
- B2B product id: 109168
- Supplier variant: 06200368.39
- Size: 39
- Warehouse: 222 Radinovo
- Previous B2B purchase price: 23.24 EUR ex VAT
- Previous recommended/final price: 37.08 EUR ex VAT
- Previous supplier stock: 45 pairs
- Barcode: 2006200368030

A difference is reported as CHANGED, not treated as an error, because price and
stock are expected to change.

## Credential safety
Credentials are entered locally at runtime and exist only in the current
PowerShell process. They are cleared after the test. No `.env`, JSON, source
file, log or Git commit stores them.

## Write safety
This harness contains no method for:
- adding to basket;
- creating an order;
- writing documents;
- changing Dolibarr;
- changing any sales channel.

v0.5.6 is therefore a supplier READ-ONLY integration test.
