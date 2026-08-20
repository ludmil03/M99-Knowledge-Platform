# M99 Architecture v0.7.2.5 — m99.eu API Preflight & Sandbox Publisher

## Purpose

Phase 2.5 validates a real end-to-end channel before the general repository and
service layer is expanded.

Target channel: `m99.eu`.

The expected API is WooCommerce REST API v3 under:
`/wp-json/wc/v3`

## Safety sequence

1. Local API credentials are stored only in `admin-platform/.env.local`.
2. `.env.local` must be Git-ignored before tooling is installed.
3. Preflight performs a read-only GET against the products endpoint.
4. Dry Run generates the exact draft JSON without network access.
5. Create Draft requires explicit typed confirmation: `CREATE_DRAFT`.
6. The sandbox publisher hard-rejects any payload whose status is not `draft`.
7. Catalog visibility is hidden.
8. Mandatory read-back verifies ID, status, name and SKU.
9. There is no automatic publish operation.
10. There is no automatic product delete operation.

## Credential rules

Never paste WooCommerce Consumer Key or Consumer Secret into source code,
commits, README files, reports or ChatGPT conversations.

Local variables:
- M99EU_BASE_URL
- M99EU_API_PATH
- M99EU_WC_CONSUMER_KEY
- M99EU_WC_CONSUMER_SECRET
- M99EU_TIMEOUT_SECONDS

## Runtime order after Phase 2.5 is committed and pushed

`SETUP_M99EU_API_LOCAL.bat`

then

`RUN_M99EU_API_PREFLIGHT.bat`

then

`RUN_M99EU_DRY_RUN.bat`

and only after both are reviewed:

`RUN_M99EU_CREATE_DRAFT.bat`

## Test product

The test product is clearly marked with:
- SKU prefix `M99-API-TEST-`
- Draft status
- Hidden catalog visibility
- `_m99_sandbox=1` metadata

This test does not yet exercise images, categories, attributes, variations,
pricing policy, inventory mapping or public publication.

Those capabilities are deliberately deferred until basic CREATE + READ-BACK
has been proven safe.
