# R8-A agent execution plan

Date: 2026-11-17. Candidate base: `5f5e676776e84c2b99ffcea16cdd098d17ed9d58`.

This is an implementation task record, not a replacement master README or an
accepted release. Historical governance and acceptance evidence remain intact.

## Authorized goal

The operator requested autonomous coordinated agents, with questions only when
necessary. Success means one complete real product published and verified in at
least one channel, preferably two. Proposed targets are m99.eu and
rabotni-drehi.com. A simulation or hidden technical canary is preparation, not
success. Main must not be merged automatically.

Read-only checks, implementation, simulations and tests continue independently.
Existing canonical products must not be duplicated. The historical m99.eu
Product 2042 / M99 100019 marker needs authenticated readback before use.

## Agent responsibilities

| Role | Responsibility | Evidence |
| --- | --- | --- |
| Coordinator | Scope, integration, current state and blockers | This record and exact commit |
| Intake developer | Existing supplier selection and route continuity | HTTP route regressions |
| Supplier developer | Native and historical evidence preservation | Actual source dataclass fixtures |
| Publishing developer | Payload/plan validation and readback | Tamper and readback regressions |
| Test engineer | Reproducible root/admin suites on Linux and Windows | JUnit workflow artifacts |
| Independent reviewer | Correctness and readiness claims | Findings and focused checks |

Parallel tasks own distinct files. Independent review follows integration.
Agents must never report planned, simulated, tested or production behavior as
interchangeable. No credentials enter task reports, commits or workflow logs.

## Candidate changes

- Reuse the existing source-aware selection validator, including domain checks.
- Register the existing r730 publish-center router once.
- Preserve native Bultex identity, image and variant evidence in the existing
  shared supplier contract. Unknown price/VAT basis remains unproven.
- Bind reviewed authorization to exact operation, reference, target and XML.
  Legacy session plans require a fresh review.
- Validate actual product XML before network access; UPDATE XML must address the
  identity-resolved remote product.
- Compare supplied localized fields and associations during readback, alongside
  numeric/safety values and remote identity.
- Run maintained tests in explicit root/admin contexts. Declare missing lxml
  dependencies and retain Linux/Windows test evidence through GitHub Actions.

## Remaining implementation work

1. Bind the wizard to real discovery/review callbacks and canonical identity
   resolution; its current explanatory Identity step is insufficient.
2. Build the exact single-product authorization plan from approved canonical
   evidence and content, including review invalidation, expiry, one-use behavior
   and durable attempted-write/recovery state. Do not enable a button without
   implementing its producer and authorization checks.
3. Bind complete assets, localized ALT, variants/default combination, persisted
   pricing, taxes and category mapping to the shared publish service. Compare
   the complete intended result after all steps, not merely the product XML.
   Empty fields in the platform blank schema must not accidentally clear
   existing data in UPDATE operations.
4. Reuse the existing PrestaShop components; inspect and implement a generic
   WooCommerce adapter. The legacy Cherokee-specific WordPress path and
   readonly catalog adapter do not establish generic WooCommerce publishing.
5. Enforce operator-specific channel rights and fresh channel readiness; static
   registry flags are not live evidence.
6. Implement and verify bounded source cache, selected-only durable evidence and
   restart recovery according to M99-SP-001.
7. Confirm actual Windows runtime/module identity and local unpublished changes
   against the integrated candidate. Preserve main's runtime-manager work.

## Real publication prerequisites

The cloud workspace currently has no shop credentials or original Windows
operational database. It cannot inspect the operator's localhost application.
GitHub access alone does not provide shop access.

Use a secure runtime configuration mechanism for the existing m99.eu settings
(`M99EU_BASE_URL`, `M99EU_PS_API_KEY`, `M99EU_PS_TEST_CATEGORY_ID`) and the
appropriate WooCommerce configuration once its adapter is proven. Never paste
keys into chat or commit `.env.local`. A test category is not the approved final
production category. Obtain current product, category and tax evidence before
performing an authorized real write.

## Acceptance

1. Focused regressions, syntax/static checks and complete maintained suites.
2. Linux and Windows CI evidence; Windows runtime/operator acceptance remains
   separate from runner tests.
3. Full-product preflight and exact authorized channel/product/action scope.
4. Real publication through the M99 operator flow, mandatory API readback,
   customer-page verification and durable audit.
5. Record product URLs and IDs, variant/image/content/price/VAT checks per target.

No automatic retry after an ambiguous write. Recover by readback first.
Candidate commits and draft review do not promote a stable release. Until the
required gates and real publication succeed, R8-A is **NOT_RELEASEABLE** and the
business goal is **NOT_YET_ACHIEVED**.
