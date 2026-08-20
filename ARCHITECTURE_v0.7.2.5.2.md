# M99 Architecture v0.7.2.5.2 — XML-Safe m99.eu PrestaShop 9 Sandbox Publisher

m99.eu is PrestaShop 9.1.5.

The original WooCommerce runtime is superseded.

The corrected integration uses:
`https://m99.eu/api/`

Key safety rules:
- API key only in Git-ignored `.env.local`;
- read-only preflight first;
- dry run performs no POST;
- create requires two explicit `CREATE_INACTIVE` confirmations;
- product is forced to `active=0`;
- ordering disabled;
- one configured test category;
- mandatory read-back;
- no images, stock updates, public activation or DELETE in the first test.

Testing rule:
All XML fixtures are generated programmatically via ElementTree.
No manually typed XML fixture is used for read-back tests.
Dedicated PrestaShop tests must pass before the full regression suite.
