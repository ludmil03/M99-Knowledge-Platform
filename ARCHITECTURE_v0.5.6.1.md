# v0.5.6.1 — Bultex parser hotfix

The v0.5.6 regression test correctly exposed a parser bug.

Cause:
The parser treated any decimal in the HTML as a possible price, so the
supplier variant code `06200368.39` was interpreted as `6200368.39`.

Fix:
- Purchase price is now parsed only from the labelled `Цена` field.
- Recommended price is parsed only from the labelled `Крайна цена` field.
- Supplier variant codes cannot be interpreted as prices.
- Regression coverage added.

No live-write capability is added.
