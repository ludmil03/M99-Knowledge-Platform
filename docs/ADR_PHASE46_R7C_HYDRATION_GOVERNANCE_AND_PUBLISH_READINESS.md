# ADR Phase 4.6 R7C — Hydration Governance + Publish Readiness

R7C integrates R7A/R7B governance into the real Calenda dispatch: `unified_add_products.hydrate_product -> CalendaPublicConnector.get_product`. It rejects colour/size tokens as Supplier Reference, keeps `IDnnn` as a separate Calenda identity role, preserves numeric/PREFIX supplier-reference candidates, cleans brand contamination, removes shared duplicate images from per-colour claims, and never infers Manufacturer MPN from supplier hydration.

R7C does not perform a website write. It captures the exact current R1/m99.eu publish chain so the next live-pilot package can wire the canonical multilingual payload into the existing duplicate-guard/readback/audit path without guessing. No DB migration, stock write, commit or push.
