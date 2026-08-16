# M99 Knowledge Platform — README v4

> **Master System Constitution / Consolidated Project Specification**  
> **Статус:** работен нормативен master документ  
> **Консолидирано:** README v1 + README v2 + README v3 + развитието до 16.08.2026 г.  
> **Repository:** `M99-Knowledge-Platform`

---

## 0. Роля на този документ

README v4 е четвъртата консолидирана версия на техническата памет на M99. Той наследява README v1, v2 и v3 и не отменя валидните им решения. Целта му е новият код да продължава от вече доказаното състояние, вместо проектът да се връща към стари или отхвърлени решения.

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

**README v4 — consolidated through 16.08.2026.**
