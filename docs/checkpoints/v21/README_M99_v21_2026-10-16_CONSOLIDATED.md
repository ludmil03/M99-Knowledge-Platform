# M99 Knowledge Platform — README v21 | Consolidated Governance, History & Safe GitHub Checkpoint

**Дата:** 16.10.2026  
**Статус:** DOCUMENTATION PREPARED / LOCAL GIT AUDIT PENDING / NOT COMMITTED / NOT PUSHED  
**Проект:** `ludmil03/M99-Knowledge-Platform`  
**Предназначение:** историческа и нормативна памет + план за безопасна консолидация + протокол за проверка и публикуване на локални Git промени.

> Важно: Това README е създадено от предоставените материали. Не удостоверява текущия локален Git HEAD, съдържанието на 38-те исторически променени файла или завършено публикуване. Нито един локален файл не е автоматично качен в GitHub Desktop/GitHub.

## 0. Правила за приоритет и достоверност

- При конфликт важи **най-новото изрично решение, което отменя предишното**, а не най-големият номер на README.
- v20 (27.09.2026) е по-стар по дата от v19 (06.10.2026). Важат по-късните изрични решения от v19, включително `/add-products` вместо `/operator/add-products`.
- Governance M99-SP-001 от 08.10.2026 е следващо одобрено правило за selective persistence, но изпълнението му трябва да бъде доказано в кода.
- `DECIDED != IMPLEMENTED != TESTED != WINDOWS_ACCEPTED != REAL_M99_ACCEPTED != REMOTE_VERIFIED`.
- Не презаписвай историческите README; добавяй нови версии и индекс.

## 1. Цел, път и развитие

Проектът започва като M99 Style Guide и M99 Knowledge Base за автоматизация на SEO, описания, FAQ, ALT и локализация на продукти. Развива се до централен knowledge/control слой за Supplier/Manufacturer/Brand evidence, canonical identity, content, images, variants, pricing/VAT, multi-channel publishing, API readback, Dolibarr, поръчки, склад, куриери и audit. Целта е малък екип, надеждна автоматизация, международна експанзия BG/EN/RO и дългосрочният M99 Group Master Plan 2036, включително целеви нетен доход 10 000 EUR/месец. Това е бизнес цел, не гарантиран резултат.

### Исторически етапи

- 2026-07: M99 Style Guide, Knowledge Base, Product ↔ ProductGroup ↔ Channel, SEO/marketing assistants.
- 2026-08: Dolibarr/CRM, MoneyWorks migration planning, supplier connector contracts, безопасни Windows installers; v0.7.1 Rev7 — 234 tests PASS (исторически).
- 2026-09: Canonical data model, SQLAlchemy/Alembic baseline, PrestaShop 9 интеграция, Palltex/BWolf controlled publishing, Calenda evidence/variants, Bultex99 public/B2B separation, R7.3.0 unified direction; README v14/v15/v16.
- 26.09: v18 recovery checkpoints, PowerShell/Git release gates, historical Product 2041 / M99 100018 pilot; местен HEAD и branch подлежат на нова проверка.
- 27.09: v20 Consolidation R1: три supplier линии → един M99 Unified Product Intake Engine, 8 selection modes, един operator workflow.
- 06.10: v19: `/add-products`, оригинално dirty worktree с исторически 38 промени, отделно clean runtime worktree, R7/R7 R1 Windows PASS и REAL M99 FAIL за legacy R3.7 PREPARE authorization.
- 08.10: M99-SP-001 — не огледално съхраняване на каталози; on-demand source access, bounded cache, selected-only persistence, governed evidence, fail-closed writes.
- 16.10: Операторът одобрява общия supplier process, добавяне на нови доставчици чрез adapters, а не нов importer, и иска пълен Git audit + documentation checkpoint. GitHub commit/push остават зависими от реалната локална проверка.

## 2. Непроменими бизнес и safety правила

- Knowledge First; Evidence Based; No Duplicate Data; Identity Before Content; AI Native, not AI Invented.
- Supplier != Manufacturer != Brand; Supplier Reference != Manufacturer MPN.
- M99 canonical ID: `M99 ` + точно шест цифри; историческите M99- кодове са compatibility only. ID не се използва повторно.
- Identity: NEW / EXISTING / AMBIGUOUS / UNRESOLVED; при двусмисленост — без автоматичен write.
- ProductGroup: draft → active → paused → retired; hard DELETE само с operator approval + ръчно `DELETE` + audit.
- CREATE != UPDATE; UPDATE не преминава тихо в CREATE; duplicate guard преди CREATE.
- Supplier availability != M99 physical stock; видим размер не доказва наличност.
- AI не измисля стандарти, сертификати, материали, характеристики, stock или снимки.
- Изображения: manufacturer → verified supplier → verified cached original; продуктова относимост, variants, WebP около 1200–1400 px, ALT и readback.
- Цени: customer-facing GROSS/VAT included, verified supplier gross benchmark минус persist-нат случаен процент 1.0–1.7%; при NO_CHANGE → NO_WRITE; VAT се разрешава по channel/market, без глобален hardcode; production rounding изисква доказателство.
- Целеви езици на canonical knowledge: BG, EN, RU, RO според нуждите; channel language IDs се откриват за конкретния магазин.
- WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY; NOT_SELECTED != BLOCKED.
- API success != business acceptance; readback е задължителен; без автоматичен retry при ambiguous write.
- Нормалният оператор работи през M99 UI, не през Python/PowerShell/CMD.

## 3. Supplier архитектура и добавяне на нов доставчик

Един **M99 Unified Product Intake Engine**, с отделни supplier-specific adapters. Повторно използване: Bultex99 — selection/public/B2B separation/identity preview; Calenda — hydration/evidence/variants/images; Palltex — durable evidence/identity/content gates/controlled publishing/readback. Не се създава четвърти importer. За нов доставчик се избира API, XML/CSV, разрешен B2B или public-site adapter, като данните се нормализират към съществуващия contract. Конфигурируем адаптер е предложение, а не доказана вече имплементирана функция.

Операторски поток: `/add-products` → Supplier → Category/Product → bounded discovery → Hydrate/Verify → operator recovery → Identity → Canonical Product/DRAFT → Content/SEO → Price/VAT → QA → Channels → Review → Publish → Readback → Audit.

Selection modes: one product, multiple products, one category, multiple categories, all products, first N, only new to M99, manual selection. При category batch: общ preflight и human by exception. Не се пази целият supplier catalog; трайно се съхраняват избраните продукти и governed evidence, останалото е ограничен временен кеш.

**Feya.bg**: обсъден е примерен DRY RUN за `category` → `mela99.com` и `m99.eu`; това НЕ доказва съществуващ работещ Feya adapter или действително извлечени продукти. Няма реално публикуване.

## 4. Канали и ERP

Целеви канали: mela99.com, m99.eu, rabotni-drehi.com, medicinski-drehi.com, laviro.ro, alviro.ro, toplinka.com, Dolibarr. Channel ID остава стабилен; CMS/version/adapter са заменяеми, версионирани профили. Доказана версия в историческия v16/v18 baseline: m99.eu PrestaShop 9.1.5; mela99.com thirty bees 1.7; laviro.ro PrestaShop 1.6.1.24; останалите версии/платформи изискват актуален read-only preflight, понеже v16 и v20 съдържат различни сведения за някои магазини. Dolibarr е ERP/CRM/warehouse execution layer, а не knowledge master; физическото намаляване на складова наличност при продажба/експедиция е нерешен исторически проблем.

## 5. Доказано и недоказано състояние

- Исторически: v0.7.1 234 PASS; R7.2.8 Windows precheck 1050 PASS/NO WRITE; v18 Product 2041 focused 129 PASS; full regression PASS според съответните checkpoints.
- Product 2041 / M99 100018 е EXISTING/UPDATE ONLY, hidden/non-orderable technical pilot, а не готов за продажба. Не създавай дубликат и не го активирай без пълни gates.
- README v19: R7/R7 R1 Windows PASS, но REAL M99 FAIL: `R3.7 PREPARE failed: Operator is not authorized for requested target(s): rabotni-drehi` при избор mela99.com + rabotni-drehi.com + m99.eu + laviro.ro.
- По-късни R7 R2.x архиви са налични за анализ, но не са автоматично признати за реално приети. Нужен е точен local runtime/branch/readback audit.
- Нито историческите тестове, нито това README доказват текущо успешно end-to-end publishing.

## 6. Git / GitHub Desktop: задължителна проверка преди commit

Оригинално локално repo: `C:\Users\user\Documents\GitHub\M99-Knowledge-Platform`. Исторически към 06.10.2026 GitHub Desktop показва ~38 changed files на `dev/m99eu-auth-readonly...`; това НЕ е текущо проверен status. Отделно clean worktree: `C:\Users\user\Documents\GitHub\M99-CANONICAL-ADD-PRODUCTS-V6-R1\M99-Knowledge-Platform`.

**Забранено без ново изрично одобрение:** Commit All / blind stage; `reset --hard`, `git clean`, force push, неконтролиран merge/rebase, process kill, DB migration, website write. Не се комитват `.env.local`, API keys, пароли, токени, `.venv`, временни архиви и credentials.

Проверка: (1) branch/HEAD/upstream/status на всеки worktree; (2) `git diff --name-status`, `git diff --cached`, `git ls-files --others --exclude-standard`; (3) преглед на всяка промяна и проверка за secrets; (4) tests/AST/encoding/known defects; (5) списък на липсващите README в **точния целеви branch**; (6) exact-file staging; (7) commit след приемане; (8) push; (9) remote SHA и съдържание readback. Изисква се operator review на текущите 38 (или актуалния брой) файла.

## 7. Проверка на GitHub към 16.10.2026 (само точни пътища)

- `main`: README.md и README_M99_v15_2026-09-14.md намерени. При точните root пътища README v16/v18/v19/v20 не са намерени. Това НЕ доказва липса на друго място или в друг branch.
- `docs/m99-sp-001`: README v15, v18, v20 и docs/governance/M99_GOVERNANCE_RULE_M99-SP-001_2026-10-08.md са намерени. README v16/v19 не са потвърдени на проверените точни пътища.
- Без проверка на локалния GitHub Desktop status НЕ се прави bulk commit/push на съществуващите промени. Създадените v21 файлове са локални артефакти за преглед и не са remote-verified.

## 8. Release protocol и критерии за готовност

`STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE → REAL_M99_UI_ACCEPTANCE → COMMIT → PUSH → REMOTE_VERIFY`.

За документационен checkpoint се правят file/hash/encoding/link/branch/secret review и точен Git commit/push/readback. За изпълним код се добавят всички runtime gates. Failed revision никога не става stable baseline. Не се маркира COMPLETE преди remote verify.

## 9. Следващ етап след безопасния Git checkpoint

1. Consolidation Map R1: точен file/function/test/route/branch/acceptance inventory; authoritative/reuse/legacy/deprecate/test-history.
2. Unified supplier adapter contract, reuse на трите линии и SP-001 selected-only persistence.
3. Един `/add-products` flow и per-target PREPARE authorization без заобикаляне на правата.
4. Един channel publishing service с отделни CREATE/UPDATE, full payload, VAT, QA и mandatory readback.
5. MAXSIM + Windows + REAL M99 acceptance преди commit/push на runtime промени.

## 10. Исторически източници и пълни архивни записи

Историческите README са запазени в отделни файлове и са приложени по-долу като неизменени изходни текстове за възстановяване на подробностите. При несъответствие между исторически checkpoint и настоящия статус важат правилата в §0.


---

# АРХИВНО ПРИЛОЖЕНИЕ — v15 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — README v15

**Checkpoint date:** 2026-09-14  
**Repository:** `ludmil03/M99-Knowledge-Platform`  
**Local repository:** `C:\Users\user\Documents\GitHub\M99-Knowledge-Platform`  
**Branch:** `main`  
**Document role:** Master System Constitution + Consolidated Decision Registry + Current Live Acceptance + R7K.4 Production-Scale Direction  
**Previous master:** README v14 (2026-09-13), preserved as historical checkpoint.

> This v15 checkpoint supersedes stale current-state statements where a later explicit decision or accepted runtime milestone exists, while preserving historical facts.

## 0. Статут на документа и правило за приоритет

README v15 е следващият master human-readable checkpoint. Той наследява всички валидни решения от README v1-v14 и ги допълва с приетите решения до 14.09.2026 г. При противоречие важи най-новото изрично superseding решение. `DECIDED != IMPLEMENTED`: дефект в реализацията не отменя архитектурно решение. Преди архитектурна промяна задължително се четат: Decision Registry -> Current Context -> Project State -> latest README -> relevant ADR -> tests/history -> proposal.

---
## 1. Визия и бизнес предназначение

M99 Knowledge Platform е централен слой за canonical identity, verified product knowledge, supplier/manufacturer evidence, commercial intelligence, content/SEO, publishing, synchronization, ERP/CRM integration, audit и governance за M99 Group. Платформата не е само scraper и не е uploader за един сайт. Целите са международно развитие, минимален административен headcount, максимална безопасна автоматизация, контрол на cash flow/stock и дългосрочна подкрепа на M99 Group Master Plan 2036.

---
## 2. Канали и destinations

NEW PRODUCT IMPORT винаги предлага explicit multi-select на target destinations. Операторът може да избере един, няколко или всички разрешени READY web channels и, когато workflow позволява, Dolibarr. Няма автоматично "всички" по подразбиране. Реалният write set е `REQUESTED ∩ AUTHORIZED ∩ READY`. `NOT_SELECTED != BLOCKED`. Daily Existing Product Sync не използва нов target selection и никога не създава липсващ channel mapping.

---
## 3. Canonical identity и lifecycle

M99 identity е независима от supplier SKU/reference, Manufacturer MPN, EAN/GTIN, MoneyWork code, Dolibarr ID, channel product ID, title и URL. Новият нормативен формат е `M99 ` + точно шест цифри; старите hyphenated references се пазят само като legacy/compatibility. Идентичността никога не се reuse-ва. ProductGroup lifecycle е `draft -> active -> paused -> retired`. Hard DELETE е изключение: operator approval + ръчно `DELETE` + audit. Identity се решава преди content. States: NEW / EXISTING / AMBIGUOUS / UNRESOLVED.

---
## 4. Supplier / Manufacturer / Brand / Evidence

Supplier и Manufacturer са отделни роли, дори когато една Organization изпълнява и двете. Supplier Reference и Manufacturer MPN са различни semantic fields, дори когато стойността им съвпада. Brand е отделен canonical object. Нов Supplier/Manufacturer/Brand изисква Super Admin governance. Evidence priority: exact official manufacturer -> official documentation/certificate -> validated B2B -> exact supplier -> verified internal data -> operator -> AI over verified facts. Observation не става автоматично canonical truth. Durable manufacturer evidence може да се reuse-ва само по exact governed scope, без fuzzy/brand-wide inference.

---
## 5. Operator UX и автоматизация

Операторът е бизнес потребител, не програмист. Нормалният workflow не трябва да изисква Python, PowerShell, HTTP, JSON/XML, SQL, credentials или вътрешни paths. Новият основен принцип е `Human by exception, not by repetition`: повторяемите решения с одобрени правила се автоматизират. За category/multi-product import няма product-by-product typed confirmations. Всеки product/target се класифицира машинно като AUTO_READY, NEEDS_REVIEW или BLOCKED. Операторът одобрява batch-ready set и обработва само exceptions/conflicts/high-risk anomalies/destructive actions.

---
## 6. New Product Import и batch processing

Един engine трябва да поддържа 1 продукт, много продукти, една/много категории, first N, only-new-to-M99 и manual selection без product-specific code. Всеки import е auditable ImportJob. Category workflow: supplier/source selection -> category/product selection -> explicit target selection -> automated hydration/evidence/identity/price/VAT/content/images/variants/preflight -> Batch Review -> publish only AUTO_READY -> quarantine NEEDS_REVIEW/BLOCKED -> strict readback -> Batch Quality Report.

---
## 7. Publishing constitution

CREATE != UPDATE. Duplicate guard before CREATE. Mandatory readback after every write. HTTP/API success != Product Quality PASS. Activation requires authorization. Final category is operator-owned. Approved identity/locked fields са защитени. CLI/BAT са development/diagnostic tooling, normal operations стартират от M99 Admin. Автоматизацията е fail-closed: failed critical gate блокира конкретния product/target; unrelated AUTO_READY items могат да продължат, освен при systemic failure.

---
## 8. Цени: източник, ежедневно наблюдение и публикация

Supplier commercial price се наблюдава ежедневно за canonical products с verified Supplier/Source mappings. Source priority за commercial facts: validated B2B connector, ако е наличен; иначе exact supplier product page. Category/search/competitor page не е достатъчно price evidence. SupplierObservation пази source/product/variant identity, URL/resource, observed_at, verified_at, price, currency, availability, changed_fields и verification/provenance state.

M99 target selling price е customer-facing GROSS/VAT-included. Новото business pricing правило е: `M99 target GROSS = verified supplier benchmark GROSS × (1 - r)`, където `r` е random процент от 1.00% до 1.70%. Процентът се генерира при първоначално pricing и при verified supplier-price change. Ако benchmark price не се е променил: `NO_CHANGE -> NO_WRITE` и не се прави gratuitous re-randomization. При промяна pipeline е: SupplierObservation -> PRICE_CHANGED -> approved pricing rule -> market currency -> VAT -> target GROSS -> platform NET representation if required -> API write -> readback -> Front Office gross verification. Suspicious/out-of-policy anomalies -> NEEDS_REVIEW.

---
## 9. VAT / данъчни правила

VAT е channel/market configuration и не се hardcode-ва универсално. Standard VAT rule/rate се resolve-ва от конкретния target store/market. Ако платформата пази NET, M99 изчислява platform NET от target GROSS. `id_tax_rules_group=0` блокира production quality за стандартно облагаем продукт. API/Back Office price alone не е достатъчен; след write се проверява customer-facing Front Office gross price. 0.00 при очаквана ненулева цена е PRICE_GATE FAIL.

---
## 10. Content, SEO, AEO/GEO и benchmark

Content Engine работи върху verified Product Knowledge. Supplier prose не се копира verbatim. Facts могат да са общи, но prose/SEO са channel/market/language specific. AI може да структурира, пише и превежда verified facts, но не измисля standards/materials/stock/technical claims. Customer-facing content не трябва да съдържа вътрешен M99 governance/evidence/debug текст. Meta Description и Short Description са различни assets; normalized similarity < 0.75. Language purity е critical gate.

Benchmark: Amazon/Zalando/eBay за information hierarchy, scanability, variants, images, specification clarity и buying information; Apple за clarity, hierarchy, concise benefits и low-noise presentation; exact official manufacturer source за factual accuracy; Stenso/Palltex и релевантни местни конкуренти за terminology, assortment, price positioning и content gaps без copying. Search benchmark се открива динамично по country/language/query.

---
## 11. Images

Image source priority: official manufacturer -> verified supplier -> verified cached original source. Друг M99 channel не е master image source само защото вече има правилната снимка. Pipeline: Discover -> Verify -> Download -> Relevance Check -> Dedupe -> Resize ~1200-1400 px -> WebP -> localized ALT -> operator/policy review -> Upload -> Association -> Readback. Theme/logo/cart/search/header assets и unrelated images се reject-ват. Variant-specific image relationship се пази, когато source го доказва.

---
## 12. Variants, combinations, availability и stock

Visible size != stock. Presence != stock. Supplier availability != M99-owned physical stock. Supplier status не създава invented quantity. Numeric external quantity се пази само при reliable exact source quantity. Variational product трябва да има точно една default combination; cache/default pointer трябва да съвпада. Combination price impact = 0 по подразбиране, освен при доказана реално различна variant selling price. Out-of-stock variant не се delete-ва само защото е временно unavailable.

---
## 13. Daily Existing Product Sync

Daily Sync е отделен operational class от New Product Import. Всеки ден се проверяват supplier/B2B price, availability, variants/sizes, product changes и discontinuation. States: NO_CHANGE, PRICE_CHANGED, AVAILABILITY_CHANGED, VARIANT_AVAILABILITY_CHANGED, PRODUCT_CHANGED, SUPPLIER_DISCONTINUED, VERIFICATION_FAILED. Source outage/parser error = VERIFICATION_FAILED, не OUT_OF_STOCK/0. Sync пише само changed fields според policy и само към вече съществуващи allowed channel/ERP mappings; не създава missing channel products.

---
## 14. Product Quality Gate и readback

Critical gates включват IDENTITY, MANUFACTURER_EVIDENCE, SUPPLIER_MATCH, PRICE, VAT, CURRENCY, LANGUAGES, CONTENT, SEO, TECHNICAL_FACTS, IMAGES, ALT, VARIANTS, DEFAULT_COMBINATION, TEST/DRAFT or governed publication state, READBACK, FRONT_OFFICE, NO_INVENTED_CLAIMS и NO_UNVERIFIED_STOCK. Numeric score никога не override-ва failed critical gate. Batch Quality Report трябва да показва success/readback counts и exception reasons.

---
## 15. Dolibarr, warehouse, MoneyWork и CRM

M99 е canonical identity/knowledge/governance layer. Dolibarr е operational ERP/CRM/warehouse. M99-owned physical stock: supplier order reception -> increase; customer shipment -> decrease; variant-aware. SUPPLIER_EXTERNAL / MANUFACTURER_EXTERNAL availability warehouses са отделни от M99_PHYSICAL. MoneyWork и legacy sites са reconciliation sources, не canonical masters. Preferred migration: Inspect -> Normalize -> Deduplicate -> Identity Map -> Supplier/Customer Map -> Dry Run -> Import -> Reconcile -> Audit. CRM foundation: First call -> Offer -> Second call.

---
## 16. Security, RBAC и audit

Operators никога не виждат channel/B2B credentials. Secrets не се commit-ват в Git, не се log-ват и не се показват в screenshots. Permissions се enforce-ват server-side. Authentication direction: secure password hashing, sessions/logout, timeout, failed-login protection, reset workflow, login/logout audit, future 2FA. Central logs: Audit, System, Supplier/B2B & Channel Integration, Security. Minimum context: timestamp, severity, user, module, operation, entity, supplier/channel, job_id, result, message, correlation_id.

---
## 17. Release engineering и Git safety

Self-Tested Release Process: преди Windows delivery се правят максимални static/package audits, AST/compile, path validation, hashes, mocked success/failure, rollback simulation, tests, secret/no-write audit и exact release scope. Windows/CMD е final environment acceptance, не първо debugging място. Installer не прави website write/migration/commit/push освен ако release contract изрично не го разрешава. След accepted milestone: Git audit -> maintained regression -> secrets guard -> git diff --cached --check -> exact staging -> commit -> refetch/remote-parent check -> push -> verify HEAD==origin/main -> record SHA. Никога blind Commit All.

---
## 18. Текущ доказан live milestone

R7K.3.2.2 е accepted Windows install milestone: 894 incoming maintained PASS, 11 dedicated PASS, 898 post-install maintained PASS, no website write/DB migration/M99 allocation/live publish/commit/push by installer. След това Job #27 за Palltex BWOLF DAYTONA, supplier ref 042502, получи permanent canonical identity `M99 100018`. Controlled CREATE към m99.eu създаде Product 2041 в Test category 26, active=0, available_for_order=0, visibility=none, price 30.20 за пилота, languages EN/BG/RU, strict API truth PASS. Това доказва CREATE contract, но Product 2041 не е production-ready и не трябва да се активира: липсват image, BWOLF channel mapping, real combinations; content/SEO са mixed/weak; 0% tax rule не е валидиран.

---
## 19. Следваща линия R7K.4

R7K.4 трябва да бъде `Complete Product Payload + Automated Category Pipeline + Supplier Price Monitoring + Dynamic Channel Pricing + VAT + Quality Readback MAXSIM`. Целта не е още един product-specific pilot, а production-scale engine: complete payload, image/brand/combinations, natural multilingual content, SEO quality, daily supplier price monitoring, random 1.00%-1.70% undercut pricing, VAT resolution, explicit multi-channel selection, AUTO_READY/NEEDS_REVIEW/BLOCKED exception engine, batch write/readback и operator batch report. Product 2041 се използва за controlled UPDATE proof; UPDATE никога не трябва silently да стане CREATE.

---
## 20. Исторически safety registry

Product 2038 / legacy `M99-1`: ambiguous historical R7D attempt; do not republish. Product 2039 / `M99-2`: exact duplicate; do not republish. Product 2040 / `M99-20260913150352758`: technical publisher proof only; do not activate without explicit decision. Product 2041 / `M99 100018`: first real Palltex canonical CREATE, permanently tied to that identity; do not re-CREATE it and do not activate until Complete Product Quality PASS.

---
## 21. Open / deferred

Still open/deferred unless later resolved: universal ProductGroup-vs-colour boundary; universal Variant SKU standard; exact production Dolibarr parent/variant and stock-decrease deployment; image-rights policy; production Vault; exact WordPress adapters; 2FA timing; observation freshness thresholds; preferred-supplier/purchasing algorithm; full Palltex colour-family traversal/per-colour images; production LLM integration; final governed Git checkpoint for post-ac3005e work. These open items do not override fixed decisions.

---
## 22. Current channel matrix

| Target | Type | Platform | Languages | Rule / note |
|---|---|---|---|---|
| `mela99.com` | web | ThirtyBees / PrestaShop 1.7 family | BG, EN | Primary Bulgarian e-commerce channel; historical hidden TEST/review workflow. |
| `rabotni-drehi.com` | web | WordPress | BG | Bulgarian workwear channel; channel-specific content. |
| `m99.eu` | web | PrestaShop 9.1.5 | EN, BG, RU | Proven classic /api GET/POST; Test category 26; controlled live acceptance Product 2041. |
| `medicinski-drehi.com` | web | e-commerce channel | BG, EN, RU | Medical clothing operational channel. |
| `laviro.ro` | web | PrestaShop 1.6.1.24 | RO, EN | Romanian market channel. |
| `alviro.ro` | web | Romanian e-commerce channel | RO, EN | Romanian market channel. |
| `toplinka.com` | web/services | service channel | BG | Heating / photovoltaic services; included in configured channel scope. |
| `Dolibarr` | erp | ERP / CRM / warehouse | BG, EN | Operational destination, not a web shop and not canonical identity owner. |

---

## 23. Consolidated Decision Registry

- **GOV-001** [DECIDED] (governance) — M99 is the Single Source of Truth for canonical identity and verified knowledge.
- **GOV-002** [DECIDED] (governance) — Knowledge First: verified knowledge precedes content, publishing and downstream automation.
- **GOV-003** [DECIDED] (governance) — AI Native, not AI Invented: AI must not invent technical or commercial facts.
- **GOV-004** [DECIDED] (governance) — Before new architecture proposals, consult Decision Registry, Current Context, Project State, latest README, relevant ADR and tests/history.
- **GOV-005** [DECIDED] (governance) — A failed implementation attempt does not reopen a DECIDED rule.
- **GOV-006** [DECIDED] (governance) — README remains the master human-readable constitution and machine-readable governance files are mandatory project memory.
- **CORE-001** [DECIDED] (core) — No Duplicate Data: reusable canonical facts/entities are stored once and mapped, not duplicated per channel.
- **CORE-002** [DECIDED] (core) — Historical observations are preserved.
- **CORE-003** [DECIDED] (core) — Market and Channel are separate concepts.
- **CORE-004** [DECIDED] (core) — Removing a product from a channel must not destroy accumulated M99 knowledge.
- **EVID-001** [DECIDED] (evidence) — Important facts preserve provenance including source, observation/verification time and conflict/reviewer context where available.
- **EVID-002** [DECIDED] (evidence) — Evidence priority is exact manufacturer, official documentation/certificates, validated B2B, exact supplier, verified internal data, operator, then AI over verified data.
- **EVID-003** [DECIDED] (evidence) — Observation is evidence and does not automatically become canonical truth.
- **UX-001** [DECIDED] (operator_ux) — Operator-first UX.
- **UX-002** [DECIDED] (operator_ux) — One-decision-per-screen is the target operator UX.
- **UX-003** [DECIDED] (operator_ux) — Operators must not need Python, PowerShell, API, HTTP, JSON, XML, SQL, credentials or platform internals.
- **UX-004** [DECIDED] (operator_ux) — The primary operator workflow is generalized Add Products, not a dedicated Add to m99.eu screen.
- **UX-005** [DECIDED] (operator_ux) — Primary Supplier selection UX must not require URL copy/paste or BAT/Python scripts.
- **ID-001** [DECIDED_TESTED] (identity) — M99 canonical identity is independent from external IDs.
- **ID-002** [SUPERSEDED] (identity) — Historical rule: M99- followed by digits only. Superseded for new allocations by ID-006; retained only for compatibility/history.
- **ID-003** [DECIDED] (identity) — Assigned M99 identity is never reused for another ProductGroup.
- **ID-004** [DECIDED] (identity) — Identity Before Content.
- **ID-005** [DECIDED] (identity) — Identity resolution states are NEW, EXISTING, AMBIGUOUS and UNRESOLVED; AMBIGUOUS requires human decision.
- **PG-001** [DECIDED] (product_group) — ProductGroup lifecycle is draft -> active -> paused -> retired.
- **PG-002** [DECIDED] (product_group) — Hard DELETE requires explicit human approval and typed DELETE confirmation.
- **ORG-001** [DECIDED] (organization) — Supplier and Manufacturer are Organization roles; one Organization may hold both roles.
- **ORG-002** [DECIDED] (organization) — New Supplier, Manufacturer and Brand proposals require Super Admin approval before general operator availability.
- **ORG-003** [DECIDED] (organization) — A canonical product may have multiple verified supplier/manufacturer mappings.
- **BRAND-001** [DECIDED] (brand) — Brand is a separate canonical object linked to owner/manufacturer organizations and official sources.
- **B2B-001** [DECIDED] (b2b) — B2B portals belong to Organizations and declare connector capabilities.
- **SRC-001** [DECIDED] (supplier_source) — An Organization may have multiple SupplierSources such as public website, B2B, API, feeds, catalogues, price lists and stock feeds.
- **SRC-002** [DECIDED] (supplier_source) — SupplierSources declare explicit capabilities including identity, technical facts, images, price, availability, variants and stock where supported.
- **SRC-003** [DECIDED] (supplier_source) — The running M99 runtime may use controlled read-only live SupplierSource access; SAFE installers do not crawl suppliers automatically.
- **SRC-004** [DECIDED] (supplier_source) — Supplier-specific adapters implement one common Live Supplier Connector contract so the operator UI remains supplier-independent.
- **IMP-001** [DECIDED] (import) — Direct Supplier Selection is the target UX.
- **IMP-002** [DECIDED] (import) — Selection supports one or many products, one or many categories, and all products where the source supports it.
- **IMP-003** [DECIDED] (import) — Every new-product import is an auditable ImportJob.
- **IMP-004** [DECIDED] (import) — WRITE_TARGETS = REQUESTED intersect AUTHORIZED intersect READY.
- **IMP-005** [DECIDED] (import) — Import presets simplify workflows but never grant permissions not already held by the user.
- **CH-001** [DECIDED] (channels) — Operators may choose one or more authorized target channels/ERP destinations for NEW PRODUCT IMPORT.
- **CH-002** [DECIDED] (channels) — m99.eu is one target channel, not the central Add Product workflow.
- **CH-003** [DECIDED] (channels) — NOT_SELECTED and BLOCKED are distinct target states.
- **PUB-001** [DECIDED] (publishing) — New products publish TEST/Draft first.
- **PUB-002** [DECIDED] (publishing) — TEST category is resolved live.
- **PUB-003** [DECIDED] (publishing) — Final category is operator-owned.
- **PUB-004** [DECIDED] (publishing) — CREATE and UPDATE are separate contracts.
- **PUB-005** [DECIDED] (publishing) — Duplicate guard runs before CREATE.
- **PUB-006** [DECIDED] (publishing) — Readback is mandatory after write.
- **PUB-007** [DECIDED] (publishing) — HTTP 200/201 does not equal Product Quality PASS.
- **PUB-008** [DECIDED] (publishing) — Activation requires authorization.
- **PUB-009** [DECIDED] (publishing) — Front Office verification is required where applicable after channel writes.
- **CNT-001** [DECIDED] (content) — Content is channel/market/language aware and based on verified facts.
- **CNT-002** [DECIDED] (content) — Every required content field is reviewed per language; Image and ALT are reviewed together.
- **CNT-003** [DECIDED] (content) — Supplier prose is not copied verbatim; prose/SEO is adapted per channel and language.
- **LANG-001** [DECIDED] (language) — Language Registry is dynamic and channel language IDs are discovered live rather than assumed.
- **IMG-001** [DECIDED] (images) — Image source priority is official manufacturer, then verified supplier; another M99 channel is not the master image source by default.
- **IMG-002** [DECIDED] (images) — Image pipeline is discover -> verify -> download -> relevance -> dedupe -> resize -> WebP -> localized ALT -> operator review -> upload -> readback.
- **VAR-001** [DECIDED] (variants) — A variational product must have exactly one default combination.
- **VAR-002** [DECIDED] (variants) — Visible size is not stock.
- **VAR-003** [DECIDED] (variants) — Dolibarr/M99 stock is variant-aware.
- **PRC-001** [DECIDED] (pricing) — Target selling price is gross VAT-included customer price.
- **PRC-002** [DECIDED] (pricing) — VAT is channel/market configuration and is not a universal hardcoded constant.
- **PRC-003** [DECIDED] (pricing) — Supplier price changes flow through approved pricing rule, currency, VAT, target gross, platform representation, write, readback and Front Office verification.
- **SYNC-001** [DECIDED] (sync) — Existing products sync daily and NO_CHANGE means NO_WRITE.
- **SYNC-002** [DECIDED] (sync) — Daily Existing Product Sync is separate from New Product Import and is not controlled by new-product target selection.
- **SYNC-003** [DECIDED] (sync) — Daily Sync operates on canonical products with verified supplier/source mappings.
- **SYNC-004** [DECIDED] (sync) — Daily Sync checks price, availability, variants/sizes, product changes and discontinuation.
- **SYNC-005** [DECIDED] (sync) — Daily Sync updates only already-existing allowed channel/ERP mappings and never auto-creates a missing channel product.
- **SYNC-006** [DECIDED] (sync) — Daily Sync change states include NO_CHANGE, PRICE_CHANGED, AVAILABILITY_CHANGED, VARIANT_AVAILABILITY_CHANGED, PRODUCT_CHANGED, SUPPLIER_DISCONTINUED and VERIFICATION_FAILED.
- **SYNC-007** [DECIDED] (sync) — VERIFICATION_FAILED is not interpreted as zero stock or OUT_OF_STOCK; last verified observation is preserved.
- **SYNC-008** [DECIDED] (sync) — Daily Sync must expose business metrics including checked products, changes, writes, NO_CHANGE, blocked and errors.
- **OBS-001** [DECIDED] (observation) — Supplier observations preserve source/product/variant mapping, timestamps, price/currency, availability, changed fields and verification/provenance state.
- **OBS-002** [DECIDED] (observation) — Historical supplier observations are retained to explain commercial changes over time.
- **PRES-001** [DECIDED] (product_presence) — Presence is not Stock.
- **PRES-002** [DECIDED] (product_presence) — M99 provides bidirectional Product Presence reporting: Product -> Channels and Channel -> Products, including missing mappings.
- **PRES-003** [DECIDED] (product_presence) — Presence states include NOT_PRESENT, PRESENT_DRAFT, PRESENT_TEST, PRESENT_ACTIVE, PRESENT_PAUSED, PRESENT_RETIRED, PRESENT_LAST_VERIFIED, UNKNOWN and VERIFICATION_FAILED.
- **PRES-004** [DECIDED] (product_presence) — Product Presence stores external IDs, publication state, price, last verification/sync and errors where available.
- **ERP-001** [DECIDED] (erp) — M99 owns canonical identity/knowledge; Dolibarr is the operational ERP/CRM/warehouse representation.
- **ERP-002** [DECIDED] (erp) — M99-owned physical stock increases through supplier reception and decreases through customer shipment.
- **ERP-003** [DECIDED] (erp) — Dolibarr uses a distinct target adapter/payload and is not treated as another website.
- **WH-001** [DECIDED] (warehouse) — Approved Supplier/Manufacturer Organizations may have linked EXTERNAL availability warehouses in Dolibarr named after the organization.
- **WH-002** [DECIDED] (warehouse) — Warehouse ownership/type distinguishes M99_PHYSICAL, SUPPLIER_EXTERNAL and MANUFACTURER_EXTERNAL.
- **WH-003** [DECIDED] (warehouse) — Supplier/manufacturer external warehouse availability is never interpreted automatically as M99-owned physical stock.
- **WH-004** [DECIDED] (warehouse) — External warehouse availability is variant-aware where reliable source data is variant-level.
- **WH-005** [DECIDED] (warehouse) — Numeric external warehouse quantity is written only when the source provides a reliable exact quantity; status-only availability never receives invented numeric stock.
- **WH-006** [DECIDED] (warehouse) — Supplier availability states may represent exact quantity, in stock, low stock, out of stock, on request, unknown or verification failed without fabricating quantities.
- **REV-001** [DECIDED] (revision) — Existing Product Content Revision is a separate operational class from New Product Import and Daily Sync.
- **REV-002** [DECIDED] (revision) — Existing approved Product Name and URL/slug are normally locked during content revision.
- **REV-003** [DECIDED] (revision) — Existing Category Name, URL/slug and structural identity fields are normally locked during content revision.
- **REV-004** [DECIDED] (revision) — Product and Category content may be revised without reopening structural identity by default.
- **QG-001** [DECIDED] (quality) — A numeric quality score can never override a failed critical Product Quality Gate.
- **SEC-001** [DECIDED] (security) — Operators never see channel/B2B credentials and secrets are never committed to Git, logged or exposed in screenshots.
- **SEC-002** [DECIDED] (security) — Permissions are enforced server-side, not only by menu visibility.
- **SEC-003** [DECIDED] (security) — Authentication direction includes secure password hashing, session management, timeout, failed-login protection, reset workflow and login/logout audit.
- **AUDIT-001** [DECIDED] (audit) — Central Super Admin logs include Audit, System, Supplier/B2B & Channel Integration and Security logs.
- **AUDIT-002** [DECIDED] (audit) — Minimum operational log context includes timestamp, severity, user, module, operation, entity, supplier/channel, job_id, result, message and correlation_id.
- **MIG-001** [DECIDED] (migration) — MoneyWork and legacy sites are reconciliation sources, not canonical masters.
- **MIG-002** [DECIDED] (migration) — Preferred migration flow is Inspect -> Normalize -> Deduplicate -> Identity Map -> Supplier/Customer Map -> Dry Run -> Import -> Reconcile -> Audit.
- **CRM-001** [DECIDED] (crm) — CRM foundation flow is First call -> Offer -> Second call.
- **OPS-001** [DECIDED] (operations) — Operational classes remain distinct: New Product Import, Existing Product Daily Sync, Manual/Exceptional Repair, Existing Product Content Revision, Existing Category Content Revision and Knowledge/Evidence Acquisition.
- **DEV-001** [DECIDED_TESTED] (development) — SAFE development uses clean baseline, controlled patch, compile, dedicated tests, full regression, exact scope review, explicit COMMIT and no automatic Push.
- **ID-006** [DECIDED_TESTED] (identity) — Normative new M99 Reference format is literal "M99 " followed by exactly six digits. Historical hyphenated references remain compatibility-only and are never newly allocated.
- **ID-007** [DECIDED_TESTED] (identity) — Canonical allocation preserves the historical reserved floor through M99 100017; the first new live canonical allocation is M99 100018 and assigned identities are never reused.
- **MFG-001** [DECIDED_TESTED] (manufacturer_evidence) — Supplier and Manufacturer remain separate semantic roles even when Supplier Reference and Manufacturer MPN have the same character value.
- **MFG-002** [DECIDED_TESTED] (manufacturer_evidence) — Durable Manufacturer evidence may be reused across jobs only by exact governed evidence scope (supplier reference + target + exact product URL/checksum context); no fuzzy or brand-wide inference.
- **CNT-004** [DECIDED_TESTED] (content) — Publish-facing content is rebuilt from checksum-verified durable evidence with the current content generator; stale stored prose must not silently bypass the current content gate.
- **CNT-005** [DECIDED] (content) — Customer-facing content must not expose internal M99 governance/evidence/debug wording; each channel language must be natural and language-pure.
- **SEO-001** [DECIDED] (seo) — Benchmark framework: Amazon/Zalando/eBay for hierarchy, scanability, variants, images, specifications and buying information; Apple for clarity, hierarchy, concise benefits and low-noise presentation; exact manufacturer sources for factual truth; Stenso/Palltex and relevant local competitors for market terminology and positioning without copying prose.
- **SEO-002** [DECIDED] (seo) — Search benchmark is dynamic by country/language/query; there is no permanent hardcoded SEO winner.
- **PRC-004** [DECIDED] (pricing) — For M99 web channels, the target customer GROSS price is lower than the verified benchmark supplier GROSS price by a randomly generated percentage from 1.00% through 1.70%.
- **PRC-005** [DECIDED] (pricing) — The random undercut factor is generated for initial pricing and when a verified supplier benchmark price changes; NO_CHANGE means no price rewrite and no gratuitous re-randomization.
- **PRC-006** [DECIDED] (pricing) — Supplier benchmark price is observed daily from the highest-priority verified commercial source: validated B2B when available, otherwise exact supplier product page. Source/category/search/competitor pages are not accepted as commercial price evidence.
- **PRC-007** [DECIDED] (pricing) — Price change pipeline is SupplierObservation -> verified change detection -> M99 pricing rule -> market currency -> channel VAT -> target GROSS -> platform representation -> write -> API readback -> Front Office gross verification. Out-of-policy anomalies go to NEEDS_REVIEW.
- **AUTO-001** [DECIDED] (automation) — Human by exception, not by repetition: repeatable decisions covered by approved rules are automated; humans handle policy approval, exceptions, conflicts, destructive actions and high-risk anomalies.
- **AUTO-002** [DECIDED] (automation) — Category/multi-product processing must not require product-by-product typed confirmations. Products are machine-classified as AUTO_READY, NEEDS_REVIEW or BLOCKED; batch confirmation applies to the ready set while exceptions are reviewed separately.
- **AUTO-003** [DECIDED] (automation) — Automation is fail-closed: any failed critical gate blocks that product/target without blocking unrelated AUTO_READY items unless the failure is systemic.
- **CH-004** [DECIDED] (channels) — Every NEW PRODUCT ImportJob provides explicit multi-select target choice across all configured authorized channels; no channel is silently selected by default.
- **CH-005** [DECIDED] (channels) — Current selectable web-channel scope is mela99.com, rabotni-drehi.com, m99.eu, medicinski-drehi.com, laviro.ro, alviro.ro and toplinka.com; Dolibarr is a separate ERP/CRM/warehouse destination when the workflow permits it.
- **BATCH-001** [DECIDED] (batch_publish) — Category publishing uses one generalized engine for one product, many products, one/many categories, first N, only-new-to-M99 or all selected products; no per-product custom code.
- **BATCH-002** [DECIDED] (batch_publish) — Batch quality report must aggregate target readiness, successful writes/readbacks and exception reasons so the operator works on exceptions rather than repetitive confirmations.
- **LIVE-001** [LIVE_ACCEPTED] (live_acceptance) — First real Palltex canonical CREATE pilot: Product 2041 / M99 100018 on m99.eu, hidden/offline/non-orderable in Test category 26, strict API truth verified. It proves CREATE plumbing but is not production-ready and must not be activated yet.
- **LIVE-002** [DECIDED] (live_acceptance) — Product 2041 quality blockers before production acceptance: no product image, no BWOLF channel brand/manufacturer mapping, no real combinations, mixed-language/customer-internal content, weak SEO lengths/slug, and unvalidated 0% tax rule.

---

## 24. Resume marker

`M99_RESUME_V15_R7K4_2026-09-14`

Resume by reading README v15 + machine memory v15, then actual working-tree diff/tests before implementation. Do not treat docs as proof that code is implemented.



---

# АРХИВНО ПРИЛОЖЕНИЕ — v16 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — README v16

**Checkpoint date:** 2026-09-21  
**Architecture target:** R7.3.0 — Unified Multi-Channel Publishing  
**Document role:** Consolidated history + current constitution + approved replaceable channel baseline  
**Previous master:** README v15 (2026-09-14), preserved as historical checkpoint.

> `DECIDED != IMPLEMENTED`. Current platform/version values are a replaceable baseline, not permanent channel identity.


## 1. Началната идея и причината да съществува M99 Knowledge

M99 Knowledge започна като идея за централен M99 Knowledge Base и M99 Style Guide за M99 Group. Първоначалната практическа цел беше една проверена продуктова база да захранва автоматично SEO заглавия, Meta Description, H1, кратки и дълги описания, FAQ, ALT текстове, блог съдържание и преводи на български, английски и румънски, а по-късно и други езици.

Проблемът, който системата решава, е повторното ръчно поддържане на една и съща продуктова информация в много магазини, различни CMS/ERP системи и пазари. От тази начална идея платформата се разви до централен knowledge и control layer: Supplier/Manufacturer evidence → canonical identity → content/SEO → images → variants → pricing/VAT → multi-channel publishing → readback → Dolibarr → orders → warehouse → couriers → audit.

Основната бизнес цел остава минимален административен headcount, максимално безопасна автоматизация, международно развитие и подкрепа на M99 Group Master Plan 2036. Операторът е бизнес потребител, а не програмист; нормалната работа не трябва да изисква Python, PowerShell, SQL, XML/JSON или ръчно изпълнение на API заявки.

## 2. Основни принципи

Нормативните принципи са: Knowledge First; Evidence Based; No Duplicate Data; Identity Before Content; AI Native, not AI Invented; Supplier != Manufacturer; Supplier Reference != Manufacturer MPN; CREATE != UPDATE; API success != business acceptance; Human by exception, not by repetition.

M99 Knowledge е master за canonical identity, verified product knowledge, provenance, policies и orchestration. Каналите са destinations. Dolibarr е ERP/CRM/warehouse execution layer, а не product knowledge master. Supplier observation е evidence и не става автоматично canonical truth. Supplier availability не е M99 physical stock.

## 3. Canonical identity и Product lifecycle

M99 identity е независима от supplier SKU/reference, Manufacturer MPN, EAN/GTIN, MoneyWorks code, Dolibarr ID, channel product ID, title и URL. Нормативният формат за нови идентификатори е „M99 “ + точно шест цифри. Старите hyphenated references остават само за compatibility/history и не се използват за нови allocations.

ProductGroup lifecycle е draft → active → paused → retired. Hard DELETE остава изключение и изисква operator approval, ръчно DELETE и audit. Identity се решава преди content. Състоянията за identity resolution са NEW, EXISTING, AMBIGUOUS и UNRESOLVED.

## 4. Supplier, Manufacturer, Brand и Evidence

Supplier и Manufacturer са отделни semantic roles, дори когато една организация изпълнява и двете. Supplier Reference и Manufacturer MPN са различни полета, дори когато текстовата им стойност съвпада. Brand е отделен canonical object.

Supplier evidence носи commercial truth: supplier reference, public/B2B price, availability и supplier variants. Manufacturer evidence носи factual truth: MPN, materials, standards, technologies, technical specifications и official images. Evidence пази provenance, exact source/resource, observed/verified time и governed scope. Durable evidence може да се reuse-ва само при exact governed match; fuzzy или brand-wide inference не е достатъчно за critical facts.

## 5. Content, SEO/AEO/GEO, изображения и варианти

Content Engine работи върху verified Product Knowledge. Supplier prose не се копира verbatim. Facts могат да са общи, но prose, SEO и localization са channel/market/language specific. AI не измисля standards, materials, certifications или stock. Customer-facing content не показва internal governance/evidence/debug текст.

Benchmark framework използва Amazon/Zalando/eBay за hierarchy, scanability, variants, images, specifications и buying information; Apple за clarity и low-noise presentation; exact manufacturer source за factual truth; supplier/local competitors за terminology, positioning и content gaps без копиране.

Image priority: official manufacturer → verified supplier → verified cached original. Pipeline: Discover → Verify → Download → Relevance → Dedupe → resize около 1200–1400 px → WebP → localized ALT → review → Upload → Association → Readback. При variational product трябва да има точно една default combination. Visible size != stock.

## 6. Pricing и VAT

M99 target selling price е customer-facing GROSS/VAT-included. Одобреното business правило е verified supplier benchmark GROSS минус случайно генериран процент между 1.00% и 1.70%. Процентът се създава при initial pricing и при verified supplier benchmark price change. Ако benchmark не се е променил: NO_CHANGE → NO_WRITE и няма gratuitous re-randomization.

Commercial source priority е validated B2B connector, когато е наличен, иначе exact supplier product page. VAT е channel/market configuration и не се hardcode-ва глобално. Pipeline: SupplierObservation → verified change → pricing rule → currency/FX → VAT → target GROSS → platform NET/API representation → write → readback → Front Office gross verification. Exact production rounding policy остава отворено governed решение.

## 7. Историческо развитие на платформата

Проектът премина през M99 Knowledge Base / Style Guide, canonical Product ↔ ProductGroup ↔ Channel модел, Dolibarr и MoneyWorks migration planning, безопасни Windows installers и все по-строги release gates.

v0.7.1 Rev7 достигна 234 tests PASS и checkpoint commit 8c3d2d7fc729f22001c320d1fa033528272eb21e. v0.7.2 Phase 1 създаде Canonical Data Model Foundation, а Phase 2 — SQLAlchemy + Alembic migration baseline. Phase 2.5 започна PrestaShop 9 integration за m99.eu и разкри import-path/runtime проблеми, които доведоха до последващи revisions.

Phase 4.6 / R7K разви Palltex/BWolf controlled publishing, durable manufacturer evidence, M99 identity gate и content gate. R7.2.5/R7.2.6 доказаха live GET structural truth за m99.eu Product 2041 / M99 100018. R7.2.7 остана controlled dry-run. R7.2.8 Windows precheck завърши с 1050 tests PASS и NO WRITE, като production blockers останаха. Решението е да не продължаваме product-specific R7.2.x линия, а да преминем към generalized R7.3.0.

## 8. R7.3.0 — Unified Multi-Channel Publishing

R7.3.0 превръща M99 Knowledge в общ publishing/orchestration engine. Операторът избира един, няколко или всички разрешени destinations. WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY. NOT_SELECTED != BLOCKED. CREATE и UPDATE са отделни contracts. Duplicate guard работи преди CREATE. Readback е задължителен след write. Activation изисква authorization.

Batch engine класифицира продукт/target като AUTO_READY, NEEDS_REVIEW или BLOCKED. Операторът одобрява ready set и работи само по exceptions, conflicts, destructive actions и high-risk anomalies.

## 9. Одобрена техническа матрица — Baseline 2026-09-21

| Channel ID | Destination | Platform | Version / Theme | R7.3.0 scope |
|---|---|---|---|---|
| M99EU | m99.eu | PrestaShop | 9.1.5 | Publish + Orders |
| MELA99 | mela99.com | thirty bees | 1.7.0 | Publish + Orders |
| MEDICAL | medicinski-drehi.com | PrestaShop | 1.7.8.11 | Publish + Orders |
| WORKWEAR | rabotni-drehi.com | WordPress / WooCommerce | WordPress 7.0.5 / Enfold | Publish + Orders |
| LAVIRO | laviro.ro | PrestaShop | 1.6.1.24 | Publish + Orders |
| ALVIRO | alviro.ro | thirty bees | 1.1.0–1.1.x | Publish + Orders |
| TOPLINKA | toplinka.com | WordPress / WooCommerce | WordPress 7.1 / Enfold Child | Publish + Orders; separate acceptance |
| DOLIBARR | Dolibarr | Dolibarr ERP/CRM | 20.0.2 | Products + Orders + Stock + Fulfillment |


## 9. Replaceable platform/version architecture

Одобрената channel matrix е baseline, а не вечна конфигурация. Channel ID е стабилна бизнес идентичност. Platform, platform_version и active_adapter са versioned и replaceable configuration.

При upgrade или migration каналът запазва channel_id. Старият technical profile остава в history с effective dates, reason, approval и compatibility/acceptance evidence. Това позволява например един сайт да премине от thirty bees към PrestaShop, WooCommerce или бъдеща платформа, без да се променя canonical channel identity.

Нормативната архитектура е: M99 Knowledge Core → extensible Channel/Integration Registry → versioned adapters → N channels + N business integrations. Core не зависи от конкретен CMS, версия, ERP или courier.

## 10. Adapter contract и capabilities

Не се приема автоматично feature parity между различни платформи и версии. Всеки adapter декларира capabilities: product read/create/update, variants, images, brands/manufacturers, categories, stock, orders, order status update, tracking writeback, languages, currencies, tax rules, readback и Front Office verification.

R7.3.0 трябва да поддържа version-aware profiles за PrestaShop 9, PrestaShop 1.7, legacy PrestaShop 1.6, thirty bees, WooCommerce и Dolibarr. Нови adapters трябва да могат да се добавят без rewrite на M99 Core.

## 11. Order Hub и Dolibarr

M99 Order Hub трябва да сваля поръчки от всички разрешени магазини по global selected status или по отделен status за всеки channel. Различните platform statuses се map-ват към canonical M99 statuses. External orders се normalize-ват и deduplicate-ват преди създаване на Dolibarr Sales Order.

Flow: Store → Order Adapter/API → M99 Knowledge → normalize/dedupe → Dolibarr → warehouse/fulfillment → courier.

За поръчката се пазят source channel, original order ID, internal M99 order ID, customer, billing/shipping, phone/email, lines, M99/SKU references, quantities, prices, VAT, discounts, shipping, currency, payment, COD, status и timestamps. Exception queue включва missing phone, unknown product, price mismatch, missing address, unknown courier office/locker, duplicate и API errors.

## 12. Courier Registry

Първите courier adapters са Speedy, Econt и Sameday. Courier Registry е extensible; couriers могат да се enable/disable и да се добавят нови.

Target automation: CONFIRMED → Dolibarr validation → READY_FOR_SHIPMENT → selected/automatic courier → AWB → label/tracking/shipping cost/COD/status → Dolibarr → source store, когато adapter-ът поддържа writeback.

Auto-AWB се разрешава само след controlled acceptance на address, office/locker, phone, COD, weight, package count, payer и service type mappings.

## 13. Product 2041 safety marker

Product 2041 / M99 100018 е hidden/inactive/non-orderable m99.eu pilot. Той доказва identity binding, API truth/readback и fail-closed behavior, но не е complete production product proof. Не трябва да се re-CREATE-ва и не трябва да се активира без complete quality pass.

## 14. Release engineering и операторски UX

Преди Windows delivery се правят максимални static/package audits, AST/compile, path validation, hashes, mocked success/failure, regression, secrets/no-write audit и exact release scope. Windows/CMD е final environment acceptance, не първо debugging място. Не се използва blind Commit All; няма force/reset/clean/automatic rebase.

Нормалният operator UI за destinations включва m99.eu, mela99.com, medicinski-drehi.com, rabotni-drehi.com, laviro.ro, alviro.ro, toplinka.com, Dolibarr и Select all. Toplinka присъства в Registry/UI, но има отделен acceptance profile.

## 15. Нови решения на checkpoint v16

CH-006 — Channel identity е независима от platform/version.
CH-007 — Platform/version/adapter са replaceable, versioned configuration с retained history.
CH-008 — Нови channels/integrations се добавят чрез registries/adapters без core rewrite.
ADP-001 — Adapters декларират capabilities; feature parity не се предполага.
ORD-001 — Order Hub normalize-ва и deduplicate-ва поръчки от всички configured channels.
ORD-002 — Order status selection може да бъде global или per-channel с canonical mapping.
ERP-004 — Dolibarr 20.0.2 е текущият replaceable/versioned ERP baseline.
CUR-001 — Courier Registry започва със Speedy/Econt/Sameday и остава extensible.
CUR-002 — Auto-AWB се разрешава само след controlled acceptance gates.
BASE-20260921 — Channel/platform matrix е operator-approved baseline и може да бъде versioned/replaced в бъдеще.

## 16. Resume marker

M99_RESUME_V16_R730_UNIFIED_MULTICHANNEL_2026-09-21

При възобновяване се четат README v16 + machine registry/history v16 + actual working-tree diff/tests. Документацията е governance/architecture evidence и не е доказателство, че описаната функционалност вече е implemented.



---

# АРХИВНО ПРИЛОЖЕНИЕ — v18 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — README v18

**Checkpoint date:** 2026-09-26  
**Role:** Full Bulgarian resume/governance checkpoint  
**Previous normative verification rule:** README v17  
**Status:** DOCUMENTATION CHECKPOINT — actual Git state must be verified before commit/push


## 1. Предназначение на този checkpoint

Този комплект е пълният описателен checkpoint на M99 Knowledge Platform към 26.09.2026 г. Целта му е след рестарт на компютъра или нов разговор работата да продължи от същото място без повторно изясняване на архитектура, бизнес правила, safety gates, продуктова идентичност, каналите, ценовата политика и release процеса.

Документацията е governance и resume evidence. Тя не превръща автоматично решение в имплементирана функционалност. Основното правило остава DECIDED != IMPLEMENTED. За текущата реална истина винаги се проверяват Git branch/HEAD, working tree, тестовете и readback от съответната система.


## 2. Бизнес цел и роля на платформата

M99 Knowledge Platform е централният knowledge и control layer за M99 Group. Платформата трябва да намалява ръчната работа, да позволява минимален административен екип и да обслужва M99 Group Master Plan 2036. Дългосрочната бизнес цел е устойчив международен бизнес и около 10 000 EUR чист месечен доход за собственика.

Нормалният оператор е бизнес потребител, а не програмист. Ежедневната работа трябва постепенно да се премести в browser Control Center. CMD/PowerShell остават за bootstrap, recovery, diagnostics и controlled release acceptance, а не за нормално управление на продукти.


## 3. Основни принципи

Knowledge First; Evidence Based; No Duplicate Data; Identity Before Content; AI Native, not AI Invented; Supplier != Manufacturer; Supplier Reference != Manufacturer MPN; CREATE != UPDATE; API success != business acceptance; Human by exception, not by repetition.

M99 Knowledge е master за canonical identity, verified product knowledge, provenance, policies и orchestration. Каналите са destinations. Dolibarr е ERP/CRM/warehouse execution layer, а не product knowledge master. Supplier availability не е M99 physical stock.


## 4. Canonical identity и lifecycle

Новият M99 идентификатор е „M99 “ + точно шест цифри. Резервираните идентификатори стигат до M99 100018; следващият нов allocation трябва да бъде >= M99 100019. Старите hyphenated references остават само за compatibility/history.

ProductGroup lifecycle е draft → active → paused → retired. Hard DELETE е изключение: operator approval + ръчно изписване DELETE + audit. M99-1 и M99-2 са protected. Product 2040 е technical pilot и не трябва да се активира.

Identity resolution има NEW, EXISTING, AMBIGUOUS и UNRESOLVED. UPDATE никога не преминава тихо към CREATE. Duplicate guard се изпълнява преди CREATE.


## 5. Supplier, Manufacturer, Brand и evidence

Supplier, Manufacturer и Brand са различни semantic roles. За Palltex: Palltex е supplier и manufacturer, а BWolf е brand. Supplier reference и Manufacturer MPN са отделни полета дори когато стойността им съвпада.

Supplier evidence носи commercial truth: supplier reference, price, availability, supplier variants. Manufacturer evidence носи factual truth: MPN, materials, standards, technologies, specifications и official images. Critical facts не се извеждат чрез fuzzy/brand-wide inference.


## 6. Content, SEO/AEO/GEO и localization

Съдържанието се генерира върху verified Product Knowledge. Supplier prose не се копира дословно. Facts могат да са общи, но prose, SEO и localization са channel/market/language specific. AI не измисля standards, materials, certifications, technologies или stock.

Целевите езици са BG/EN и при румънските канали RO. Желаните outputs включват SEO title, meta description, H1, кратко/дълго описание, FAQ, ALT texts, tags/keywords, technical specifications, EN norms и преводи. Качеството трябва да е сравнимо с добрите практики на Amazon/Zalando/eBay за scanability и Apple за clarity/low-noise presentation.


## 7. Images и variants

Image priority: official manufacturer → verified supplier → verified cached original. Pipeline: Discover → Verify → Download → Relevance → Dedupe → resize около 1200–1400 px → WebP → localized ALT → review → Upload → Association → Readback.

При variant product трябва да има точно една default combination и cache_default_attribute да сочи към нея. Visible size не означава stock. Не се измислят child combination references. Безопасният минимален combination payload съдържа product binding, price impact 0, minimal quantity 1, default_on и нужната association.


## 8. Pricing и VAT

Нормативният pricing target е customer-facing GROSS/VAT-included. Verified supplier benchmark GROSS се намалява със случайно генериран процент между 1.00% и 1.70%. Процентът се създава при initial pricing и при verified supplier benchmark price change; при NO_CHANGE има NO_WRITE и няма gratuitous re-randomization.

VAT е channel/market configuration и не се hardcode-ва глобално. Pipeline: SupplierObservation → verified change → pricing rule → currency/FX → VAT → target GROSS → platform NET/API representation → write → readback → Front Office gross verification. Exact production rounding остава governed decision, ако не е имплементирано и доказано.

За Palltex Daytona / Product 2041 е наблюдаван supplier price 30.99 gross. Не трябва просто да се запази m99.eu net 30.20 и да се добави 20% VAT, защото това би нарушило ценовото правило. Ако persisted discount/VAT state не може да се докаже, системата трябва да fail-close, а не да измисля стойност.


## 9. Канали и техническа матрица

Текущата replaceable baseline матрица е: m99.eu — PrestaShop 9.1.5; mela99.com — thirty bees 1.7.0; medicinski-drehi.com — PrestaShop 1.7.8.11; rabotni-drehi.com — WordPress/WooCommerce, WordPress 7.0.5 / Enfold; laviro.ro — PrestaShop 1.6.1.24; alviro.ro — thirty bees 1.1.0–1.1.x; toplinka.com — WordPress/WooCommerce, WordPress 7.1 / Enfold Child; Dolibarr — 20.0.2.

Channel identity е постоянна бизнес идентичност. Platform/version/adapter са versioned replaceable configuration. Нови channels/integrations трябва да се добавят чрез registries/adapters без core rewrite. Feature parity не се предполага; всеки adapter декларира capabilities.


## 10. Multi-channel publishing

Операторът трябва да може да избира един, няколко или всички destinations. WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY. NOT_SELECTED != BLOCKED. CREATE и UPDATE са отделни contracts. Readback е задължителен след write. Activation изисква authorization.

Batch engine класифицира product/target като AUTO_READY, NEEDS_REVIEW или BLOCKED. Целта е операторът да одобрява ready set и да работи само по exceptions, conflicts, destructive actions и high-risk anomalies. Потвържденията за category-wide publish трябва да се автоматизират по правила, а не да изискват целодневно кликане.


## 11. Orders, Dolibarr и couriers

M99 Order Hub трябва да сваля поръчки от разрешените магазини, да normalize-ва и deduplicate-ва и да ги предава към Dolibarr Sales Orders. Dolibarr остава ERP/CRM/warehouse execution layer. Отворен operational проблем е физическата наличност да се намалява коректно при sale/expedition.

Courier Registry е extensible. Начални adapters: Speedy, Econt, Sameday. Auto-AWB се разрешава само след controlled acceptance на address, office/locker, phone, COD, weight, package count, payer и service type mappings.


## 12. Product 2041 / M99 100018 — текущ pilot

Canonical identity: M99 100018; Job 27 / Item 29; supplier ref 042502; Manufacturer MPN 042502 като отделна роля; exact Palltex URL https://palltex.bg/bg/p/daytona/17374; existing m99.eu Product ID 2041.

Product 2041 е EXISTING и трябва да се UPDATE-ва, никога да не се CREATE-ва повторно. Последно доказан live readback: id 2041, reference M99 100018, price 30.2 net, tax rules group 0, category 26, active 0, available_for_order 0, visibility none, images 0, combinations 0. Той е hidden/non-orderable pilot и не е production-ready.

Canonical preview има 1 image URL и 8 variant rows. Преди live update трябва да има corrected full-payload preview/writer simulation, exact identity guard, pricing/VAT resolution, image/variant/default-combination quality gates и hidden update + readback. При ambiguous connection reset след write няма automatic retry; първо recovery/readback.


## 13. Release engineering — нормативно правило v17

Всеки бъдещ executable ZIP/package задължително преминава: STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE. За checkpoint следват COMMIT → PUSH → REMOTE_VERIFY.

Ако липсва задължителен слой: NOT_RELEASEABLE. Failed revision никога не става stable baseline. Нито един gate не се пропуска за скорост. Windows-only проверка никога не се обявява PASS преди реално изпълнение.

PowerShell ZIP има отделен VALIDATE_*_AST.ps1 с Parser.ParseFile и CMD го изпълнява преди main script. Known-regression scans трябва да пазят срещу предишни дефекти: foreach parser spacing, automatic $Args collision, diverged Git diff discovery, arbitrary staged threshold, Unicode-dependent matching, wrong pytest root/import context, unexpected dirty state, ambiguous write retry и вече установения R2.8 MAX_PATH/Copy-Item проблем.


## 14. Continuous execution и ускоряване

Ако следващата техническа стъпка е определена и не изисква ново бизнес решение, secret, destructive action, нова live-write authorization или разрешаване на ambiguity, работата продължава автоматично. Не се спира с въпрос „да продължа ли?“. Свързаните промени се обединяват в по-голяма ревизия, максимално се тестват преди ZIP и Windows остава final acceptance.

При технически failure се прави autonomous diagnosis/recovery, без да се поврежда stable baseline. Практическият vertical result — продуктово въвеждане/публикуване — има приоритет пред архитектурно почистване, което не го блокира.


## 15. Git checkpoint policy

Definition of Done: TESTED → WINDOWS_ACCEPTED → COMMITTED → PUSHED → VERIFIED. Всеки работещ Windows-accepted checkpoint трябва да завършва с commit + push + remote verify, освен когато конкретната ревизия изрично е само preparation/staging.

Използва се exact staging; никога blind Commit All. Изключват се operational DB, _m99_backups, runtime logs/state, caches, secrets, ZIP/temp reports/audit artifacts. Няма force/reset/clean/automatic rebase. При remote moved/conflict системата fail-close.

Recovery branch не се merge-ва автоматично в main. Това е consequential action и изисква отделно решение след reconstruction validation.


## 16. Recovery reconstruction — доказана история

Поради проблеми в по-късните runtime/process-control revisions беше избран clean reconstruction от c447e0d. Suspicious boundary е c447e0d → 56f6d0f, където е добавен runtime manager с process-control. Това не е доказателство за причината за ClientError, а причина за консервативно възстановяване.

R1–R1.6 откриха и поправиха: recursive Git wrapper, Git discovery, wrong pytest root/import context, nonzero pathspec handling, duplicate Add Products regression и Unicode exact-match проблем. R1.7 достигна full 1064 tests PASS + 6 warnings. R1.8 направи verified checkpoint commit 4c8c81cb5c01177d5a1d7192395c24caf8d97fe1 и remote verify.

R2.0–R2.5 откриха selector regex, diverged diff discovery, PowerShell foreach syntax, $Args collision, arbitrary staged threshold и malformed condition. R2.6 въведе real Windows AST pre-gate и достигна 66 focused PASS + 1064 full PASS + 6 warnings; остави exact staged admin-platform/app/main.py, без commit/push.

R2.7 беше създаден, но по-късно обявен NOT_RELEASEABLE по новия full-verification contract и не трябва да се използва. R2.8 опита да добави README v17 + machine policy, но Windows спря на MAX_PATH при Copy-Item. R2.9 поправи това с extended-path byte copy; Windows: AST PASS, policy readback PASS, 66 focused PASS, 1064 full PASS + 6 warnings, staged files = 3, commit/push FALSE.

R2.10 беше предназначен за exact 3-file commit/push/verify, но FAILED преди Git mutation. AST беше PASS, след което malformed PowerShell `throw"WRONG_HEAD"` се интерпретира като команда `throwWRONG_HEAD`. Exit code 1. Следователно R2.10 не е checkpoint и не е доказан commit/push. Освен това условието е било в true branch, което означава, че при изпълнението HEAD не е съвпаднал с hardcoded base; actual HEAD трябва да се прочете, а не да се предполага.


## 17. Текущ Git state и правило след R2.10

Последният доказан remote stable recovery checkpoint е 4c8c81cb5c01177d5a1d7192395c24caf8d97fe1 на recovery/c447e0d-clean-reconstruction. Последният доказан historical main stable checkpoint е 2c779450f8809afc3eddc738e949a34fbb47ea20.

След R2.9 са доказани точно 3 staged файла: admin-platform/app/main.py, README_M99_v17_FULL_VERIFICATION_RULE.md и M99_FULL_VERIFICATION_POLICY_v17.json. R2.10 не е направил commit/push според показания log, но понеже HEAD mismatch condition се е задействала, следващият installer трябва първо да прочете actual branch/HEAD/status и да fail-close при неочаквана промяна; не трябва да reset-ва или да гадае.


## 18. Исторически важни checkpoints

v0.7.1 Rev7: 234 tests PASS; commit 8c3d2d7fc729f22001c320d1fa033528272eb21e. v0.7.2 Phase 1: Canonical Data Model Foundation PASS; commit 193b6bcc6c8f4b13439102a99f00d1b542b1851f. Phase 2: SQLAlchemy + Alembic baseline PASS; real admin DB not migrated. Phase 2.5 PrestaShop 9 variants имаха import/runtime failures и не са stable publish proof.

Phase 4.6 R7K/R7K.1/R7K.2.x/R7K.3.x развиха Palltex controlled product publish, durable manufacturer evidence, identity/content gates. R4.3.4–R4.3.13 развиха Product 2041 preview/readback/full-payload/browser auth foundations. R4.3.11 има известен defect: invented child combination refs; това не трябва да се връща.


## 19. Отворени задачи — приоритетен ред

1) Създаване и записване на този v18 resume checkpoint в GitHub Desktop без destructive Git действие. 2) Прочит на actual branch/HEAD/status след R2.10 failure и безопасен exact checkpoint commit/push/remote verify на валидния set. 3) Продължаване на recovery branch без runtime/process-control.

4) Product 2041: corrected full-payload preview/writer simulation без invented child refs; exact UPDATE-only identity; pricing/VAT fail-closed; image + 8 variants + exactly one default; hidden update/readback само след всички gates и authorization. 5) След m99.eu pilot — duplicate lookup/review и adapters за останалите избрани канали.

6) Daily supplier price monitoring и governed application на 1.0–1.7% pricing rule. 7) Order Hub → Dolibarr → warehouse/fulfillment → courier adapters. 8) Dolibarr physical stock decrement при sale/expedition. 9) MoneyWorks migration: products + suppliers + customers + prices/contractors. 10) README/history artifacts да се поддържат при всеки значим checkpoint.


## 20. Как да се продължи след рестарт

Първо прочети README_M99_v18_2026-09-26.md и M99_KNOWLEDGE_STATE_v18_2026-09-26.json. След това прочети actual Git branch/HEAD/status; не приемай hardcoded HEAD. Сравни staged/untracked/unstaged set с checkpoint документацията. Не използвай R2.7 или failed R2.10 като stable baseline.

Ако v18 документите са само staged в GitHub Desktop, следващата задача е full-verification checkpoint commit → push → remote verify на exact intended files. Ако вече са committed/pushed, verify remote HEAD и clean tree. След verified checkpoint продължи директно към Product 2041 corrected full-payload work.

Не искай повторно потвърждение за технически определени, non-destructive стъпки. Спирай само при ново бизнес/governance решение, secret, destructive action, нова live-write authorization или реална ambiguity.


## 21. Resume marker

M99_RESUME_V18_2026_09_26_R29_ACCEPTED_R210_FAILED_HEAD_STATE_VERIFY_NEXT



---

# АРХИВНО ПРИЛОЖЕНИЕ — v20 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — Master README v20 / Consolidation R1

**Дата:** 2026-09-27  
**Статус:** DECIDED / DOCUMENTATION CHECKPOINT  
**Роля:** консолидирана human-readable project constitution и план за следващата работа.

> Precedence: latest explicit superseding decision wins; history is preserved. DECIDED != IMPLEMENTED. TESTED != WINDOWS_ACCEPTED. WINDOWS_ACCEPTED != PRODUCTION_READY.


## 1. Роля на документа

Този документ е консолидирана човешка памет на M99 Knowledge Platform към 27.09.2026. Той събира установените в проекта правила, архитектурни решения, доказани тестови резултати, трите линии за въвеждане на продукти, каналите, правилата за идентичност, съдържание, цени, ДДС, публикуване, безопасност и начина на разработка. При конфликт важи правилото: най-новото изрично решение, което отменя старо решение, има предимство; историческото решение се пази като история. DECIDED не означава IMPLEMENTED, а IMPLEMENTED не означава WINDOWS_ACCEPTED или PRODUCTION_READY.

## 2. Бизнес цел и обхват

M99 Knowledge Platform е централната система за знание, продуктова идентичност, доставчици, производители, марки, продуктови данни, съдържание, цени, канали, публикуване и последващ readback. M99 е Single Source of Truth за каноничната идентичност и провереното знание. Дългосрочният бизнес контекст е M99 Group Master Plan 2036: минимален административен персонал, безопасна автоматизация, международна експанзия и цел за устойчив собственически доход. Knowledge First и AI Native, not AI Invented остават основни принципи.

## 3. Основни governance правила

1) M99 е собственик на каноничната идентичност. 2) Няма дублиране на канонични факти по канали; каналите са destinations. 3) Observation е evidence, не автоматично truth. 4) Manufacturer evidence е по-висок фактически авторитет за технически характеристики; supplier/B2B е основен източник за цена, наличност, варианти и търговски факти. 5) Supplier, Manufacturer и Brand са различни роли/обекти. 6) AI може да редактира и локализира доказани факти, но не може да измисля технически или търговски факти. 7) Историческите наблюдения се пазят. 8) Премахване от канал не унищожава M99 knowledge. 9) Всяка важна автоматизация е fail-closed. 10) Операторът работи през M99 Knowledge UI, без необходимост от Python, PowerShell, API, XML, JSON или SQL.

## 4. Канонична идентичност и ProductGroup

Новият нормативен M99 reference е „M99 “ + шест цифри, напр. M99 100018. Старите M99-<digits> са compatibility/history, не формат за нови allocations. Идентичността никога не се използва повторно за друг ProductGroup. Identity resolution има четири състояния: NEW, EXISTING, AMBIGUOUS, UNRESOLVED. AMBIGUOUS и UNRESOLVED блокират автоматичен write и изискват човешко решение. ProductGroup lifecycle е draft → active → paused → retired. Hard DELETE е отделна, изключителна операция и изисква операторско одобрение, ръчно въвеждане DELETE и audit. UPDATE никога не преминава мълчаливо към CREATE.

## 5. Трите исторически линии за въвеждане на продукти

В проекта са се развили три основни supplier линии. Те не са конкуриращи се архитектури, а три източника на доказани решения, които трябва да бъдат консолидирани.

A) STENSO → Bultex99. STENSO е ранният референтен supplier connector с contract health_check → list_categories → list_products → get_product. След преминаването към bultex99.com старият stenso.net се използва като migration/identity evidence, а не като текущ source of truth. Bultex99 развива public catalog parser, отделен B2B read-only слой, legacy STENSO matching, осем selection modes, identity preview, target intersection, dry-run и bridge към общия Product Import Wizard. Panda UNO LOW е първият детайлно подготвен Bultex99 кандидат.

B) Calenda.bg. Calenda развива най-дълбоко evidence/hydration/variant accuracy: product grouping, supplier reference, color variants, variant-specific images, image hydration, size availability, evidence governance, supplier reconciliation и deep discovery. Ключовото правило е, че supplier availability не е M99 physical stock; размер/цвят не се превръщат автоматично в идентичност; Manufacturer MPN не се измисля от supplier hydration; изображенията трябва да бъдат свързани с правилния вариант чрез доказателство.

C) Palltex.bg. Palltex развива най-силно durable evidence, manufacturer/brand resolution, canonical identity, publish-ready content gate, controlled publishing, duplicate protection, readback и audit. BWolf е brand на Palltex; за този source Palltex е supplier и manufacturer, BWolf е brand. Линията R7K/R7K4 доказва controlled publish към m99.eu, но натрупва много исторически runtime routes, които не трябва да останат като отделни operator workflows.

## 6. Извод от трите линии

Крайното решение е един M99 Unified Product Intake Engine с supplier-specific adapters. От Bultex99 се запазва general import/selection contract и разделението public/B2B; от Calenda — evidence/hydration/variant/image accuracy; от Palltex — durable evidence, identity governance, quality gates, controlled write/readback/audit. Не се създава четвърти importer и не се избира една supplier линия за „победител“. Спецификите остават в adapters; общите правила се изнасят в shared canonical pipeline.

## 7. Единен operator workflow

Единственият нормален операторски вход трябва да бъде M99 Knowledge → „Добави продукти“ (/operator/add-products). Потокът е: Доставчик → Обхват/избор → Hydration/Evidence → Identity → Canonical Product → Content → Price/VAT → Quality Gates → Channel Selection → Review → Publish → API Readback → Audit. Старите отделни publish screens могат временно да останат като compatibility/backend implementation, но не трябва да са нормален операторски път.

## 8. Selection modes

Общият importer поддържа: един продукт; няколко продукта; една категория; няколко категории; всички продукти; първите N; само новите спрямо M99; ръчен избор. При масови операции няма потвърждение за всеки продукт. Системата прави batch preflight/QA, операторът одобрява избрания scope веднъж, валидните продължават, а невалидните се блокират индивидуално.

## 9. Evidence и canonical facts

Evidence pipeline: Manufacturer evidence → Supplier evidence → M99 canonical facts → editorial/SEO composition → localization → Quality Gate → Channel content. Важните факти пазят provenance: source, време на observation/verification и conflict/reviewer context, когато е наличен. Неподкрепени standards, certifications, materials, technologies, dimensions, stock или performance claims не се публикуват. Manufacturer, supplier и brand никога не се сливат само защото на конкретен източник са една и съща организация.

## 10. Съдържание и езици

Каноничната многоезична база е BG + EN + RU + RO. Каналът получава само езиците, които реално поддържа, а language IDs се откриват от конкретния shop и не се hardcode-ват глобално. За m99.eu доказаните active languages са EN/BG/RU с live IDs 1/2/3 към последния authenticated read-only preflight.

За всеки задължителен език: Product Name, H1, Short Description, Long Description, H2/H3 (и H4/H5 при нужда), Meta Title, Meta Description, FAQ, технически текстове, ALT, slug/link rewrite и textual structured-data fields. H1 е точно един. Short Description е отделен asset. Meta Description и Short Description трябва да са достатъчно различни; установеният similarity gate е < 0.75. Long Description е приблизително 400–700+ смислени думи, целево 500–800 при достатъчно evidence, без padding. Обичайно 4–7 H2, FAQ 4–8 при достатъчно evidence. Standards/certifications са hard factual gate. Images: WEBP, приблизително 1200–1400 px, локализирани ALT. Variants идват само от evidence и има точно една default combination.

## 11. Цена и ДДС

Целевата цена в собствените канали е customer-facing GROSS/VAT included. Проверената supplier gross цена се подбива с persisted random margin между 1.00% и 1.70%. Margin се избира при initial pricing или при доказана промяна на supplier price и се пази до следваща промяна. NO_CHANGE = NO_WRITE. VAT е channel/market configuration и никога универсален hardcode. Pipeline: supplier observation → change detection → pricing rule → currency/market → channel VAT → target GROSS → platform representation → write → API readback → front-office gross verification. Supplier price monitoring е предвидено ежедневно.

## 12. Channel Registry — актуално решение

Операторът трябва да вижда всички целеви destinations и да може да избира един, произволен subset или всички READY targets. Формулата остава WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY. NOT_SELECTED и BLOCKED са различни състояния.

Уеб канали: mela99.com — Thirty Bees / PrestaShop 1.7 family; m99.eu — PrestaShop 9.1.5; rabotni-drehi.com — WordPress; medicinski-drehi.com — WordPress; laviro.ro — PrestaShop 1.6.1.24; alviro.ro — Romanian e-commerce channel, readiness трябва да се доказва; toplinka.com — WordPress + WooCommerce, вече изрично включен като пълноправен product publishing channel. Dolibarr е ERP/CRM/warehouse destination, не public shop и не owner на canonical identity.

Новото решение от 27.09.2026 отменя старото foundation описание, в което toplinka.com е „not enabled for product import“. Той трябва да присъства в Channel Registry, Channel Selection UI, target-resolution тестовете и бъдещата Channel Adapter архитектура. READY не се приема по подразбиране — доказват се WooCommerce API/write contract, authentication, languages, VAT/price rules, product/variant mapping и readback.

## 13. Publishing governance

Публикуването на продукти се извършва от M99 Knowledge UI, не от CMD. CMD/PowerShell може да остане development/install/test механизъм, но не е операторски publish интерфейс. Бутонът „Публикувай“ е explicit write authorization за показания product/scope/targets. Backend непосредствено преди write повтаря identity, duplicate, price, VAT, languages, content, variants, images, target readiness и authorization gates. CREATE и UPDATE са отделни contracts. Няма DELETE в нормалния publish pipeline. При ambiguous POST outcome няма blind retry; първо readback/recovery. След успешен write има задължителен readback и audit.

## 14. m99.eu доказан статус

m99.eu е PrestaShop 9.1.5. Authenticated read-only preflight R2 доказва API authentication, dynamic languages, category/schema reads и permissions. Последният доказан remote checkpoint е 7c81f3b17148392041d31aabe4a3ed809f5ad5d0 на dev/m99eu-auth-readonly-preflight-r2. Live language mapping: id 1=en, id 2=bg, id 3=ru. Products permissions са GET/POST/PUT true, DELETE false. Test category 26 е inactive. Доказаният транспорт за проблемната Windows среда използва fresh one-shot HTTPS connection, Basic Auth, Connection: close и no retry. API key никога не се показва в UI/log.

## 15. Panda UNO LOW — текущ Bultex99 кандидат

UNO LOW S3S FO LG SR ESD — Panda е първият подготвен кандидат за Bultex99. Supplier public product 5161; примерен variant SKU за размер 36: 06100764.36; sizes 36–48; supplier gross price €58.90 VAT included; standard EN ISO 20345:2022+A1:2024; protection S3S FO LG SR ESD. Manufacturer evidence от Calzaturificio Panda Sport сочи model 11720E и weight 570 g. Persisted price decision при supplier €58.90 е margin 1.31% и M99 gross €58.13. Потенциалният next canonical ID M99 100019 трябва да бъде проверен за collision непосредствено преди allocation; не се приема сляпо.

## 16. Palltex controlled live история

Palltex R7K/R7K4 линията доказва first controlled live creation/readback към m99.eu за M99 100018 / channel Product 2041. Продуктът е създаден hidden/non-orderable в test category и API truth е verified, но исторически не е production-ready поради quality blockers като images/combinations/content/SEO/tax-rule validation. Това доказателство се използва за publish safety patterns, не като причина да се запази Palltex-specific operator UI.

## 17. Development и release правила

Потребителят не е програмист и Windows acceptance трябва да е последна проверка, а не основна debugging среда. Всяка версия се самотества максимално преди предоставяне: STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE. Stable checkpoint добавя COMMIT → PUSH → REMOTE_VERIFY. Failed revision никога не става stable. Full regression е allow-list: root tests/ от repo root и admin-platform/tests/ от admin-platform. Не се включват output, backups, scripts, live network diagnostics и credential probes като implicit regression roots.

## 18. Git и safety правила

Без reset, clean, rebase, merge или force push като автоматични действия. Exact staging only; никога Commit All. Не се прави website write, DB migration или process kill от SAFE installer. Secrets не се логват. Source failure не означава zero stock. Supplier availability не означава M99 physical stock. API success не означава business acceptance. При connection reset след write — readback/recovery first, no blind retry. Не се твърди PASS, push или remote verify без доказателство.

## 19. Натрупан архитектурен дълг

Текущият runtime съдържа няколко исторически operator/publish routes: product_publish, operator_single_product_publish, unified_add_products, r37_add_products_flow, r7k4 operator publish, r7k4 real operator publish, r730 knowledge publish center и други Phase 4.6 services. Има дори повторно include на r730 publish center в main.py. Това е development history, не желаната крайна UX архитектура. Не трябва да се добавя нов паралелен път; трябва да се направи inventory, characterization tests и контролирана консолидация към /operator/add-products.

## 20. Решение: следващата работа е в пет етапа

ЕТАП 1 — Consolidation Map, без runtime промяна. Всички свързани файлове и routes се класифицират като AUTHORITATIVE / REUSE / LEGACY / DEPRECATE / TEST-HISTORY. Картата включва Bultex99/STENSO, Calenda, Palltex, всички publish paths, channel adapters и release gates.

ЕТАП 2 — Unified Supplier Adapter Contract. Bultex99, Calenda и Palltex остават supplier-specific adapters, но връщат един canonical SupplierProductEvidence contract. Общите capabilities включват identity facts, technical facts, images, price, availability, variants и commercial evidence; липсващ capability остава explicit unsupported/unknown.

ЕТАП 3 — Unified Product Intake Pipeline. Един engine: Selection → Hydration → Evidence → Identity → Canonical → Content → Price/VAT → QA → Targets. /operator/add-products е единственият нормален operator entry point.

ЕТАП 4 — Unified Publish Service. Publish service получава canonical product и channel targets; не трябва да зависи от това дали source supplier е Bultex99, Calenda или Palltex. UI → Publish Service → Channel Adapter → API → Readback → Audit. toplinka.com влиза като WordPress/WooCommerce channel adapter target.

ЕТАП 5 — Migration + Regression. Трите доказани supplier сценария стават golden regression flows: Bultex99/Panda UNO LOW; Calenda реален color/size/image scenario; Palltex BWolf/M99 100018 controlled history. Старите parallel runtime paths се deprecated едва след доказване, че новият pipeline покрива функционалността без regression.

## 21. Definition of Done за Consolidation R1

R1 не прави live website write. Резултатът е пълна dependency/consolidation map, authoritative component list, legacy/deprecation list, regression specification и точен migration sequence. Не се премахва работещ historical code преди characterization tests. След R1 следва implementation на shared contracts с максимални simulations и пълния README v17/v19 release gate.

## 22. Разговорни решения, които вече са нормативни

Потребителят изрично изисква: да не се създават нови обходни пътища; да се използва съществуващият M99 Knowledge environment; публикуването да е през M99 Knowledge, не през CMD; да се правят максимално много тестове и симулации преди Windows версия; да не се чака допълнително „давай напред“ за технически безопасни стъпки; трите supplier линии да бъдат изучавани като история преди консолидация; toplinka.com да бъде включен в channel selection и е WordPress/WooCommerce; следващата работа да е точно в петте етапа по-горе; README, machine-readable memory и български DOC/DOCX трябва да пазят това решение и историята.

## 23. Принцип за бъдещи промени

Преди нова архитектурна промяна се четат Decision Registry, Current Context, Project State, latest master README, relevant ADRs, tests и Git history. Стар README не се приема автоматично за истина, когато е superseded от по-ново изрично решение и доказан runtime/test acceptance. Новата работа трябва да намалява броя на паралелните пътища, а не да ги увеличава.



---

# АРХИВНО ПРИЛОЖЕНИЕ — v19 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — README v19

**Checkpoint date:** 2026-10-06  
**Repository:** `ludmil03/M99-Knowledge-Platform`  
**Primary local repository:** `C:\Users\user\Documents\GitHub\M99-Knowledge-Platform`  
**Current recovery/runtime worktree:** `C:\Users\user\Documents\GitHub\M99-CANONICAL-ADD-PRODUCTS-V6-R1\M99-Knowledge-Platform`  
**Document role:** Master Human-Readable Constitution + Resume Checkpoint + Recovery/Acceptance Contract  
**Precedence:** latest explicit superseding decision wins; historical evidence is preserved.  
**Core anti-loop rule:** `DECIDED != IMPLEMENTED`.

> README v19 consolidates the project decisions from the beginning through 2026-10-06 and supersedes stale current-state statements in earlier README/state files. Earlier files remain historical evidence and must not be deleted.

## 0. Mandatory resume protocol

Before any new M99 architecture or implementation work, read in this order:

1. README v19.
2. Machine memory/state companion for v19.
3. Current Git state and exact branch/worktree.
4. Relevant tests and historical accepted checkpoints.
5. Only then propose or implement the next milestone.

Never infer that a failed implementation reopens an already decided architecture rule.

## 1. Mission

M99 Knowledge Platform is the canonical identity, verified product knowledge, supplier/manufacturer evidence, content/SEO, pricing/VAT, publishing, synchronization, ERP/CRM and audit/governance layer for M99 Group.

It is not a one-site scraper and not a one-channel uploader. The long-term direction is M99 Group Master Plan 2036: international BG/EN/RO expansion, minimal administrative headcount, safe automation, improved cash-flow/stock control and operator-first workflows.

## 2. Binding governance

- Knowledge First.
- Evidence Based.
- No Duplicate Data.
- Identity Before Content.
- AI Native, not AI Invented.
- Supplier != Manufacturer != Brand.
- CREATE != UPDATE.
- Duplicate guard before CREATE.
- Mandatory readback after every write.
- Operator-first UX.
- Human by exception, not by repetition.
- ProductGroup lifecycle: `draft -> active -> paused -> retired`.
- Hard DELETE only after operator approval and manual typed `DELETE`, with audit.
- Historical observations are preserved.
- Removing a channel mapping never destroys canonical M99 knowledge.

## 3. Operator and release discipline

The operator is a business user, not a programmer. Normal work is performed in M99 Knowledge UI. CMD/PowerShell/Python are bootstrap, recovery, diagnostics and acceptance tooling only.

No release/package is considered accepted merely because synthetic or Windows tests pass.

Mandatory Definition of Done:

`TESTED -> WINDOWS_ACCEPTED -> REAL_M99_ACCEPTED -> COMMITTED -> PUSHED -> REMOTE_VERIFIED`

Mandatory gate order:

`STATIC -> SYNTAX_AST -> KNOWN_DEFECT_REGRESSION -> STATE_SIMULATIONS -> SAFETY_FAIL_CLOSED -> FOCUSED_TESTS -> FULL_REGRESSION -> PACKAGE_INTEGRITY -> WINDOWS_PRE_GATES -> WINDOWS_ACCEPTANCE -> REAL_M99_UI_ACCEPTANCE -> COMMIT -> PUSH -> REMOTE_VERIFY`

A failed revision never becomes stable.

## 4. Pre-delivery MAXSIM rule

Before giving any Windows ZIP, exhaust all practical local tests and simulations. This is binding.

At minimum:
- static/syntax/AST checks;
- known-defect regressions;
- realistic state-transfer simulations;
- fail-closed and rollback paths;
- focused tests;
- full regression;
- ZIP/package readback;
- launcher/runtime identity;
- realistic Jinja/HTTP route tests;
- Git-not-in-PATH / GitHub Desktop embedded Git;
- exact repository basename;
- stale/orphan worktree collision;
- Unicode/CRLF/encoding regressions;
- no destructive Git;
- no website write during installer;
- no DB migration unless explicitly authorized;
- no process kill;
- no commit/push before real acceptance.

## 5. Git safety

Forbidden without explicit new authorization:
- `git reset --hard`;
- `git clean`;
- force push;
- uncontrolled merge/rebase;
- Commit All / blind staging.

Use exact staging only.

The original dirty worktree is evidence and must remain untouched during recovery/reconstruction unless a later explicit decision supersedes this.

## 6. GitHub Desktop situation on 2026-10-06

The supplied GitHub Desktop screenshot shows:

- repository: `M99-Knowledge-Platform`;
- current worktree: `M99-Knowledge-Platform`;
- current branch display begins `dev/m99eu-auth-readonly...`;
- **38 changed files** are visible;
- GitHub Desktop offers **“Commit 38 files…”**;
- the selected file is `admin-platform\app\services\stage3_milestone_a_orchestrator.py`;
- GitHub Desktop warns that the file uses LF and Git is configured to convert to CRLF on checkout;
- Fetch origin was performed and shows “Last fetched just now”.

**Binding action:** DO NOT press “Commit 38 files…”. Do not bulk-stage/commit these changes. This dirty worktree is not the clean reconstruction acceptance branch.

The proven recovery approach remains an isolated clean worktree with leaf directory exactly `M99-Knowledge-Platform`.

## 7. Proven reconstruction base and supplier strategy

The strongest verified historical reconstruction base is:

`b9a3140b098287f600f7741c9f7a6bc6bc8aa0b9`

Reason:
- inherits the proven Calenda integration line;
- contains Palltex connector/hydration/controlled publish/readback work;
- precedes later patch accumulation;
- preserves README v12-v15 governance.

Supplier strategy:
- **Calenda:** preserve existing working integration; do not rewrite without evidence.
- **Palltex:** preserve existing working integration; do not rewrite without evidence.
- **Stenso:** historical compatibility contract may remain, but Stenso is retired from the active source strategy.
- **Bultex99 public website:** new public connector only.
- Historical Bultex/BULTEX99 B2B portal work is a separate system and must not be reused as public `bultex99.com` scraping/auth logic.

Common architecture:

`M99 UI -> Add Products -> Source Registry -> supplier-specific adapter -> SupplierProductEvidence -> Canonical Product -> Identity -> Content -> Price/VAT -> QA -> Targets -> Review -> Publish -> API -> Mandatory Readback`

## 8. Canonical Add Products UX

Canonical initial route is:

`/add-products`

`/operator/add-products` is legacy and must not be the normal entry screen. If retained for compatibility, it must redirect safely to `/add-products`.

Normal operator flow:

`Source -> Category/Product -> Hydrate/Verify -> operator recovery if needed -> Identity -> DRAFT -> Targets/Review -> Publish -> Readback`

The operator must be able to re-extract the same product or an alternate exact product URL before DRAFT/channel write. A failed extraction must not trap the operator.

## 9. Product extraction and evidence

The public supplier connector must fail closed.

For images:
- accept product-specific evidence such as exact JSON-LD/OG/product media;
- reject flags, logos, theme assets, unrelated catalog images, generic staff photos and other page chrome;
- preserve product/variant image provenance;
- do not infer variant relationships without exact evidence.

Supplier availability is not M99 physical stock.

Missing evidence must produce a clear warning/review state, not invented facts.

## 10. Source-neutral identity wording

The UI must use **Source Product ID** or supplier-neutral wording.

Hard-coded “Calenda Product ID” is forbidden in generic Bultex/Palltex/other supplier flows.

Canonical M99 identity is independent from supplier SKU/reference, source product ID, manufacturer MPN, EAN/GTIN, MoneyWork ID, Dolibarr ID, channel product ID, title and URL.

Normative M99 reference: `M99 ` + six digits.

## 11. Target selection — binding UX

The operator selects targets **once**.

Supported combinations:
- one site;
- multiple sites;
- site + Dolibarr;
- multiple sites + Dolibarr;
- Dolibarr only.

Selection must persist through PREPARE -> Identity -> DRAFT -> Review. It must not be requested a second time.

Configured targets:
- mela99.com
- rabotni-drehi.com
- m99.eu
- medicinski-drehi.com
- laviro.ro
- alviro.ro
- toplinka.com
- Dolibarr

Safety formula:

`WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`

`NOT_REQUESTED != BLOCKED`.

A target that is not authorized or not ready must be classified individually. It must not cause an opaque whole-page JSON crash if other requested targets can still be evaluated safely.

## 12. Current R7 / R7 R1 findings

R7 installed and Windows tests passed:
- operator re-extract same/alternate URL;
- generic image exclusion;
- product image evidence fail-closed;
- multi-target UI;
- no website write/migration/process kill/Git mutation.

R7 R1 installed and Windows tests passed:
- source-neutral ID wording;
- targets selected once and carried forward;
- exact requested target set persisted toward DRAFT;
- safety formula preserved.

**REAL M99 acceptance is still FAIL.**

Observed live defect:
When the operator selected:
- mela99.com
- rabotni-drehi.com
- m99.eu
- laviro.ro

and pressed the blue Continue to Identity/DRAFT button, PREPARE returned:

`R3.7 PREPARE failed: Operator is not authorized for requested target(s): rabotni-drehi`

This proves the new target-state UI/state persistence is reaching an older R3.7 authorization bottleneck.

## 13. Immediate next milestone — R7 R2 MAXSIM

R7 R2 must be a consolidated correction, not another narrow patch.

Required behavior:
1. Preserve single target selection from Hydrate through Review.
2. Remove the obsolete R3.7 single/limited-target authorization bottleneck from the active multi-target flow.
3. Evaluate each requested target independently as REQUESTED/AUTHORIZED/READY/BLOCKED.
4. Keep `WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`.
5. Do not silently authorize an unauthorized target.
6. Do not lose the entire PREPARE flow because one target is blocked; show target-level state and safe continuation where policy allows.
7. Preserve source-neutral Source Product ID.
8. Preserve operator re-extract/recovery.
9. Preserve image evidence fail-closed behavior.
10. Preserve Calenda/Palltex integrations.
11. Do not reuse historical Bultex B2B logic.
12. Add exact regression for:
   `Bultex99 -> mela99.com + rabotni-drehi.com + m99.eu + laviro.ro -> PREPARE -> Identity -> DRAFT`.
13. No website write in pre-delivery MAXSIM.
14. No commit/push until Windows and REAL M99 acceptance both pass.

## 14. Publishing is a real M99 UI operation

The user explicitly requires real publishing from M99 Knowledge UI, not CMD.

After R7 R2 stabilizes the flow, the milestone must continue toward:
- user-selected real product;
- user-selected target(s);
- explicit Publish button authorization for displayed scope;
- full payload;
- VAT;
- API write;
- mandatory full readback;
- no automatic retry after ambiguous write.

A Windows PASS is not proof that publishing works.

## 15. VAT and price

M99 business price is customer-facing gross/VAT included.

For ordinary Bulgarian PPE/workwear, current business rule is 20% VAT unless exact governed evidence says otherwise. Channel tax binding must still be resolved and read back correctly; do not hard-code an arbitrary PrestaShop tax-rule-group ID.

If a target platform stores tax-exclusive price:
`NET = GROSS / 1.20` under the applicable 20% rule, with controlled rounding.

Do not use `/api/tax_rules_groups` HTTP 400 as the sole tax discovery gate. Prefer a proven valid existing product/configuration/readback path.

Pricing rule for own channels:
verified supplier gross benchmark less a persisted random 1.0%-1.7%. Do not re-randomize when supplier benchmark has not changed.

## 16. Full product payload requirement

Real publication must not be a minimal placeholder payload. Where applicable and evidenced, it includes:
- M99 ID;
- names/content for required channel languages;
- Supplier / Manufacturer / Brand separately;
- supplier SKU/reference;
- source Product ID and URL;
- canonical category;
- short/long descriptions;
- SEO title/meta;
- technical/material facts;
- standards only when applicable/evidenced;
- sizes/variants;
- images + ALT;
- price + VAT semantics;
- stock only when proven;
- active/category state;
- exact target;
- CREATE/UPDATE identity decision.

Readback must compare the written product. Wrong price/VAT/language/category/variant/image/identity is a failure.

## 17. Language/content baseline

Canonical baseline: BG + EN + RU + RO, subject to target channel requirements.

AI may write/structure/translate verified facts, but may not invent standards, materials, stock or technical claims.

Content must remain customer-facing; internal governance/debug/evidence text must not leak into published copy.

## 18. Runtime acceptance facts

Clean accepted recovery worktree:
`C:\Users\user\Documents\GitHub\M99-CANONICAL-ADD-PRODUCTS-V6-R1\M99-Knowledge-Platform`

Proven runtime launcher method:
- use original proven `admin-platform\.venv`;
- load original proven `admin-platform\.env.local` through `scripts\Load-Env.ps1`;
- do not print/copy/change secrets;
- set runtime import path/current directory to the clean worktree;
- verify `app.main.__file__` points to the intended clean worktree;
- run on the configured host/port.

Proven live runtime port during current acceptance: `127.0.0.1:8070`.

Never allow an old server on an existing port to masquerade as the new runtime.

## 19. Historical proven checkpoints to preserve

- Stage 1 commit: `37184e2abf94ffe773aa71f2c20efe841d4d8007`.
- Stage 2 commit: `c93686698f14a861ab476a59e0aef6b9e9d4b7bd`.
- Stage 3 commit: `b868be5a9c9c61ecafdc633ff8f7d03bd35b67c7`.
- Stage 4 commit: `a1bed8100ab29fed7cd57d053aed87dc32c5ba9d`.
- Historical reconstruction base: `b9a3140b098287f600f7741c9f7a6bc6bc8aa0b9`.
- Historical R6-R7F checkpoint: `ac3005eb610a3fe1e1417366a116fd51e61003aa`.
- Later public main tip observed in history: `2c779450f8809afc3eddc738e949a34fbb47ea20`.
- Recovery v18 context used trust anchor `4c8c81cb5c01177d5a1d7192395c24caf8d97fe1`; local recovery HEAD had moved to `f65a5f10f57510f0114695fb3a9f1639f020ba2d`.
- v18 focused Product 2041 suite: 129 passed; full regression passed with FastAPI deprecation warnings.

These are historical anchors, not permission to reset the current dirty worktree.

## 20. Known defects that must remain permanent regressions

Include regressions for:
- Git missing from PATH; GitHub Desktop embedded Git discovery;
- Unicode/Cyrillic and `core.quotepath`;
- LF/CRLF handling;
- pager/less unavailable;
- PowerShell parser/`$args`;
- dirty/unexpected state;
- exact repo basename `M99-Knowledge-Platform`;
- stale/orphan worktree path;
- mixed `str`/`Path` installer manifest;
- missing `.venv` in clean worktree;
- proven `.env.local` config source;
- runtime identity mismatch;
- realistic Jinja context;
- target state loss;
- hard-coded Calenda ID wording;
- legacy `/operator/add-products` route;
- `/api/tax_rules_groups` 400;
- ambiguous write/retry;
- CREATE/UPDATE collision;
- image contamination;
- category/product contamination;
- variants/colors/sizes becoming standalone products;
- package referencing nonexistent tests/files;
- synthetic test pass without live UI acceptance.

## 21. Current stop point / resume marker

**Resume marker:** `M99_RESUME_2026_10_06_R7_R1_REAL_M99_TARGET_AUTH_FAIL`

Current truth:
- R7 R1 installer: PASS.
- Windows acceptance for R7 R1 focused package: PASS.
- REAL M99 flow: FAIL at PREPARE authorization.
- No commit/push for R7/R7 R1.
- Original GitHub Desktop worktree: dirty, 38 changed files shown; do not Commit All.
- Next work: build **R7 R2 TARGET AUTHORIZATION + STATE CONTINUITY MAXSIM**, maximize simulations, then provide ZIP only after all feasible pre-delivery gates pass.

## 22. Next-session instruction

Do not ask the user to restate the project.

Start from Section 21 and:
1. inspect/patch the active R3.7 PREPARE authorization boundary;
2. preserve the R7/R7 R1 operator recovery and target-state work;
3. MAXSIM the exact four-target live scenario;
4. create a Windows ZIP only after tests pass;
5. Windows acceptance;
6. immediately repeat REAL M99 acceptance;
7. only after REAL M99 PASS: exact staging -> commit -> push -> remote verify.

Do not stop merely to say that work will continue when the next safe technical step is already known.



---

# АРХИВНО ПРИЛОЖЕНИЕ — SP001 (неизменен изходен текст; историческо свидетелство)

# M99 Knowledge Platform — Architecture Decision M99-SP-001

**Date:** 2026-10-08  
**Status:** APPROVED BY OPERATOR — governance decision; implementation pending  
**Title:** Supplier On-Demand + Selective Persistence  
**Applies to:** All current and future supplier connectors, including Bultex99, Palltex and Calenda.

## Binding decision
M99 must not mirror or permanently store complete supplier catalogs. Supplier categories and product listings are retrieved on demand and held only in a bounded temporary cache. Persistent M99 records are created only for products selected for M99 processing (DRAFT or later), subject to existing identity, evidence and authorization gates.

## Mandatory controls
1. **On-demand extraction:** Request only the supplier category/product information needed for the operator's current task.
2. **Bounded temporary cache:** Enforce expiration, size limits and eviction; never treat cache content as permanent M99 product records.
3. **Selective persistence:** Persist canonical product information only for selected DRAFT/managed products; do not bulk-import supplier catalogs.
4. **Evidence-first:** Retain sufficient verified facts, provenance, timestamps and hashes for governed decisions, without unnecessary full-page duplication.
5. **No redundant requests:** PREPARE, Identity, Content Intelligence and DRAFT reuse validated data rather than re-fetching the same supplier page per screen.
6. **Supplier request control:** Rate-limit, deduplicate requests and honor HTTP 429 / Retry-After. Never bypass supplier verification or interpret 429 as success.
7. **DRAFT recovery:** Persist selected DRAFT state safely so operator work can resume after restart; temporary cache loss must not destroy accepted DRAFT data.
8. **Selective monitoring:** Check supplier prices/availability only for active managed M99 products and only as permitted by source policy; supplier availability is not physical M99 stock.
9. **Fail-closed:** Missing, expired, mismatched or insufficient evidence requires review or explicit re-extraction; no invented facts or implicit publish.
10. **Existing governance remains:** Supplier ≠ Manufacturer ≠ Brand; CREATE ≠ UPDATE; exact target authorization; explicit Publish; mandatory full readback; no unapproved database migration or Git mutation.

## Implementation milestone
**R7 R2.7 — SELECTIVE PRODUCT PERSISTENCE + SUPPLIER REQUEST CONTROL MAXSIM**.
First inspect existing DRAFT/evidence schema and active routes; reuse existing storage where suitable. Implement and simulate bounded cache, source request control, restart recovery, authorization and fail-closed behavior. Run regression before Windows ZIP. Do not commit/push until Windows and REAL M99 acceptance both pass.

## Status clarification
This file records the approved architecture decision; it does **not** claim that the code, repository README, database or remote GitHub has already been updated.

