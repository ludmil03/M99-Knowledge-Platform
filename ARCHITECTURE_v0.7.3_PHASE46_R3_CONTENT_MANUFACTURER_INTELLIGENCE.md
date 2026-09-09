# M99 v0.7.3 Phase 4.6 R3 — Manufacturer Intelligence + Canonical Content

Three-pass README review performed before implementation: architecture/governance; content/language/benchmark; manufacturer evidence/publishing safety.

Language registry: BG / EN / RU / RO / GR + future languages. Current target defaults: m99.eu EN/BG/RU; mela99.com BG/EN; laviro.ro and alviro.ro RO/EN. Live channel language discovery may supersede defaults.

Benchmark framework: Amazon/Zalando/eBay for information hierarchy, scanability, variants, images, specifications and buying information; Apple for clarity/hierarchy/concise benefits/low-noise presentation; official exact manufacturer source for factual truth; Stenso/Palltex/category competitors for local market evidence without prose copying.

R3 adds a separate Content Intelligence control plane linked from Canonical Preview. Operator supplies official manufacturer website. Runtime performs bounded GET-only discovery, exact reference matching, same-domain crawl/sitemap/search-like seed discovery, image/document/table extraction, SSRF protection, explicit operator confirmation, DRAFT evidence persistence, and multilingual content bundle generation with H1, meaningful H2/H3, short/long descriptions, technical specification table, FAQ, Meta Title, Meta Description, SEO keywords, localized ALT and Product schema skeleton.

No channel write. No DB migration. No stock write. No silent Manufacturer approval. No unsupported technical claims.

## R3 content-quality contract

For `m99.eu` the current generated language bundle is EN/BG/RU. The engine creates natural localized product names, one H1, six or more meaningful H2 sections, H3 FAQ, short and long descriptions, technical specifications, official manufacturer tables, FAQ, Meta Title, Meta Description, keywords, Product schema and localized image ALT.

Manufacturer extraction captures headings, paragraphs, list items, tables, image candidates and document links. The RIVER fixture recognizes exact reference, Oxford fabric, 70/30 composition, 130 g/m², classic cut, stiffened collar, chest pocket, contrast details, OEKO-TEX, supported branding methods and size/measurement tables.

The runtime can persist only operator-confirmed manufacturer evidence and the generated content bundle into the existing DRAFT evidence snapshot. This is not a channel publish and does not approve a canonical Manufacturer role silently.


## R3 FIX2 — schema-adaptive preview

Windows runtime proved `ImportJobItem.detection` is not mapped.
R3 therefore must not treat transient Python attributes as durable evidence.

FIX2 carries the existing Canonical Preview source_uuid/product_url into the
Manufacturer Intelligence route and obtains supplier evidence through the
accepted R2 canonical-preview helper. Persistence is capability-detected.

Manufacturer + Content can be accepted as READ/VERIFY/PREVIEW without schema
mutation. Production auto-publish must later require durable approved content.


## R3 FIX3 — exact untracked-file allowlist

Windows acceptance reached 594 maintained tests PASS. The next gate exposed a
Git porcelain representation detail: default `git status --porcelain=v1`
collapses wholly-untracked directories to directory entries.

Release safety requires exact file allowlists, therefore the release driver now
uses `--untracked-files=all`. No application/runtime behavior changes.


## R3 FIX4 — active runtime route graph + source-context E2E

Real browser acceptance proved two facts after successful installer/regression:
1. `/content-intelligence/review` was absent from the active FastAPI route graph.
2. Canonical Preview possessed `source_uuid` and `product_url` in its request URL,
   but the generated Content Intelligence link emitted empty values.

FIX4 therefore:
- registers the R3 router directly in the proven active `app.main` entrypoint;
- verifies the real imported `app.main:app` route table contains
  `/content-intelligence/review`;
- builds the Content Intelligence link from `request.query_params`, so it uses
  the actual Canonical Preview request values rather than optional template vars;
- keeps R37 no-publish architecture intact;
- performs no channel write, migration, stock write, commit or push.

New release-engineering rule:
source-file registration is insufficient. A new web route must pass an
`app.main:app` active-route-graph import probe before operator delivery.


## R3 FIX5 — security-compatible active route probe

`app.main` intentionally requires `M99_SESSION_SECRET`. Release validation must
satisfy that prerequisite without weakening it. The installer now supplies a
cryptographically random secret only to the child route-probe process.

The value is not printed or persisted. Route acceptance verifies exact method +
path contracts for review/discover/confirm.


## R3 FIX6 — consolidated active runtime context

Active-runtime acceptance must reproduce the real process context, not only the
source tree. For M99 Admin this includes:
- PYTHONPATH including admin-platform;
- an ephemeral process-only M99_SESSION_SECRET for the acceptance child;
- current working directory = admin-platform;
- relative runtime resource `app/static` present.

The route graph is accepted only after importing the real `app.main` under those
conditions and verifying exact HTTP methods and paths.


## R3 FIX7 — normalized Admin runtime root

The release driver now defines a single canonical runtime root:

`ADMIN = REPO / "admin-platform"`

All runtime-sensitive checks use this root consistently: virtualenv, PYTHONPATH,
template tree, relative static resources and active `app.main` import cwd.

This prevents probe-only NameError/cwd drift and makes the acceptance context
match the real Admin process.


## R3 FIX8 — Manufacturer identity usability contract

Manufacturer source identity and supplier source identity are separate.

A known Manufacturer is resolved against ACTIVE approved sources of kind
`MANUFACTURER`. Its official `base_url` is reused automatically. The operator
does not re-enter the URL for every product.

`UNKNOWN` Manufacturer is explicitly supported. It does not block DRAFT.
Manual official-site entry is an optional override only.

Manufacturer product code is resolved by evidence priority:
1. verified Manufacturer evidence;
2. explicit Manufacturer code/reference from supplier evidence;
3. supplier reference as a candidate requiring exact official-page verification;
4. UNKNOWN.

Discovery is a safe UI operation: external/network/content-generation failures
must return to the review screen with an explanatory warning, never a raw 500.


## R3 FIX9 — accepted prestate is cumulative

A later installer must validate the cumulative accepted working tree, not an older
phase subset. For this chain the valid prestate is exactly `R2 | R3 | FIX4`.

`app/main.py` and the active-route E2E test are expected accepted files, not
unexpected drift.


## R3 FIX10 — discovery collection contract

Discovery helper outputs are normalized at composition boundaries. `_sitemap`
may return tuple/list/empty sequence; the discovery queue converts it explicitly
to a list before composing seed/search URLs.

Operator-visible discovery remains fail-safe and must not expose a raw 500.


## R3 FIX11
Evidence collection boundaries normalize tuple/list containers before composition.
Affected E2E: exact candidate -> provisional manufacturer evidence -> build_content_bundle -> _profile -> review.
