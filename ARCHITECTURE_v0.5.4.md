# M99 v0.5.4 — Identity, Catalog & Optimization Guardrails

- Canonical M99 ID: `M99 000001` (M99 + space + six digits).
- Existing MoneyWork, Dolibarr and website identifiers are preserved as mappings.
- Existing website canonical URLs are protected during SEO/content enrichment.
- Hierarchy: ProductGroup -> Product -> Variant.
- Each stock-managed variant gets its own M99 ID.
- Website UX may expose one product page with size/color attributes.
- Dolibarr may hold each stock-managed variant as a separate product/SKU.
- Supplier is a commercial relationship, not a canonical product category.
- One variant can have multiple SupplierProduct records.
- SEO/AI optimization is evaluated per Channel x Market using KEEP / ENRICH / REPLACE.
- Changes require evidence; successful existing pages are not rewritten automatically.
- Previous versions/baselines must be retained for rollback.
- Sync ownership: M99=identity/knowledge/SEO workflow; Dolibarr=stock/PMP/ERP; Channel=existing URL/record ID.
- Migration from old M99-PM/M99-PV IDs is phased through aliases, not destructive renaming.
