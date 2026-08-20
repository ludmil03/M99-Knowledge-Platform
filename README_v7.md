# M99 Knowledge Platform

**README v7**  
**Stable baseline:** M99 v0.7.1 — Platform Consolidation & Test Baseline  
**Baseline commit:** `8c3d2d7fc729f22001c320d1fa033528272eb21e`  
**Status:** Stable development baseline  
**Date:** 2026-08-20

## 1. Purpose

M99 Knowledge Platform is the central product identity, knowledge, supplier, market intelligence, SEO, publishing and integration layer for the M99 ecosystem.

The platform is designed as a Single Source of Truth. External systems such as supplier databases, manufacturer websites, MoneyWork, Dolibarr, online stores and marketplaces are sources, destinations or operational systems; they do not own the canonical M99 identity.

The long-term objective is to connect product knowledge, suppliers, customers, inventory operations, websites, ERP/CRM, SEO, AI and automation without duplicating core business data.

## 2. Core architectural principles established

1. **M99 owns canonical identity.** External IDs are mappings, not the master identity.
2. **Knowledge is evidence-driven.** Facts retain source, provenance and confidence.
3. **Product knowledge and market knowledge are separate but connected.**
4. **A market is not a channel.** Websites and marketplaces are channels within markets.
5. **Product groups are dynamic.**
6. **Verified facts cannot be silently overwritten by AI or uncertain imports.**
7. **Historical observations must be preserved.**
8. **ERP systems operate the business but do not own M99 knowledge.**
9. **SEO and content are market-specific and channel-aware.**
10. **Removing a product from a channel must not destroy its accumulated knowledge.**

## 3. Canonical product and data model

The architecture has evolved toward the following canonical chain:

`ProductGroup → ProductVariant → SupplierOffer → Evidence → ChannelPresence → ChannelContent → ChannelPrice → InventoryMapping`

The product identity layer separates the logical product/model from commercially or technically distinct variants. External identifiers such as supplier SKU, manufacturer SKU, EAN/GTIN, MoneyWork code, Dolibarr ID, website ID or marketplace ID are stored as mappings to M99 entities.

The identity resolution flow is controlled:

`External Record → Import → Normalization → Resolver → Matcher → Decision → Overrides → Operator Review → Final M99 Identity`

Uncertain records must not silently modify canonical identity.

## 4. ProductGroup governance

ProductGroup is treated as a governed business entity with lifecycle:

`draft → active → paused → retired`

Normal lifecycle transitions replace destructive deletion. Hard deletion remains possible only as an exceptional operator action, after explicit approval and manual confirmation with `DELETE`, with the action recorded for auditability.

## 5. Markets, channels and product groups

The platform is designed as multi-market and multi-channel.

Current channel scope includes:

- mela99.com
- rabotni-drehi.com
- m99.eu
- medicinski-drehi.com
- toplinka.com
- laviro.ro
- alviro.ro

The architecture separates Market, Channel and ProductGroup and introduces Channel/ProductGroup mappings so a new market or website does not require redesigning product identity.

Configuration-driven markets, channels and product groups are the target direction.

## 6. Knowledge and evidence

M99 distinguishes a fact from the evidence supporting it.

Evidence can originate from manufacturers, official documentation, certificates, suppliers, ERP data, websites, competitors, customers, salespeople, field tests, service technicians, operators and AI inference.

Technical truth should prefer authoritative manufacturer and certification sources. Supplier and competitor information remains useful evidence but must not silently replace stronger verified sources.

AI is intended to work on verified knowledge and explicitly identified inference, not to invent missing technical facts.

## 7. Supplier and external-data architecture

Supplier information is not treated as canonical product identity. Supplier records map to M99 products and variants through controlled resolution.

The architecture supports supplier-specific offers, codes, prices, availability and evidence while preserving one canonical M99 product identity.

Work completed to date includes supplier/import foundations, parser and test work, including the Bultex B2B parser test baseline.

## 8. MoneyWork and migration direction

MoneyWork is treated as a legacy/operational source, not the owner of M99 identity.

The preferred migration path is:

`MoneyWork → M99 Import / Identity Resolution → Confirmed M99 Identity → Dolibarr + Websites + Other Channels`

This prevents legacy accounting or ERP identifiers from becoming permanent business identity.

CSV data for products, suppliers and customers has been considered as migration input, with the intention to normalize, match and validate records before operational synchronization.

## 9. Dolibarr role

Dolibarr is the planned operational ERP/CRM layer for:

- inventory and warehouses;
- purchasing;
- suppliers;
- customers;
- sales;
- CRM;
- orders;
- deliveries;
- invoicing;
- logistics.

The separation of responsibility is:

`M99 Knowledge Platform = identity + knowledge + governance`

`Dolibarr = operations + stock + purchasing + CRM + sales + logistics`

Future integration must use explicit M99 ↔ Dolibarr mappings rather than allowing Dolibarr IDs to become M99 identity.

## 10. Publishing and websites

The target publishing flow is:

`M99 Product → Knowledge Validation → Channel Rules → Market Rules → Content Generation → SEO Validation → Operator Review → Publish`

The platform is intended to support differentiated content per site and market, including Bulgarian, English and Romanian content where required.

Publishing targets include the current M99 websites and future marketplaces/channels.

## 11. SEO, AI and content direction

The platform foundation is intended to support automated generation and validation of:

- SEO titles and meta descriptions;
- H1 and heading structures;
- product and category descriptions;
- FAQ;
- image ALT text;
- structured data;
- internal-linking recommendations;
- translations;
- blog and editorial content;
- social and marketing content.

The long-term rule is that generated content must be based on canonical, verified knowledge and channel/market context.

## 12. Repository and architecture consolidation

The repository has progressed through multiple architecture revisions from v0.5.x and v0.6.x into the v0.7.x consolidation stage.

The project contains architecture history, core modules, configuration, data, documentation, integrations, knowledge assets, scripts, state and tests. Architecture history is intentionally preserved rather than overwritten so major design decisions remain traceable.

A v1 target architecture was added during the v0.7.1 consolidation to define stable future namespaces and responsibilities.

## 13. Admin platform baseline

An administrative platform baseline was prepared and placed under controlled Git workflow. The work introduced application configuration, database/security foundations, routes/entities/preflight structure and a local development environment.

Because the admin layer is operationally sensitive, changes are handled through SAFE installers, explicit test gates, rollback and operator confirmation rather than uncontrolled direct modification.

## 14. SAFE development workflow established

A major achievement of v0.7.1 is the introduction of a repeatable safety workflow for changes.

The workflow now follows:

`Known Git baseline → clean working tree → controlled patch → dependency check → Python compile → full pytest → review changed files → explicit COMMIT → Push only after review → final read-only verification`

The SAFE tools intentionally avoid automatic push. Failed gates trigger rollback to the known baseline.

This workflow was tested through multiple revisions until the complete suite passed.

## 15. Test baseline

During v0.7.1 consolidation, the Python test environment was normalized and pytest dependencies were made explicit.

A malformed Bultex parser test was diagnosed in stages. The final correction converted the complete test to native pytest syntax instead of patching individual lines.

The final gate result was:

**234 tests passed**

This is the accepted test baseline for M99 v0.7.1.

Future changes should preserve or intentionally update this baseline; tests must not be disabled merely to make a release pass.

## 16. Stable v0.7.1 baseline

The final Revision 7 commit is:

`8c3d2d7fc729f22001c320d1fa033528272eb21e`

Commit subject:

`feat(v0.7.1): platform consolidation and test baseline rev7`

Final read-only verification confirmed:

- branch: `main`;
- Local HEAD equals the stable commit;
- `origin/main` equals the same commit;
- working tree is clean;
- ahead of origin/main: `0`;
- behind origin/main: `0`;
- synchronization: PASS;
- final result: PASS.

Therefore **M99 v0.7.1 — Platform Consolidation & Test Baseline** is the stable recovery and development baseline.

## 17. What must not be changed casually

The following rules are now architectural constraints:

- M99 canonical identity must not be replaced by external IDs.
- ProductGroup lifecycle must be preserved.
- Hard deletion requires explicit operator governance.
- Uncertain imports must not silently alter verified identity.
- Evidence provenance must remain traceable.
- Market, Channel and ProductGroup must remain separate concepts.
- ERP functionality should not be duplicated unnecessarily in M99.
- Website removal must not delete accumulated product knowledge.
- Test gates and rollback must remain part of controlled changes.
- Push to GitHub must remain a deliberate step after verification.

## 18. Next version

The recommended next development stage is:

# M99 v0.7.2 — Canonical Data Model Foundation

Primary objectives:

1. Stabilize the canonical ProductGroup / Product / ProductVariant model.
2. Formalize SupplierOffer and supplier mappings.
3. Formalize Market and Channel registries.
4. Implement ChannelProductGroup / ChannelPresence mappings.
5. Define customer and supplier master-data boundaries between M99 and Dolibarr.
6. Define inventory mappings without duplicating ERP stock logic.
7. Prepare deterministic M99 ↔ Dolibarr synchronization contracts.
8. Preserve evidence, lifecycle and operator-approval rules.
9. Expand tests before new automation and publishing work.
10. Keep v0.7.1 as the immutable recovery baseline.

## 19. Development rule from this point forward

Every significant change should be made from a known stable baseline and should pass:

- repository-scope verification;
- dependency verification;
- compile checks;
- relevant unit/integration tests;
- full regression tests when applicable;
- changed-file review;
- explicit operator commit approval;
- post-push synchronization verification.

## 20. Current status

**Stable version:** M99 v0.7.1  
**Stable commit:** `8c3d2d7fc729f22001c320d1fa033528272eb21e`  
**Tests:** 234 passed  
**Branch:** main  
**Local/remote synchronization:** verified  
**Next planned version:** M99 v0.7.2 — Canonical Data Model Foundation

---

M99 Knowledge Platform is no longer only a collection of product data and scripts. At the v0.7.1 baseline it has a defined identity model, evidence rules, market/channel architecture, ERP boundary, lifecycle governance, test baseline and controlled development process. The next phase is to turn these architectural rules into a stable canonical data model that can safely support suppliers, customers, Dolibarr, inventory mappings, websites, SEO, AI and future automation.
