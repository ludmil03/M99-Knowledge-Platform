# R3.7R7 — Complete Identity Persistence + Manufacturer Evidence + Variant Images

R7 reconciles every existing SQLAlchemy Identity table (`m99_v073_identity_*`)
against the real Admin DB, creates only missing mapped tables after backup, adds
operator-confirmed Manufacturer/Brand evidence in PREPARE, and preserves exact
per-variant image evidence through Canonical Preview.

Manufacturer evidence does not silently create or approve a canonical
Manufacturer Organization. No publish, PrestaShop write, Dolibarr write,
M99-owned stock write, automatic commit or push is performed.
