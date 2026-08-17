# M99 Knowledge Platform — README v5

> **Master System Constitution / Consolidated Project Specification**  
> **Статус:** работен нормативен master документ  
> **Консолидирано:** README v1 + README v2 + README v3 + README v4 + развитието до 17.08.2026 г.  
> **Repository:** `M99-Knowledge-Platform`

---

## 0. Роля на този документ

README v5 е петата консолидирана версия на техническата памет на M99. Той наследява README v1, v2, v3 и v4 и не отменя валидните им решения. Целта му е новият код да продължава от вече доказаното състояние, вместо проектът да се връща към стари или отхвърлени решения.

**Governance:** failure на discovery/parser/API не превръща вече доказано решение в неизвестно. Използват се registry/history → live verification → operator само при реален конфликт.

### Статуси
- **DECIDED** — изрично прието нормативно правило.
- **IMPLEMENTED** — има код/config/script.
- **TESTED** — доказано чрез тест, live GET, write/readback или migration analysis.
- **PROPOSED** — предложено, но не е нормативно.
- **OPEN** — нерешено.
- **DEFERRED** — прието като полезно, но отложено.

---

## 1. Визия и бизнес цел

M99 Knowledge Platform е централният knowledge, product, commercial и customer intelligence слой на M99 Group. M99 е Single Source of Truth за canonical identity и verified knowledge; Dolibarr е оперативният ERP/CRM/warehouse слой; сайтовете са channel representations; MoneyWork и съществуващите сайтове са legacy sources; manufacturer/supplier/B2B portals са evidence/commercial sources.

Бизнес целта остава международно развитие, минимален административен headcount, максимална автоматизация, подобрен cash flow, намаляване на slow-moving stock и приблизително 10 000 EUR чиста месечна печалба в рамката M99 Group Master Plan 2036.

---

## 2. Архитектура

```text
LEGACY + MANUFACTURERS + SUPPLIERS/B2B + CHANNELS + OPERATOR KNOWLEDGE
                                ↓
                    NORMALIZE / MATCH / EVIDENCE
                                ↓
                       CANONICAL M99 TRUTH
                                ↓
          PRODUCT/CONTENT — ERP/CRM/WAREHOUSE — CUSTOMER/SALES
                 ↓                  ↓                  ↓
          MULTI-CHANNEL TEST     DOLIBARR         NEXT ACTIONS
                 ↓
          OPERATOR APPROVAL
```

Целевата посока след v0.6.8.x е **един общ M99 importer engine**, а не отделен продуктово-специфичен скрипт за всеки артикул.

---

## 3. Историческо развитие

| Етап | Фокус | Ключова промяна |
|---|---|---|
| README v1 | Foundation | Single Source of Truth, Evidence Based, AI Native, repository foundation. |
| v0.5.x | Migration + ERP | MoneyWork importer, Dolibarr mapping, identity guardrails. |
| v0.6.2–0.6.3 | Evidence/Identity | Exact manufacturer evidence, supplier quarantine, existing-product discovery. |
| v0.6.4–0.6.6 | Content/publishing | Claim taxonomy, multilingual content, DRY_RUN/WRITE_DRAFT/readback. |
| v0.6.6.4.x | Legacy reconciliation | 2076 vs 2100 canonical field-by-field selection. |
| v0.6.7.0–.6.x | Cherokee pilot | Multi-source discovery, content, channel matrix, secrets, price, BNB FX. |
| v0.6.7.7.x | Real write + Quality | Technical write success ≠ Product Quality PASS. |
| README v3 | Constitution | TEST-first, identity governance, supplier monitoring, Customer 360. |
| v0.6.7.9.x | Five-channel recovery | rabotni-drehi REST/WooCommerce recovery, TEST bootstrap, image and identity gates. |
| v0.6.8.0–.2 | Unified importer | Common five-channel preflight/write architecture and hotfixes. |
| v0.6.8.3–.5.3 | CKE1124A integration | New-product import, legacy match, Laviro combinations/images, Alviro TLS diagnostic. |
| README v4 | Consolidation | Five-channel operational truth + recovery/Git checkpoint + path to batch import. |
| v0.6.8.6.x | Laviro price/VAT recovery | Доказано е, че цена/ДДС са правилни, а липсваща default combination може да счупи Front Office price display. |
| README v5 | Admin Platform Design | Selective new-product import, daily existing-product sync, Product Presence, RBAC, Supplier Browser и M99 Admin Panel. |

---

## 4. Canonical Product / Identity

M99 ProductGroup е master. Channel product, supplier page, manufacturer page, Dolibarr record и MoneyWork code са mappings/evidence.

ProductGroup lifecycle:

`draft → active → paused → retired`

Physical DELETE е разрешен само след operator approval и изрично ръчно `DELETE`.

### M99 Reference — вече решено

README v3 оставяше final canonical numbering format OPEN. След последващите реални тестове това е **DECIDED/TESTED**:

`M99-` + само цифри

Пример: `M99-1274366573`

Не се допуска буквено-цифров hash след `M99-`.

`supplier_reference` е отделно поле и никога не замества M99 reference.

---

## 5. Evidence и източници

Приоритетът остава:

exact official manufacturer → official catalogue/certificate → exact supplier/B2B → verified internal/legacy data → operator → AI върху verified data.

Near-match, wrong colour, conflicting protection class или ambiguous product не може да захранва commercial truth.

---

## 6. Изображения — актуализирано правило

Image pipeline:

`exact product discovery → verify → download → dedupe → resize → WebP → localized ALT → upload → association → readback`

**DECIDED:** source изображенията се изтеглят от производителя или доставчика. Друг M99 channel не се използва като source само защото вече съдържа правилното изображение.

Theme assets, logo, cart/search/home/header icons и други нерелевантни изображения трябва да бъдат отхвърляни.

---

## 7. Пет активни продуктови канала

Five-channel importer работи върху:

| Канал | Платформа / роля | Основен езиков режим | Състояние към 16.08.2026 |
|---|---|---|---|
| mela99.com | Thirty Bees / PrestaShop family | BG + EN, legacy RU layer | API/write работи; TEST 93; controlled product writes доказани. |
| medicinski-drehi.com | PrestaShop | BG + legacy multilingual fields | Legacy matching работи; CKE1124A product 1225 намерен; identity adoption остава incomplete. |
| laviro.ro | PrestaShop 1.6.1.24 | RO + EN | CKE1124A recovery PASS; TEST 128; 7/7 size combinations и 5 images. |
| alviro.ro | Thirty Bees family | RO + EN | Пети канал; DNS/TCP 443 PASS, verified TLS certificate validation FAIL; API-dependent checks blocked. |
| rabotni-drehi.com | WordPress + WooCommerce | BG | REST/WC auth възстановени; TEST 3007; controlled draft и image/variation write доказани. |

`m99.eu` остава част от по-широката M99 архитектура, но не е част от текущия five-channel product-write contract.

---

## 8. Publishing Constitution

1. NEW product → TEST/staging first.
2. TEST category се открива live; historical ID е hint.
3. Operator задава финални категории и activation.
4. Existing legacy name + URL/slug са locked.
5. Approved M99 product name + URL също стават locked.
6. Неодобрен TEST draft може да бъде ремонтиран.
7. CREATE и UPDATE са различни contracts.
8. PrestaShop/Thirty Bees `active=0`; WooCommerce `draft` преди approval.
9. Mandatory readback след write.
10. HTTP 200/201 ≠ Product Quality PASS.
11. Blocked channel не трябва автоматично да спира READY channels, освен при изрично atomic operation правило.
12. По подразбиране в текущата integration фаза: PUBLIC ACTIVATION = NO, STOCK WRITE = NO, DELETE = NO.

---

## 9. Language / Content / SEO

Езиковата чистота е critical gate. Фактите са canonical, но prose/SEO се адаптират по channel/language и не се копират механично.

Complete package:
- Product Name / H1
- short description
- long structured description
- H2/H3
- technical specifications
- materials
- verified sizes
- FAQ
- Meta Title
- Meta Description
- SEO keywords
- stable slug policy
- schema, когато каналът позволява
- images + localized ALT

M99 Style Guide и M99 Knowledge Base остават основата за AI SEO/marketing generation.

---

## 10. Pricing и monitoring

Supplier price, FX и channel price са отделни доказуеми стъпки.

За текущия Cherokee workflow е използвана supplier price × 0.987 логика; BGN използва EUR/BGN 1.95583; RO channel pricing използва официален BNB EUR/RON и последния публикуван курс в неработен ден.

**DAILY SUPPLIER MONITORING: MANDATORY** за идентифицираните активни supplier products:
- price;
- availability;
- variants/sizes;
- product changes;
- supplier reference;
- discontinuation.

Supplier availability ≠ M99/Dolibarr physical stock.

---

## 11. WW601 — интеграционен етап

Cherokee WW601 / supplier reference `08001931` беше основният benchmark преди CKE1124A.

В процеса бяха доказани:
- controlled TEST writes;
- price/FX gates;
- numeric M99 reference rule;
- WooCommerce recovery;
- необходимостта от exact-product image validation;
- manufacturer/supplier-only image sourcing;
- five-channel preflight architecture.

---

## 12. CKE1124A — текущият Gold Integration Product

Продукт: Cherokee Infinity CKE1124A, бордо.  
Supplier reference: `08001873`  
M99 reference: `M99-1274366573`  
Supplier price при теста: 34.30 EUR  
Размери: `2XS, XS, S, M, L, XL, 2XL`  
Exact supplier images: 5.

### Последно доказано състояние

**mela99.com**
- product 2459 беше създаден в TEST;
- 5 supplier images;
- QUALITY_PASS при v0.6.8.3.

**medicinski-drehi.com**
- legacy product ID 1225;
- legacy match = true;
- existing combinations/images са запазени;
- правилното действие е ADOPT_LEGACY_IDENTITY;
- v0.6.8.5.3 завърши с `LEGACY_ADOPT_INCOMPLETE`, защото reference/supplier_reference не бяха записани.

**laviro.ro**
- product ID 878;
- M99 reference и supplier reference са правилни;
- 7/7 size combinations са разпознати;
- 5 images;
- `LAVIRO_RECOVERY_PASS`.

**alviro.ro**
- DNS PASS;
- TCP/443 PASS;
- unverified TLS работи с TLS 1.3;
- verified certificate validation FAIL — expired certificate според Python SSL verification;
- API/language/TEST checks не трябва да се заобикалят чрез insecure TLS; първо certificate/chain fix.

**rabotni-drehi.com**
- product ID 96801 при CKE1124A import;
- 5 images;
- 7 WooCommerce variations;
- QUALITY_PASS при v0.6.8.3;
- targeted recovery v0.6.8.5.3 правилно не прави нов write.

---

## 13. Версии след README v3

### v0.6.7.9.1
Rabotni capability/auth/WAF diagnostic.

### v0.6.7.9.2
REST/WooCommerce read recovery; TEST category missing.

### v0.6.7.9.3
TEST bootstrap + controlled draft.

### v0.6.7.9.4
TEST 3007 и controlled product write; открит проблем с theme images.

### v0.6.7.9.5
Numeric M99 reference + exact image gate.

### v0.6.7.9.6
Image bridge experiment; окончателно е изяснено, че source трябва да е manufacturer/supplier.

### v0.6.8.0
Five-Channel Unified Importer; първоначален `SUPPLIER_REF` NameError.

### v0.6.8.1 / v0.6.8.2
Hotfixes; four-channel readiness постигната, Alviro остава blocked.

### v0.6.8.3
CKE1124A Five-Channel Import.

### v0.6.8.4
CKE1124A Recovery + Combination Gate.

### v0.6.8.5
Legacy Match + Laviro Image/Combination Recovery + Alviro TLS Chain Diagnostic.

### v0.6.8.5.1
Credential loader fix.

### v0.6.8.5.2
Self-contained launcher fix.

### v0.6.8.5.3
Targeted recovery:
- Medicinski legacy match;
- Laviro recovery PASS;
- Alviro root TLS blocker;
- no Mela/Rabotni write;
- no public activation;
- no stock write;
- no DELETE.

---

## 14. Dolibarr / Migration / CRM

M99 е canonical truth; Dolibarr е operational representation.

Migration pipeline:

`inspect → normalize → deduplicate → identity map → supplier/customer map → dry run → import → reconcile → audit`

MoneyWork code е legacy/external identifier, не автоматично M99 ID.

Target warehouse flow:
- supplier order → reception → physical stock increase;
- customer order → shipment/configured stock event → physical stock decrease;
- stock е variant-aware.

CRM foundation:
`Първо обаждане → Оферта → Второ обаждане`

Customer 360 и follow-up rules от README v3 остават валидни.

---

## 15. Security / Credentials / Audit

- No credentials in Git.
- No API keys/passwords in tracked plaintext.
- No secrets in logs/screenshots.
- Local credential loading е доказано за five-channel scripts.
- Production Vault остава deferred.
- Runtime JSON/TXT outputs са audit artifacts, не canonical truth.
- `output/` трябва да остане извън нормалния source commit, освен при изрично решение.

---

## 16. Git и 48H Recovery Snapshot

Преди repository consolidation беше направен локален 48-часов recovery snapshot.

Snapshot:
`C:\Users\user\Documents\M99-Recovery-Snapshots\M99_48H_20260816_174937.zip`

SHA256:
`81C262F00416F0675149B6BE001E95CD60029681049195F04AB53478192421AE`

Проблемният `M99 Knowledge Platform 140826.docx` беше копиран повторно след освобождаване от Word и присъствието му в ZIP беше проверено с `tar -tf`.

Snapshot съдържа и пакетите/source artifacts от v0.6.7.9.x до v0.6.8.5.3.

**Recovery snapshot ≠ Git source tree.** Той остава аварийно копие и не трябва автоматично да се push-ва целият.

---

## 17. Repository Version Governance

README файловете също са versioned project artifacts.

Правило от v4:
- `README.md` — текущата repository landing/master версия;
- `docs/history/README_v1.md`
- `docs/history/README_v2.md`
- `docs/history/README_v3.md`
- `docs/history/README_v4.md` или snapshot на текущата версия.

Преди промяна трябва да се извърши read-only repository audit. Никоя липсваща историческа версия не се измисля; тя се възстановява само от доказан файл/snapshot.

---

## 18. Consolidated Rule Updates във v4

| ID | Правило | Статус |
|---|---|---|
| ID-005 | M99 Reference = `M99-` + digits only | DECIDED/TESTED |
| IMG-002 | Product images идват от manufacturer/supplier source, не от друг M99 channel | DECIDED/TESTED |
| CHAN-001 | Current product importer contract има пет канала: Mela, Medicinski, Laviro, Alviro, Rabotni | DECIDED/TESTED |
| LEGACY-001 | Exact legacy match → adoption, не duplicate CREATE | DECIDED/TESTED |
| VAR-001 | Existing verified size combinations се запазват; missing combinations се създават само след gate | DECIDED/TESTED |
| TLS-001 | TLS verification failure не се заобикаля за production write; root cause се поправя | DECIDED |
| BACKUP-001 | Преди risky consolidation/push се пази validated recovery snapshot | DECIDED/TESTED |
| DOC-001 | README/master documentation има собствена version history | DECIDED |

Всички останали валидни правила от README v3 остават в сила.

---

## 19. Open / Deferred Decisions

- Universal Variant SKU standard.
- ProductGroup vs colour-variant universal boundary.
- Exact Dolibarr parent/variant implementation.
- Exact Dolibarr stock-decrease settings per deployment.
- Tax mapping per channel.
- Formal image-rights policy per supplier/manufacturer.
- Production Vault deployment.
- Formal acceptance/implementation of Customer Score, Prospect Engine, Next Best Action и Contact Fatigue Protection.

**Премахнато от OPEN:** final canonical M99 numbering format — вече е решено като numeric M99 reference.

---

## 20. Следващ продуктов batch

След CKE1124A следващата договорена продуктова стъпка е repeatable importer за **първите 10 артикула от Stenso категория „Медицинско облекло“**.

Цел:
1. без product-specific hardcoding;
2. source discovery;
3. identity/evidence;
4. supplier data;
5. canonical M99 object;
6. localized channel payloads;
7. images;
8. combinations;
9. five-channel preflight;
10. TEST/draft write само за READY channels;
11. readback;
12. operator QA.

След успешен 10-product batch → контролирано преминаване към 100–200 продукта.

---

## 21. Roadmap от текущата точка

1. Repository read-only audit за README v1/v2/v3 и source versions.
2. Freeze README v4 като следваща master documentation версия.
3. Repository Consolidation + Safe Push Prep.
4. Safe commit/push без credentials, runtime output и recovery ZIP.
5. Завършване на Medicinski legacy adoption за CKE1124A.
6. Alviro certificate/chain fix + full verified preflight.
7. 10-product Stenso medical batch importer.
8. Operator QA и baseline.
9. 100–200 product controlled scale.
10. Central pricing/image/content/quality engines.
11. Production daily supplier price + availability monitoring.
12. M99 → Dolibarr production integration.
13. Customer 360 / CRM automation.
14. International scale в M99 Group Master Plan 2036.

---

## 22. Definition of Success

**Single product:** exact identity, evidence, supplier mapping, pricing/FX, localized content, materials/sizes/FAQ, SEO, manufacturer/supplier images, variants, TEST draft, readback, operator-ready, no invented claims.

**Bulk:** първо 10 продукта, след това 100–200 през същия engine без специален код за всеки продукт.

**Five-channel:** всеки канал има independent preflight/status; blocked channel е видим и диагностируем, а READY channel може да продължи според publishing contract.

**Migration/ERP:** legacy identity/history не се губи; Dolibarr е operational representation на canonical M99 entities.

**Business:** по-малко ръчна работа, по-бързо и качествено развитие на каталога, контрол на price/stock/content и международна мащабируемост.

---

**M99 Knowledge Platform — Product truth once. Customer truth once. Verified everywhere. Operated through Dolibarr. Governed by humans.**

**README v5 — consolidated through 17.08.2026.**

---

# README v5 — Нови нормативни решения от 17.08.2026 г.

Следващите раздели са част от README v5 и надграждат, без да отменят, валидните решения от README v1-v4.

## 23. Laviro Price + VAT + Default Combination — доказано правило

При Laviro product ID `877` / M99 reference `M99-3423871970` / supplier reference `08001931` беше диагностициран случай, при който Back Office показваше правилна цена, а клиентската част показваше `0,00 lei`.

Диагностиката доказа:

- NET price: `168.548387`;
- Tax Rules Group: `5`;
- стандартна VAT ставка: `24%`;
- calculated GROSS: `209.00 lei`;
- 7 размерни комбинации;
- всички combination price impacts: `0`;
- specific price ID `14920` е legacy и изтекъл;
- server-side Front Office HTML съдържа правилни price signals `209`;
- първоначално `cache_default_attribute = 0`;
- първоначално няма нито една combination с `default_on = 1`.

След операторско задаване на default combination `7627 / XXS`:

- `default_on = 1`;
- `cache_default_attribute = 7627`;
- Front Office започва да показва правилно цената.

### DECIDED: M99 PRICE + VAT GATE

За всеки target market/channel:

1. M99 target selling price е **крайна клиентска цена с ДДС**.
2. Standard VAT rule/rate се чете от конкретния магазин/държава, а не се hardcode-ва.
3. Ако платформата пази NET price, M99 изчислява NET от target GROSS.
4. `id_tax_rules_group` не може да е нулев за продукт, който трябва да се продава със стандартно ДДС.
5. Combination price impact е `0` по подразбиране, освен когато конкретен вариант реално има различна крайна цена.
6. Specific prices се валидират и се различават active vs expired legacy.
7. API/Back Office price не е достатъчен за `QUALITY_PASS`.
8. След write се прави API readback и Front Office gross-price verification.
9. Front Office `0.00` при очаквана ненулева цена означава `PRICE_GATE = FAIL`.
10. Данъчните правила са channel-specific configuration, а canonical M99 price policy остава централизирана.

### DECIDED: DEFAULT COMBINATION GATE

Всеки вариативен продукт:

- трябва да има **точно една** default combination;
- `cache_default_attribute` трябва да сочи към същата combination;
- липсваща default combination блокира `QUALITY_PASS`;
- повече от една default combination блокира `QUALITY_PASS`;
- existing correct default combination е `PASS`, не blocker;
- M99 не променя default combination без доказана причина или operator policy.

---

## 24. Два отделни operational режима

M99 разделя процесите за **нови** и **съществуващи** продукти.

### 24.1 Selective New Product Import

Изборът на target channels се отнася **само за нови продукти**.

Операторът може да избере един или повече targets, например:

- само `medicinski-drehi.com`;
- само `laviro.ro` + `alviro.ro`;
- всички web channels;
- всички web channels + Dolibarr;
- Dolibarr only, когато конкретният workflow го изисква.

**DECIDED — M99 NEW PRODUCT SCOPE RULE**

Нито един new-product importer не приема всички channels по подразбиране.

```text
WRITE_TARGETS =
REQUESTED_TARGETS
∩ AUTHORIZED_TARGETS
∩ READY_TARGETS
```

Статуси по target:

- `NOT_SELECTED`
- `SELECTED`
- `UNAUTHORIZED`
- `BLOCKED`
- `READY`
- `COMPLETED`
- `FAILED`
- `QUALITY_INCOMPLETE`

`NOT_SELECTED` е различно от `BLOCKED`.

### 24.2 Daily Existing Product Sync

За вече въведените canonical products target selection от оператора **не управлява ежедневната синхронизация**.

Всеки ден M99 трябва да:

1. вземе всички canonical products с verified supplier/source mapping;
2. провери supplier price;
3. провери supplier availability;
4. провери variants/sizes;
5. провери discontinued/changed state;
6. сравни с последното verified състояние;
7. при `NO_CHANGE` да не прави write;
8. при промяна да синхронизира всички **вече съществуващи** channel/ERP mappings според ownership policy.

**Daily sync не създава продукт в channel, в който той не е бил въведен.**

Пример:

```text
M99 Product
  mela99.com              PRESENT
  medicinski-drehi.com    PRESENT
  laviro.ro               PRESENT
  alviro.ro               NOT_PRESENT
  rabotni-drehi.com       NOT_PRESENT
  Dolibarr                PRESENT
```

Daily sync работи върху Mela + Medicinski + Laviro + Dolibarr. Не създава автоматично Alviro или Rabotni.

### Change detection

Минимални резултати:

```text
NO_CHANGE
PRICE_CHANGED
AVAILABILITY_CHANGED
VARIANT_AVAILABILITY_CHANGED
PRODUCT_CHANGED
SUPPLIER_DISCONTINUED
VERIFICATION_FAILED
```

---

## 25. Product Presence Registry / Channel Availability

Всеки canonical M99 продукт трябва да може да отговори на въпроса:

> „В кой сайт/сайтове е въведен този продукт и къде не е въведен?“

Това е отделно от stock availability.

### Presence statuses

```text
NOT_PRESENT
PRESENT_DRAFT
PRESENT_TEST
PRESENT_ACTIVE
PRESENT_PAUSED
PRESENT_RETIRED
PRESENT_LAST_VERIFIED
UNKNOWN
VERIFICATION_FAILED
```

### Stock statuses

```text
IN_STOCK
OUT_OF_STOCK
PARTIAL_VARIANT_STOCK
SUPPLIER_AVAILABLE
SUPPLIER_UNAVAILABLE
UNKNOWN
```

**DECIDED — Presence != Stock.**

`NOT_PRESENT` означава продуктът не е въведен в channel-а.  
`OUT_OF_STOCK` означава продуктът е въведен, но няма наличност.

### Channel mapping matrix

Всеки ProductGroup трябва да може да пази/показва:

- channel;
- channel product ID;
- URL;
- presence status;
- publication status;
- last verified;
- last sync;
- stock status;
- variant mappings;
- price;
- currency;
- VAT/gross verification;
- sync ownership;
- verification error, ако има.

### Query modes

**FAST**

Отговаря от M99 Product Presence Registry / last verified state.

**LIVE VERIFY**

Проверява избраните channels/ERP в реално време.

При временен API/site failure доказано `PRESENT` не се превръща в `NOT_PRESENT`. Използва се:

```text
PRESENT_LAST_VERIFIED
LIVE_CHECK_FAILED
```

---

## 26. M99 Admin Panel — нова продуктова посока

След standalone importer/recovery фазата M99 трябва да се превърне в многопотребителски вътрешен web software.

Предложена следваща major линия:

**`M99 v0.7.0 — Admin Platform Foundation`**

UI трябва да е визуално и функционално близък до PrestaShop Back Office: ляво navigation меню, central work area, таблици, filters, badges, forms, actions и audit-aware workflows.

### Основно меню

```text
Dashboard

Catalog
 ├─ Products
 ├─ Product Groups
 ├─ Variants
 ├─ Categories
 ├─ Brands
 └─ Product Presence

Imports
 ├─ New Product Import
 ├─ Supplier Browser
 ├─ Import Jobs
 ├─ Sources / Suppliers
 └─ Import History

Synchronization
 ├─ Daily Price Sync
 ├─ Availability Sync
 ├─ Supplier Monitoring
 └─ Sync Errors

Channels
 ├─ mela99.com
 ├─ medicinski-drehi.com
 ├─ laviro.ro
 ├─ alviro.ro
 ├─ rabotni-drehi.com
 ├─ m99.eu
 └─ Dolibarr

CRM / ERP
 ├─ Customers
 ├─ Suppliers
 ├─ Dolibarr
 └─ Mappings

Quality
 ├─ Product Quality Gate
 ├─ Price + VAT Gate
 ├─ Default Combination Gate
 ├─ Image Gate
 ├─ Language Gate
 └─ Errors / Warnings

Users
 ├─ Users
 ├─ Roles
 ├─ Permissions
 └─ Audit Log

Settings
 ├─ Pricing
 ├─ VAT Rules
 ├─ Credentials
 ├─ Languages
 ├─ Import Presets
 └─ System
```

---

## 27. Authentication

M99 Admin Panel трябва да има собствена authentication система.

### Login

Потребителят влиза чрез:

- username **или**
- email;
- password.

### Security requirements

- password никога не се пази като plaintext;
- password hash с подходящ съвременен password hashing algorithm;
- session management;
- logout;
- failed login throttling / lockout policy;
- session timeout;
- audit на login/logout;
- reset-password workflow;
- възможност за 2FA в следващ етап;
- credentials за channels/suppliers не се показват на операторите.

---

## 28. Roles and Permissions / RBAC

Permissions не са само menu visibility. Те се прилагат server-side върху actions и targets.

Начални роли:

### M99_SUPER_ADMIN

- всички channels;
- Dolibarr;
- imports;
- daily sync;
- pricing;
- users;
- roles;
- system settings;
- audit;
- operator approval;
- configuration.

### CHANNEL_MANAGER

Може да управлява само изрично разрешените channels.

Пример за управител на `medicinski-drehi.com`:

```text
AUTHORIZED CHANNELS:
✓ medicinski-drehi.com

NEW PRODUCT IMPORT:
✓

CREATE/UPDATE TEST:
✓

GENERATE CONTENT:
✓

IMPORT IMAGES:
✓

IMPORT VARIANTS:
✓

PRICE UPDATE:
✓ according to approved policy

OTHER CHANNEL WRITE:
✗

DOLIBARR WRITE:
✗ unless separately granted

DELETE:
✗

SYSTEM SETTINGS:
✗

USERS:
✗
```

### OPERATOR

Подготовка, selection, preview, dry run и операторски задачи според granted permissions, без автоматични административни права.

### Отделни permissions

Примерни capabilities:

```text
product.read
product.create
product.update
product.activate
product.retire
product.delete_approve
import.create_job
import.execute
import.select_targets
supplier.browse
sync.view
sync.run_manual
pricing.view
pricing.approve
channel.<channel>.read
channel.<channel>.write
dolibarr.read
dolibarr.write
users.manage
roles.manage
settings.manage
audit.read
```

---

## 29. Supplier Browser / Direct Supplier Selection

Операторите трябва да могат да избират продуктите **директно от сайтовете на доставчиците**.

Основен модул:

**Suppliers → Browse & Import**

### Single Product

Операторът отваря продуктова страница при доставчика и избира:

```text
[ Импортирай този продукт ]
```

Това създава M99 Import Job. Не прави директен uncontrolled website write.

### Multi Product Selection

Операторът може да маркира няколко supplier products:

```text
✓ Product A
✓ Product B
✓ Product C

[ REVIEW SELECTION ]
[ CREATE IMPORT JOB ]
```

### Category / Multi-category Selection

Операторът отваря една или повече supplier categories и може да избере:

```text
( ) всички продукти
( ) първите 10
( ) първите 20
( ) само новите за M99
( ) избрани ръчно
```

### DECIDED — M99 DIRECT SUPPLIER SELECTION RULE

Операторът може да инициира new-product import от:

- exact supplier product page;
- множество selected supplier products;
- една supplier category;
- множество supplier categories.

Selection никога не заобикаля:

- identity resolution;
- evidence verification;
- duplicate/legacy matching;
- operator authorization;
- target scope;
- pricing/VAT;
- image gate;
- combination/default gate;
- language/content gate;
- Test/Draft policy;
- readback;
- Product Quality Gate.

---

## 30. Import Job като първокласен обект

Всеки new-product import се записва като `ImportJob`.

Минимален модел:

```text
job_id
created_at
created_by
operator_role

source_id
source_type
source_urls
source_categories

selected_products
product_count

requested_targets
authorized_targets
ready_targets
blocked_targets

pricing_policy
content_policy
image_policy
language_policy

dry_run
requires_confirmation

status
started_at
finished_at

result_per_product
result_per_target
audit_log
```

Пример:

```text
JOB: M99-IMPORT-20260817-0012
Operator: medicinski_manager
Source: Stenso
Selection: first 10 medical clothing products
Requested targets:
  medicinski-drehi.com
Authorized targets:
  medicinski-drehi.com

Result:
  10 preflight
   8 new products
   1 legacy match
   1 ambiguous/block
```

---

## 31. Import Presets

За често повтарящи се workflows M99 трябва да има presets.

Примери:

### MEDICINSKI / STENSO

```text
Source: Stenso
Target: medicinski-drehi.com
Mode: New products
Language: BG
Initial state: TEST/Draft
```

### PALLTEX / ALL CHANNELS + ERP

```text
Source: Palltex
Targets:
  mela99.com
  medicinski-drehi.com
  laviro.ro
  alviro.ro
  rabotni-drehi.com
  [m99.eu when enabled]
  Dolibarr
Mode: New product import
Pricing: channel policy
VAT: standard per market
```

Preset не може да даде права, които потребителят няма.

---

## 32. New Product Import Wizard

Предложен flow в Admin Panel:

```text
1. Source / Supplier
2. Browse / Select Products or Categories
3. Identity / Duplicate Review
4. Target Channels
5. Pricing + VAT
6. Content + Languages
7. Images
8. Variants + Default Combination
9. Preflight
10. Operator Confirmation
11. TEST / Draft Import
12. Readback
13. Quality Report
14. Publish/Activate according to permission
```

Channel manager вижда само targets, за които има право.

---

## 33. Daily Existing Product Sync Module

Dashboard модулът трябва да показва:

```text
Last run
Products checked
Supplier checks
Price changes
Availability changes
Variant changes
Channel writes
Dolibarr writes
NO_CHANGE count
Blocked count
Errors
```

Daily Sync не трябва да генерира unnecessary writes.

**DECIDED: NO_CHANGE → NO_WRITE.**

Price changes минават през:

```text
supplier price
→ approved pricing rule
→ market currency
→ standard VAT
→ target gross
→ platform NET if required
→ API write
→ readback
→ Front Office gross-price gate
```

---

## 34. Product Presence UI

Примерен Product detail tab:

```text
Cherokee Infinity CKE1124A Bordeaux
M99-1274366573
Supplier reference: 08001873
```

| Target | Presence | Publication | Product ID | Stock | Price | Last verified |
|---|---|---|---:|---|---:|---|
| mela99.com | PRESENT | TEST | 2459 | UNKNOWN | channel price | timestamp |
| medicinski-drehi.com | PRESENT | ACTIVE | 1225 | variant-aware | channel price | timestamp |
| laviro.ro | PRESENT | TEST/ACTIVE according to live state | 878 | variant-aware | RON gross | timestamp |
| alviro.ro | NOT_PRESENT / live status | — | — | — | — | timestamp |
| rabotni-drehi.com | PRESENT | DRAFT | 96801 | variant-aware | channel price | timestamp |
| Dolibarr | mapping state | operational | ID | physical stock | ERP price | timestamp |

Actions:

```text
[ LIVE VERIFY ALL ]
[ VERIFY SELECTED ]
[ OPEN CHANNEL PRODUCT ]
[ VIEW SYNC HISTORY ]
```

---

## 35. Dashboard — PrestaShop-style operational view

Dashboard трябва да е business-first.

Примерни cards:

```text
Canonical products
Products by channel
Products not mapped to Dolibarr
Products missing in selected channels

Today's supplier checks
Price changes
Availability changes
New supplier products

Requires attention:
  Price/VAT gate failures
  Missing default combination
  Image failures
  Language failures
  Supplier ambiguity
  Presence verification failures
  Daily sync failures
```

---

## 36. Web channels vs ERP targets

Dolibarr не е „още един сайт“.

### Web channel payload

Може да включва:

- product identity mapping;
- name;
- content;
- SEO;
- categories;
- images;
- variants;
- price;
- tax;
- publication state.

### Dolibarr payload

Може да включва:

- canonical M99 identity;
- supplier mapping;
- supplier reference;
- EAN/GTIN;
- cost/purchase data;
- selling price policy;
- variants;
- warehouse master data;
- stock ownership;
- product lifecycle;
- counterparties/mappings.

M99 orchestration engine използва target adapter според типа target.

---

## 37. Технологична посока за M99 v0.7.0

Предпочитана архитектура:

```text
Browser
  ↓
M99 Admin Panel
  ↓
M99 Application/API Layer
  ↓
M99 Canonical Database
  ↓
Services / Engines
  ├─ Identity
  ├─ Evidence
  ├─ Supplier Browser
  ├─ Import Jobs
  ├─ Pricing + VAT
  ├─ Content
  ├─ Images
  ├─ Variants
  ├─ Presence Registry
  ├─ Daily Sync
  ├─ Quality Gates
  └─ Audit
  ↓
Adapters
  ├─ Thirty Bees / PrestaShop
  ├─ WooCommerce
  ├─ Dolibarr
  └─ Supplier/B2B connectors
```

Python остава естествен backend избор, защото голяма част от доказаната integration logic вече е Python-based.

UI е отделен от конкретните магазини и не трябва да бъде PrestaShop module.

---

## 38. Browser Extension — по-късен етап

След стабилен Supplier Browser може да се добави browser extension/button.

Операторът е в нормален браузър върху supplier product page и избира:

```text
M99
[ Import this product ]
```

Extension изпраща URL/context към M99 Admin Panel и създава Import Job.

Това е **DEFERRED**, докато embedded/controlled Supplier Browser и Admin authorization не са стабилни.

---

## 39. Обновена класификация на операциите

От README v5 M99 има три ясно разграничени operational classes:

### A. NEW PRODUCT IMPORT

- operator initiated;
- supplier direct selection;
- target selection;
- authorization;
- TEST/Draft first;
- no assumption of all channels.

### B. EXISTING PRODUCT DAILY SYNC

- scheduled;
- all canonical products with supplier mappings;
- updates all existing channel/ERP mappings;
- no automatic creation in missing channels;
- NO_CHANGE → NO_WRITE.

### C. MANUAL / EXCEPTIONAL REPAIR

- controlled;
- exact target;
- exact allowed fields;
- explicit confirmation;
- mandatory readback;
- no broad side effects.

---

## 40. Нови README v5 normative rules

| ID | Правило | Статус |
|---|---|---|
| PRICE-001 | Target selling price е gross/VAT-included customer price | DECIDED/TESTED |
| VAT-001 | Standard VAT се чете от конкретния channel/market | DECIDED/TESTED |
| VAR-002 | Всеки variational product има точно една default combination | DECIDED/TESTED |
| VAR-003 | `cache_default_attribute` сочи към default combination | DECIDED/TESTED |
| FO-001 | Front Office gross-price verification е част от Product Quality Gate | DECIDED/TESTED |
| NEW-001 | Target selection се прилага за new-product imports | DECIDED |
| SYNC-001 | Existing canonical products се проверяват ежедневно | DECIDED |
| SYNC-002 | Daily sync обновява само existing mappings, не създава missing channel products | DECIDED |
| SYNC-003 | `NO_CHANGE → NO_WRITE` | DECIDED |
| PRES-001 | Presence и Stock са отделни dimensions | DECIDED |
| PRES-002 | Всеки ProductGroup има channel/ERP presence mapping | DECIDED |
| AUTH-001 | M99 Admin има username/email + password authentication | DECIDED |
| AUTH-002 | Server-side RBAC управлява actions и allowed targets | DECIDED |
| UI-001 | Admin UI следва PrestaShop-style Back Office interaction model | DECIDED |
| SUP-001 | Operator може да избира product(s)/category(ies) директно от supplier source | DECIDED |
| JOB-001 | Всяка new-product операция е auditable ImportJob | DECIDED |
| SCOPE-001 | Write = requested ∩ authorized ∩ ready | DECIDED |
| ERP-001 | Dolibarr е ERP target type, не web channel | DECIDED |

---

## 41. README / Repository governance към v5

В repository трябва да се запазят всички исторически README версии.

Желано състояние:

```text
README.md
README_v2.md
README_v3.md
README_v4.md
README_v5.md

docs/history/README_v1.md
docs/history/README_v2.md
docs/history/README_v3.md
docs/history/README_v4.md
docs/history/README_v5.md
```

`README.md` не се презаписва автоматично от v5 installer-а. Ако v5 трябва да стане GitHub landing README, това се прави с отделно operator-approved действие след проверка.

---

## 42. Следваща major milestone

**PROPOSED / NEXT: `M99 v0.7.0 — Admin Platform Foundation`**

Минимален първи vertical slice:

1. Authentication;
2. Users;
3. Roles / permissions;
4. Dashboard shell;
5. Product list;
6. Product Presence;
7. Supplier registry;
8. Supplier Browser / URL selection;
9. New Product Import Job;
10. target selection;
11. Stenso single-product import;
12. Stenso category import;
13. Daily Existing Product Sync framework;
14. Audit Log.

Първият реален user workflow трябва да позволи на channel manager:

```text
Login
→ Suppliers
→ Stenso
→ Browse medical clothing
→ open/select product(s) or category
→ Import
→ medicinski-drehi.com
→ Preflight
→ TEST/Draft
→ Quality Report
```

без PowerShell, Python или `.bat` interaction.

---

## 43. Обновена Definition of Success

### За оператор

Не е необходимо да знае Python, PowerShell, API или PrestaShop internals.

### За нов продукт

Операторът избира supplier product/category, M99 открива identity, показва targets според permissions и извършва controlled TEST/Draft import.

### За съществуващ продукт

M99 ежедневно проверява supplier truth и актуализира всички вече съществуващи mappings при реална промяна.

### За управлението

По всяко време може да се попита:

- къде е въведен продуктът;
- къде липсва;
- къде е active/draft/test;
- каква е последната verified цена;
- къде има stock;
- кога е синхронизиран;
- какъв е supplier status;
- кой operator/job е направил промяната.

### За качеството

Нито technical write, нито Back Office price, нито HTTP 200 са достатъчни сами по себе си.

`QUALITY_PASS` изисква всички приложими identity, evidence, content, image, variant/default, price/VAT, presence и readback gates.

---

**README v5 е отправната нормативна база за прехода от standalone importer scripts към M99 Admin Platform.**

