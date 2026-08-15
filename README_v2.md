# M99 Knowledge Platform — README v2

> **Втора, разширена версия на първоначалния README**  
> **Статус:** Master Project Documentation / Consolidated System Specification  
> **Консолидирано до:** v0.6.7.5 — Cherokee WW601 Real Product Publish  
> **Repository:** `M99-Knowledge-Platform`

---

## 0. За този документ

Този файл е **втора версия на първоначалния `README.md`**. Първият README постави фундаментите на M99 Knowledge Platform: Single Source of Truth, Knowledge First, No Duplicate Data, Evidence Based, AI Native и връзката на базата знания с онлайн магазини, ERP, CRM, SEO и бъдещи автоматизации.

След него проектът се разви значително. Бяха изяснени продуктова идентичност, ProductGroup lifecycle, evidence hierarchy, manufacturer/supplier matching, commercial quarantine, supplier intelligence, pricing, multilingual content, SEO/AEO/GEO, изображения, variants, six-site publishing, Dolibarr ERP/CRM, MoneyWorks migration, controlled write/readback, secrets architecture и реален product-publish pilot.

**Целта на README v2 е да бъде техническата памет на проекта.** Той не е маркетингово резюме, а master overview и operational specification.

### Статуси на решенията

- `DECIDED` — изрично прието правило.
- `IMPLEMENTED` — присъства в код/config/script.
- `TESTED` — доказано чрез unit/regression/live GET/preview/readback.
- `OPEN DECISION` — обсъждано, но без окончателен contract.

Никое `OPEN DECISION` не трябва да се представя като окончателно правило.

---

## 1. Визия

M99 Knowledge Platform е корпоративна knowledge/product platform за групата M99.

Основният принцип е:

> **Един продукт се разбира и описва правилно веднъж, след което проверената продуктова истина се използва навсякъде.**

Платформата трябва да захранва:

- онлайн магазини;
- ERP;
- CRM;
- складови процеси;
- AI агенти;
- SEO и AEO;
- marketing automation;
- продуктови каталози;
- supplier intelligence;
- pricing engine;
- migration tooling;
- бъдещи вътрешни приложения.

---

## 2. Бизнес контекст

M99 развива e-commerce за работно облекло, медицинско облекло, защитни обувки, инструменти, консумативи и индустриални стоки, както и услуги чрез `toplinka.com`.

Стратегически цели, които системата трябва да подпомага:

- международно развитие;
- България + Румъния;
- минимален административен headcount;
- максимална автоматизация;
- подобрен cash flow;
- намаляване на slow-moving stock;
- систематизиран план за 1 / 3 / 5 / 10 години;
- цел за приблизително 10 000 EUR чиста месечна печалба;
- „M99 Group Master Plan 2036“ като жива система.

### Настоящ оперативен приоритет

Сайтовете губят темпо, когато продуктите, цените и съдържанието не са актуални. Затова непосредственият приоритет е:

```text
PRODUCT ACQUISITION
→ PRODUCT VERIFICATION
→ PRICING
→ CONTENT
→ IMAGES
→ VARIANTS
→ DRAFT PUBLISH
→ READBACK
→ OPERATOR REVIEW
→ ACTIVATION
```

Infrastructure, която не блокира продуктовия pipeline, е вторична в текущия етап.

---

## 3. Core Principles

### 3.1 Single Source of Truth

Всеки canonical факт трябва да се съхранява веднъж и да се използва навсякъде.

### 3.2 Knowledge First

Първо се изграждат проверени знания. От тях се генерират Product Master, descriptions, SEO, FAQ, ERP/CRM records и channel payloads.

### 3.3 No Duplicate Data

Технологии, материали, стандарти и product facts трябва да бъдат reusable entities, а не копирани независими текстове.

### 3.4 Evidence Based

Приоритет на evidence:

```text
1. Exact official manufacturer product
2. Official manufacturer documentation / catalog / certificate
3. Exact proven supplier/distributor product
4. Проверени M99/channel data
5. M99 Expert / operator
6. AI — само върху доказани данни
```

Search pages, category pages и image assets са discovery evidence, не автоматично product/commercial truth.

### 3.5 AI Native, не AI Invented

AI може да извлича, структурира, сравнява, превежда, адаптира и генерира. Не може да измисля technical facts, standards, stock или commercial claims.

---

## 4. Canonical M99 Product Architecture

Channel product в PrestaShop/Thirty Bees/WordPress не е master. Supplier page също не е master. Manufacturer page е authoritative evidence, но не е M99 record.

Canonical layer е:

```text
M99 ProductGroup
```

Целевата структура е:

```text
ProductGroup
 ├─ canonical identity
 ├─ manufacturer identity
 ├─ facts
 ├─ evidence/provenance
 ├─ colour identity
 ├─ supplier mappings
 ├─ commercial observations
 ├─ assets
 ├─ channel mappings
 └─ variants
     ├─ size
     ├─ barcode/EAN
     ├─ supplier variant
     ├─ stock
     └─ channel combination
```

---

## 5. ProductGroup lifecycle

`DECIDED`

```text
draft → active → paused → retired
```

Изтриването остава възможно, но **само след operator approval и изрично ръчно действие `DELETE`**.

Автоматична система няма право да изтрива ProductGroup само защото supplier page липсва, продуктът временно не е намерен или scraper/matcher е върнал грешка.

---

## 6. M99 Identity и номерация

M99 identity трябва да е независима от manufacturer SKU, supplier ref, Dolibarr ID, PrestaShop ID, WordPress ID и legacy MELA references.

По време на разработката са използвани/обсъждани формати:

```text
M99-PM-000001
M99 000001
M99 100002
M99 100017
```

Има migration concept:

```text
current_internal_id: M99-PM-000001
target_m99_id:       M99 000001
preserve_current_alias: true
```

### Immutable identity

`DECIDED PRINCIPLE`

След окончателно присвояване M99 ID не трябва да се използва за друг ProductGroup, дори първият да стане `retired` или бъде изтрит след approval.

### Финален numbering algorithm

`OPEN DECISION`

Преди mass production трябва да се фиксират:

- един финален canonical format;
- sequence storage;
- atomic reservation;
- collision handling;
- ProductGroup ID vs Variant SKU;
- human-readable reference.

До това решение системата не трябва да измисля нов формат самостоятелно.

---

## 7. Product, Colour и Variant

Размерите на един модел/цвят са variants, не независими ProductGroups, когато продуктова логика не налага друго.

Пример:

```text
Cherokee WW601 Navy
 ├─ 2XS
 ├─ XS
 ├─ S
 ├─ M
 ├─ L
 ├─ XL
 └─ 2XL
```

### Colour model

Трябва да се различават:

```text
manufacturer_colour
supplier_colour_alias
canonical_colour
localized_colour
```

Пример:

```text
canonical/manufacturer: NAVY
supplier aliases: NAVY / DARK BLUE
BG: тъмносин
EN: Navy
RO: bleumarin
RU: тёмно-синий
```

### ProductGroup vs colour variant

`OPEN DECISION`

Не е окончателно решено дали различните цветове на един style винаги са отделни ProductGroups или colour variants. Решението може да бъде category-specific. До окончателен standard автоматичен merge на различни цветове не се разрешава.

### Size fields

Минимум:

```text
size_system
size_code
display_label
sort_order
manufacturer_size
supplier_size
channel_size
barcode/EAN if available
```

Видим size selector не доказва stock.

---

## 8. Manufacturer Evidence

Manufacturer е authoritative за:

- model/style;
- manufacturer item/MPN;
- material;
- technology;
- construction;
- protection class;
- standards/certifications;
- official colour;
- dimensions;
- official size range.

Manufacturer facts имат приоритет пред supplier marketing text.

---

## 9. Supplier Intelligence

Основни обсъждани/използвани източници:

- `stenso.net`
- `palltex.bg`
- `feya.bg`
- `teniskinaedro.com`
- `bult.bg`
- `calenda.bg`
- `toolsshop.bg`
- `euromasterbg.com`
- `viking-t.bg`
- VVM
- Bultex B2B
- Diadora Utility
- Puma Safety
- Cherokee

Supplier може да предостави:

- supplier reference;
- exact price;
- local naming;
- visible sizes;
- current stock, когато е доказан;
- market terminology;
- useful product facts;
- product images.

---

## 10. Supplier Match States

Разработката използва състояния като:

```text
EXACT
VERY_STRONG
NEAR_MATCH
SAME_MODEL_WRONG_COLOUR
DISCOVERY_ONLY
REJECT
```

`DECIDED + TESTED`: не всеки match може да захранва commercial data.

При mismatch по manufacturer item, protection class или colour:

```text
auto_merge_allowed = false
commercial_data_usable = false
pricing_eligible = false
availability_eligible = false
```

Пример: official Diadora S1PS срещу supplier S3S near-match не се auto-merge-ва и supplier price/stock не се използват за S1PS продукта.

---

## 11. Search / Category / Image Noise Filter

`IMPLEMENTED / TESTED`

```text
SEARCH_PAGE   → DISCOVERY_ONLY
CATEGORY_PAGE → DISCOVERY_ONLY
IMAGE_ASSET   → DISCOVERY_ONLY
WRONG_COLOUR  → NO COMMERCIAL EVIDENCE
EXACT_PRODUCT → COMMERCIAL EVIDENCE ELIGIBLE
```

Това правило възникна след Cherokee supplier discovery, където search/pagination/sorting URLs даваха много несвързани цени.

---

## 12. Supplier Descriptions

`DECIDED`

Когато supplier product е exact, неговото описание може да се използва като market evidence за локална терминология, naming и practical customer language.

**Supplier prose не се копира verbatim.** M99 генерира оригинално content, базирано на доказаните manufacturer + supplier facts.

---

## 13. Pricing Engine

### Current primary supplier rule

За текущия Cherokee workflow:

```text
PRIMARY_SUPPLIER = stenso.net
```

`DECIDED`:

```text
M99 selling price = exact Stenso selling price - 1.3%
M99 selling price = Stenso × 0.987
```

### EUR/BGN

```text
1 EUR = 1.95583 BGN
```

### Cherokee WW601

Доказана Stenso цена:

```text
25.20 EUR
```

Изчисление:

```text
25.20 × 1.95583 = 49.286916 BGN
49.286916 × 0.987 = 48.646186092 BGN
FINAL = 48.65 BGN
```

### Critical parsing lesson

`97.79 BGN`, видяно на Cherokee Stenso page, не е product price. То е BGN equivalent на free-delivery threshold 50 EUR.

Следователно parser не трябва да избира произволно currency число от HTML.

### Price safety rules

- exact target product only;
- raw supplier price се пази;
- raw currency се пази;
- observed_at timestamp;
- conversion only once;
- discount only once;
- final rounding;
- no silent update при ambiguous price.

---

## 14. Stock

Видим размер ≠ наличност.

Stock трябва по възможност да бъде variant-aware:

```text
ProductGroup → Variant → Supplier/Warehouse
```

Пример:

```text
WW601 Navy M  = 4
WW601 Navy L  = 2
WW601 Navy XL = 0
```

Никое описание не трябва да твърди „налично“, ако live evidence не го доказва.

---

## 15. Images / Assets

Legacy Apify/OpenAI script вече е съдържал image pipeline:

```text
resize target: 1200 × 1200
format: WEBP
quality: 85
```

По-късният target е приблизително 1200–1400 px на long edge.

Rules:

- preserve aspect ratio;
- no factual alteration;
- prefer clean manufacturer assets;
- exact supplier assets may be used when appropriate;
- deduplicate;
- intentional main image order;
- localized ALT;
- unique ALT by view;
- no keyword stuffing.

---

## 16. M99 Content / SEO / AEO Quality Standard

Product page трябва да поддържа, когато channel позволява:

- Product Name;
- exactly one H1;
- meaningful H2/H3 hierarchy;
- Meta Title;
- Meta Description;
- short description;
- long description;
- technical specifications;
- FAQ;
- ALT;
- schema/structured data;
- internal links;
- URL/canonical logic;
- variants;
- commercial fields.

### H1

Exactly one primary H1. Трябва да отразява canonical identity и primary search intent естествено.

### H2/H3

Практическа цел за complete page: обикновено 4–7 meaningful H2. Cherokee full-content test използва 6 H2. H3 е за genuine subsections, technologies и FAQ.

### Meta Title

Работна QA guideline: приблизително 50–60 characters, когато е естествено. Unique, product-specific, localized.

### Meta Description

Работна QA guideline: приблизително 140–160 characters, когато е естествено. Никакви unverified stock/discount claims.

### Short description

Ориентир: 50–100 думи с най-полезните differentiators.

### Long description

За стратегически важни продукти ориентир: 400–700+ думи, но без padding. Количеството текст следва количеството доказана полезна информация.

### FAQ

Ориентир: 4–8 useful questions. Cherokee canonical preview използва 6, а по-късен QA implementation отчита H3/FAQ около 8.

### Real QA evidence

При Cherokee v0.6.7.4.2 full content preview channel/language резултатите бяха от типа:

```text
H1 = YES
H2 = 6
H3/FAQ = 8
ALT = 5
SCORE = 97
```

Това е реален project benchmark, не задължителна еднаква числова стойност за всеки продукт.

---

## 17. Content Claim Taxonomy

Използвани категории:

```text
FACT
DERIVED_SAFE_CLAIM
MARKETING_CLAIM
UNSUPPORTED_CLAIM
```

Policy:

```text
FACT               → allowed
DERIVED_SAFE_CLAIM → allowed
MARKETING_CLAIM    → review/evidence required
UNSUPPORTED_CLAIM  → blocked
```

Примери за safe derivation:

```text
low-top product type → low-cut construction
breathable mesh upper → breathable upper
removable insole → removable insole claim
```

---

## 18. Technical Specifications

Публикуват се само приложими, доказани fields, например:

```text
Brand
Collection
Model / Style
Manufacturer Item / MPN
Supplier Reference
Colour
Material
Fit
Dimensions
Product Type
Protection Class
Standards
ESD
Toe Cap
Anti-puncture
Fabric
Pockets
Lining
Insole
Midsole
Outsole
Width
Size range
```

EU norms/standards никога не се infer-ват само от category.

---

## 19. SEO / AEO / GEO

SEO се оценява като система, не като keyword density:

- identity consistency;
- search intent;
- unique metadata;
- heading structure;
- entity coverage;
- factual completeness;
- schema;
- internal linking;
- image metadata;
- URL stability;
- duplicate content;
- language quality;
- commercial consistency.

AEO/GEO цел:

- explicit identity;
- clear factual sentences;
- structured attributes;
- concise FAQ;
- consistent model/MPN/SKU entities;
- evidence-backed claims;
- no contradictions.

Целта е retrievability и trustworthiness, не manipulation на AI recommendations.

---

## 20. Benchmark Framework

### Global commerce

```text
Amazon
Zalando
eBay
```

Сравняваме information hierarchy, scanability, variants, images, specification clarity и buying information.

### Product storytelling / information design

```text
Apple
```

Сравняваме clarity, hierarchy, concise benefits и low-noise presentation.

### Manufacturer truth

Official exact manufacturer page/documentation е benchmark за factual accuracy. Използвани examples: Diadora Utility, Puma Safety, Cherokee.

### Local market

```text
Stenso
Palltex
+ category-specific competitors
```

Сравняваме terminology, assortment, price positioning, category structure, sizes и customer-facing information — без копиране на prose.

### Search benchmark

Най-силните текущо ranking relevant pages по country/language/query трябва да се откриват динамично. Няма вечен hardcoded „SEO winner“.

---

## 21. Channel Differentiation

Техническите facts могат да са еднакви, но prose не трябва да е механично duplicate между собствените сайтове.

Има `Channel duplication guard`; при v0.6.7.4.3 резултатът е `PASS`.

---

## 22. Language Policy

`DECIDED`

Български канали:

```text
BG + EN + RU
```

Румънски канали:

```text
RO + EN
```

Всеки language document трябва да е natural localization, не literal translation.

---

## 23. Channel Matrix

| Channel | Platform / family | Languages | Notes |
|---|---|---|---|
| `mela99.com` | Thirty Bees / PrestaShop Webservice family | BG / EN / RU | Primary BG channel, hidden review/Test workflow |
| `m99.eu` | WordPress | BG / EN / RU | Professional/international profile |
| `rabotni-drehi.com` | WordPress | BG / EN / RU | Separate descriptions from mela99.com |
| `medicinski-drehi.com` | PrestaShop 1.7.8.11 | BG / EN / RU | Medical clothing |
| `laviro.ro` | PrestaShop 1.6.1.24 | RO / EN | Romania |
| `alviro.ro` | Thirty Bees 1.1.x | RO / EN | Romania |

### mela99.com historical category facts

- ранна hidden Test category: ID 938;
- later live Test category discovery: ID 93, inactive;
- early API creation succeeded;
- early recurring error: `Property Product->link_rewrite is empty` / code 84;
- later fixed with multilingual `link_rewrite`.

---

## 24. Publishing Engine

Canonical workflow:

```text
Manufacturer
+
Exact Supplier
↓
Identity Resolution
↓
Evidence Merge
↓
Canonical ProductGroup
↓
Pricing
↓
Content
↓
Images
↓
Variants
↓
Channel Payload
↓
WRITE_DRAFT
↓
Readback
↓
Operator Review
↓
Activation
```

---

## 25. GET-only, DRY_RUN и WRITE_DRAFT

Development използва последователни safety layers.

### GET-only

```text
HTTP policy: GET ONLY
WRITE ALLOWED: NO
```

За live audits, category/product discovery, supplier extraction и previews.

### DRY_RUN

```text
Mode: DRY_RUN
Write attempted: NO
```

### WRITE_DRAFT

Първият real write е non-public:

```text
PrestaShop / Thirty Bees: active = 0
WordPress: status = draft
```

### Partial success

`DECIDED` за all-sites operation:

```text
ALL SITES REQUIRED: YES
PARTIAL SUCCESS ACCEPTED: NO
```

---

## 26. Readback / Update Guards

След write системата трябва да fetch-не продукта обратно и да провери поне:

- ID;
- reference;
- active/status;
- price;
- important written fields.

При update на existing product established URL/slug трябва да се пази, освен ако има explicit migration. Controlled publish вече е използвал:

```text
URL/slug update: LOCKED / KEEP
```

---

## 27. Categories / Review Workflow

Target pattern:

```text
canonical product
→ channel draft/inactive
→ review category where applicable
→ operator inspection
→ correction
→ activation
```

Existing valid categories се пазят при update, освен при approved migration.

---

## 28. Existing Product Audit — 2076 vs 2100

Беше направен live full-parameter audit.

### Product 2076

Observed:

- reference `MELA-REF`;
- active 0;
- 9 images;
- 6 combinations;
- very short content;
- no H1/H2/H3;
- no FAQ.

### Product 2100

Observed:

- missing reference;
- active 1;
- 9 images;
- 6 combinations;
- stronger description;
- FAQ;
- still no proper H1/H2/H3.

### Conclusion

Няма един `global winner`.

Canonical build трябва да избира **най-доброто доказано поле по поле**, а не сляпо да фаворизира целия legacy record.

---

## 29. Diadora Canonical Example

Canonical example:

```text
GLOVE A.BOX LOW PRO S3S
manufacturer item: 701.183119_80013
```

Manufacturer-backed facts включват BLACK, S3S, aluminium 200 J toe cap, K SOLE, ESD и A.Box System.

Този case установи separation между canonical identity, container product, commercial values, images/combinations и regenerated content.

---

## 30. Cherokee WW601 Pilot

Canonical identity:

```text
Brand: Cherokee
Collection: WW Revolution
Style: WW601
Supplier alias: WWE601
Manufacturer item: CK-WW601--
Colour: Navy
```

Manufacturer name:

```text
Women's 2-Pocket Sweetheart V-Neck Scrub Top
```

Manufacturer facts:

- 78% polyester;
- 20% rayon;
- 2% spandex;
- Missy relaxed fit;
- 26-inch center-back length;
- curved V-neckline;
- short sleeves;
- 2 front patch pockets;
- instrument loops;
- mesh side panels;
- shirttail hem;
- silky stretch twill.

Exact Stenso record:

```text
Supplier reference: 08001931
Alias: WWE601
Colour: Navy
```

Observed visible sizes:

```text
2XS XS S M L XL 2XL
```

Wrong-colour Grey/Black same-model pages са отделени от exact target; search/category/image pages са discovery-only.

---

## 31. Cherokee Multilingual Content

Generated languages:

```text
BG EN RU RO
```

Channel mapping:

```text
mela99.com             BG EN RU
m99.eu                 BG EN RU
rabotni-drehi.com      BG EN RU
medicinski-drehi.com   BG EN RU
laviro.ro              RO EN
alviro.ro              RO EN
```

Supplier verbatim copy: `NO`.

---

## 32. Cherokee Current Commercial Rule

```text
Stenso exact price: 25.20 EUR
M99 final:          48.65 BGN
```

при:

```text
EUR/BGN = 1.95583
M99 = Stenso - 1.3%
```

---

## 33. v0.6.7.5 — Real Product Publish

Target runtime:

```text
1. Fetch exact Stenso page
2. Verify WWE601 / 08001931
3. Extract exact EUR price
4. EUR → BGN
5. Apply -1.3%
6. Price guard
7. Extract sizes
8. Extract images
9. Generate/localize content
10. Create/update channel product
11. Upload assets
12. Draft/inactive
13. Readback
14. Audit
```

Planned exact confirmation:

```text
PUBLISH_DRAFT ALL_SITES CHEROKEE WW601 NAVY 48.65 BGN
```

---

## 34. Dolibarr — Role in Architecture

Dolibarr е избран за CRM, след което да бъде разширен към ERP/warehouse/accounting processes.

M99 Knowledge Platform остава canonical product truth. Dolibarr е operational representation.

```text
M99 canonical product
→ Dolibarr operational product/variant
```

Dolibarr не трябва независимо да измисля canonical identity.

---

## 35. Dolibarr Product / Variant Model

Target operational example:

```text
Parent/family:
Cherokee WW601 Navy

Variants:
2XS, XS, S, M, L, XL, 2XL
```

Обсъждан example SKU pattern:

```text
M99-CHEROKEE-WW601-NAVY
M99-CHEROKEE-WW601-NAVY-2XS
M99-CHEROKEE-WW601-NAVY-XS
M99-CHEROKEE-WW601-NAVY-S
...
```

`OPEN DECISION`: това е логичен пример, но универсалният final Variant SKU standard още трябва да се фиксира.

---

## 36. Dolibarr Warehouse

Реален проблем, разглеждан в проекта:

> след sale + expedition физическата stock quantity не се намаляваше както се очаква.

Target process:

```text
Supplier order
→ reception
→ physical stock increase

Customer order
→ shipment / configured stock event
→ physical stock decrease
```

Exact Dolibarr trigger/settings трябва да се валидират спрямо конкретната инсталация.

Stock трябва да е variant-aware, не само parent quantity.

---

## 37. Supplier Commercial Data in ERP

За supplier relationship трябва да могат да се пазят:

```text
Supplier
Supplier SKU
Supplier Price
Currency
VAT state
Observed At
Availability
Lead Time
Primary/Secondary Supplier
```

---

## 38. Dolibarr CRM

Първоначалният CRM workflow:

```text
Първо обаждане
→ Оферта
→ Второ обаждане
```

Desired:

- event templates;
- automatic follow-up points;
- reminders;
- customer history;
- relationship between customer, offer, order, invoice.

Срещани configuration issues:

- only `manual event`;
- липсващи desired call/offer event types;
- `main_use_advanced_event` issue.

---

## 39. MoneyWorks / CSV Migration

В проекта са подавани data files за:

- products;
- suppliers;
- customers;
- prices/relationships.

Migration requirement:

```text
source inspection
→ normalization
→ deduplication
→ identity mapping
→ supplier/customer mapping
→ dry run
→ import
→ reconciliation
→ audit
```

Имало е реални Dolibarr CSV test imports към `llx_product` с Puma test records.

---

## 40. AI SEO Assistant

Трябва автоматично да може да генерира:

- SEO title;
- Meta Description;
- H1;
- full descriptions;
- FAQ;
- ALT;
- blog articles;
- product comparisons;
- translations.

---

## 41. AI Marketing Assistant

Desired automation:

- Facebook;
- LinkedIn;
- Instagram;
- email campaigns;
- site news;
- new-product communication.

---

## 42. M99 Style Guide / Knowledge Base

M99 Style Guide трябва да определя tone, terminology, factuality, structure, forbidden filler, localization и channel differentiation.

M99 Knowledge Base е фундаментът за SEO, marketing, product generation, supplier intelligence и future agents.

---

## 43. Legacy Apify + OpenAI Pipeline

Legacy script използва Apify + OpenAI + HTML extraction + image processing + direct PrestaShop API.

Той е valuable prior art, но новата архитектура добавя:

- evidence;
- canonical identity;
- matching guards;
- provenance;
- readback;
- channel-specific content;
- controlled writes.

Target end-state:

```text
Extract
→ Normalize
→ Resolve Identity
→ Merge Evidence
→ Generate Content
→ Translate
→ Process Images
→ Calculate Price
→ Publish API
```

Normal product publishing трябва да е direct API, не CSV. CSV остава подходящ за migration/import scenarios.

---

## 44. Supplier Refresh

Желаната първоначална cadence за supplier/manufacturer scraping е weekly.

Price/stock може в бъдеще да има по-честа cadence, ако business need го изисква.

---

## 45. Historical Test Stock Quantity

В ранни тестове е използвана/обсъждана default quantity `30 pcs`.

Това е **test history**, не production stock rule. Реалният stock не трябва да се измисля като 30.

---

## 46. PrestaShop Writable Schema

По време на controlled write се установи safer approach:

```text
GET live blank/writable schema
→ fill supported fields
→ write
```

вместо произволно да се конструира XML без awareness за конкретната PrestaShop/Thirty Bees версия.

---

## 47. Credentials и Security

API keys/passwords:

- не се commit-ват;
- не се логват;
- не се показват в reports/screenshots;
- не се държат в plaintext tracked files.

Six-site readiness проверяваше API root, languages, categories, product lookup/schema и WordPress REST/auth routes.

Проблемите с многократно console credential input доведоха до design за Central Secrets.

---

## 48. M99 Central Secrets Architecture

Design candidate:

```text
HashiCorp Vault KV v2
```

Goals:

- six channel credentials entered once;
- use from multiple authorized computers;
- central rotation;
- revocable machine access;
- no Git secrets;
- redacted status/logs.

### Production Vault status

`DEFERRED / OPEN`

Production deployment беше отложен, защото immediate priority е real product publishing.

Никоя documentation не трябва да обещава „невъзможно за хакване“. Целта е least privilege, TLS, revocation, short-lived auth и minimal blast radius.

---

## 49. Testing Philosophy

Regression suite расте с проекта. По milestones са наблюдавани 58, 98, 143, 200, 206, 216, 220, 222 и 225 tests.

Target validation flow:

```text
compile
→ unit tests
→ regression
→ product-specific tests
→ live GET audit
→ prewrite
→ controlled write
→ readback
→ operator QA
```

Нов feature не трябва да чупи вече приет guardrail.

---

## 50. Audit Outputs

Operational scripts записват JSON/TXT artifacts в `output/`, например:

- product audit;
- supplier evidence;
- canonical build;
- content preview;
- readiness;
- publish audit;
- readback.

Output file е audit evidence, не canonical truth сам по себе си.

---

## 51. Git / Update Workflow

Working repository:

```text
C:\Users\user\Documents\GitHub\M99-Knowledge-Platform
```

Typical installer flow:

```text
check working tree
→ git pull --ff-only
→ copy payload
→ compile/tests
→ git add
→ commit
```

Documentation updates могат умишлено да останат uncommitted до visual review.

Windows `LF → CRLF` warnings сами по себе си не са functional failure.

---

## 52. Operator Gates

Operator review е required при:

- identity conflict;
- wrong-colour match;
- price ambiguity;
- tax ambiguity;
- reference migration;
- destructive merge;
- delete;
- activation;
- high-impact category/variant change.

`DELETE` винаги остава explicit human action.

---

## 53. Business / Automation Principles

Automation трябва да намалява manual work по:

- product content;
- translation;
- price checks;
- image formatting;
- multi-site entry;
- supplier monitoring;
- repetitive CRM follow-up.

Critical approval остава при operator.

Knowledge Platform е технологична основа за по-широкия `M99 Group Master Plan 2036`.

---

## 54. Immediate Roadmap

```text
1. Cherokee WW601
2. Real controlled draft publication
3. Visual/operator QA
4. Fix only observed real defects
5. 10–20 product batch
6. Repeatable bulk workflow
7. Automated supplier refresh
8. Scale categories
```

Временно secondary:

- production Vault;
- non-blocking infrastructure refactors;
- ERP improvements, които не пречат на product publishing.

---

## 55. Definition of Success — Cherokee Pilot

Cherokee WW601 е успешен, когато има:

- correct canonical identity;
- manufacturer-backed facts;
- exact supplier mapping;
- correct price;
- correct currency handling;
- localized channel-specific content;
- correct images;
- size variants;
- no invented stock;
- draft/inactive state;
- successful API readback;
- correct product visible to operator.

---

## 56. Definition of Success — Bulk Workflow

След single-product validation, 10–20 products трябва да могат да преминат през същия pipeline без custom code changes за всеки product.

---

## 57. Open Decisions Register

Теми, които не трябва да се представят като окончателно решени:

1. final M99 numbering scheme;
2. ProductGroup vs colour-variant boundary;
3. universal Variant SKU standard;
4. exact Dolibarr parent/variant implementation;
5. exact Dolibarr stock-decrease settings;
6. live currency policy per channel;
7. tax mapping per channel;
8. final category mapping strategy;
9. exact WordPress commerce API implementation per WP store;
10. production Vault deployment;
11. image rights/source policy per supplier/manufacturer;
12. auto-activation after draft/readback;
13. price refresh frequency;
14. stock refresh frequency.

---

## 58. Normative Critical Gates

Product activation остава blocked при failure на critical gate:

```text
IDENTITY_VALID
MANUFACTURER_EVIDENCE_VALID
SUPPLIER_MATCH_VALID when supplier commercial data is used
PRICE_VALID
CURRENCY_VALID
LANGUAGES_VALID
CONTENT_VALID
H1_VALID
META_VALID
TECHNICAL_FACTS_VALID
IMAGES_VALID
VARIANTS_VALID
NO_INVENTED_CLAIMS
NO_UNVERIFIED_STOCK
READBACK_VALID
```

Numeric quality score не може да override-не failed critical gate.

---

## 59. Historical Evolution / Important Milestones

### Foundation

- original README;
- Knowledge Base = Single Source of Truth;
- evidence hierarchy;
- repository structure.

### v0.5.x

- MoneyWorks migration work;
- Dolibarr adapter/import work;
- identity/catalog/optimization guardrails;
- M99 ID migration concepts.

### v0.6.2–v0.6.3

- manufacturer exact evidence;
- supplier near-match blocking;
- existing-product discovery;
- channel content/SEO preview;
- publication blocked until identity/existing-product review.

### v0.6.6.x

- controlled publish;
- DRY_RUN;
- WRITE_DRAFT;
- writable schema;
- review category policy;
- readback guards;
- live product audit.

### v0.6.6.4.3 / v0.6.6.4.4

- 2076 vs 2100 full parameter audit;
- canonical master build preview;
- field-by-field canonical selection.

### v0.6.7.0

- Cherokee WW601 product discovery direction;
- multilingual expansion policy.

### v0.6.7.1–v0.6.7.1.4

- multi-source supplier intelligence;
- direct supplier page extraction;
- robust discovery;
- noise filter;
- launcher repair.

### v0.6.7.2

- manufacturer + supplier evidence merge;
- canonical Cherokee identity.

### v0.6.7.3.x

- supplier market enrichment/content logic refinements and hotfixes.

### v0.6.7.4 / v0.6.7.4.2

- multilingual canonical content;
- full descriptions;
- H1/H2/FAQ/ALT quality scoring.

### v0.6.7.4.3–v0.6.7.4.5

- all-sites channel-specific package;
- no partial success;
- real WRITE_DRAFT adapters;
- six-site readiness.

### v0.6.7.4.5.1

- Central Secrets architecture.

### v0.6.7.5

- Cherokee WW601 Real Product Publish;
- exact Stenso price rule;
- 48.65 BGN price candidate;
- real controlled product-write milestone.

---

## 60. README v1 → README v2

README v1 постави фундаментите:

- Vision;
- Mission;
- Single Source of Truth;
- Knowledge First;
- No Duplicate Data;
- Evidence Based;
- AI Native;
- initial repository structure and roadmap.

README v2 не отменя тези принципи. Той ги **разширява с всички натрупани operational и architectural решения до текущия milestone**.

README v2 трябва да бъде актуализиран при всяко значимо решение:

```text
Decision
→ Code/Config
→ Tests
→ Changelog
→ README v2 / specialized docs
```

---

## 61. Recommended Specialized Documentation

README v2 остава master map, а детайлите могат да се развиват в:

```text
docs/
  IDENTITY_AND_NUMBERING.md
  PRODUCT_VARIANTS_COLOURS_SIZES.md
  EVIDENCE_ENGINE.md
  SUPPLIER_INTELLIGENCE.md
  PRICING_ENGINE.md
  CONTENT_SEO_AEO.md
  IMAGES_ASSETS.md
  CHANNEL_PUBLISHING.md
  DOLIBARR_ERP_WAREHOUSE.md
  DOLIBARR_CRM.md
  MONEYWORKS_MIGRATION.md
  SECURITY_AND_SECRETS.md
  TESTING_QA_AUDIT.md
  ADR/
```

Specialized docs не трябва да противоречат на master decisions в README v2.

---

## 62. Final Design Philosophy

M99 Knowledge Platform не е просто scraper, translator, SEO generator, ERP bridge или uploader.

Тя е единна система:

```text
KNOWLEDGE
+ EVIDENCE
+ IDENTITY
+ COMMERCIAL INTELLIGENCE
+ CONTENT
+ ERP / CRM
+ MULTI-CHANNEL PUBLISHING
+ AUDIT
```

Основната формула е:

```text
PRODUCT TRUTH ONCE
→ VERIFIED EVIDENCE
→ CANONICAL M99 RECORD
→ CHANNEL-SPECIFIC REPRESENTATION
→ EVERY STORE
→ ERP / CRM / AI
```

Следващият значим резултат не е още един preview, а **актуален, правилно структуриран и проверен продукт, реално създаден в M99 каналите и готов за операторско активиране**.

---

**M99 Knowledge Platform — README v2 — Product truth once. Verified everywhere.**
