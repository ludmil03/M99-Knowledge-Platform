# Revision 31 Phase 4.3 R2 — Palltex by STENSO connector pattern

STENSO is the proven reference supplier connector. R2 applies the same supplier-specific adapter concept to Palltex: `health_check -> list_categories -> list_products -> get_product`. Palltex categories are `/bg/cat/...`; products are `/bg/p/.../<id>`. Runtime reads are same-domain GET only. Missing hydration facts remain warnings; no facts are invented. No website write, stock write, DB migration, credentials, commit or push.
