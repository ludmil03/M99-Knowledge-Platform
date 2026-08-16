# M99 Knowledge Platform — README v3

> **Master System Constitution / Consolidated Project Specification**  
> **Статус:** работен нормативен master документ  
> **Консолидирано:** README v1 + README v2 + migration/Dolibarr/B2B/product publishing/CRM решенията до 15.08.2026  
> **Repository:** `M99-Knowledge-Platform`

---

## 0. Роля на този документ

README v3 е третата, консолидирана версия на техническата памет на M99. Той не отменя валидните решения от README v1/v2, а ги събира с всички последващи решения за MoneyWork migration, Dolibarr ERP/CRM/warehouse, supplier/B2B integration, daily price+stock monitoring, TEST-first publishing, immutable published identity, Product Quality Gate и Customer & Sales Intelligence.

**Правило за governance:** нов код не трябва да връща проектa към вече отхвърлено поведение. Failure на discovery/parser не означава, че решението е неизвестно — първо се използва M99 registry/history, после live verification, а operator се пита само при реален конфликт.

### Статуси

- **DECIDED** — Изрично прието правило; следващият код не трябва да му противоречи.
- **IMPLEMENTED** — Има код/config/script, който реализира правилото.
- **TESTED** — Проверено чрез тестове, live GET, real write/readback или migration analysis.
- **PROPOSED** — Предложено направление, още не е нормативно решение.
- **OPEN** — Не е окончателно решено; системата не трябва да го предполага.
- **DEFERRED** — Прието като полезно, но отложено спрямо текущия приоритет.

---

## 1. Визия и бизнес цел

M99 Knowledge Platform е централният knowledge, product, commercial и customer intelligence слой на M99 Group. Тя е Single Source of Truth за canonical identity и verified knowledge; Dolibarr е оперативният ERP/CRM/warehouse слой; сайтовете са channel representations; MoneyWork и съществуващите сайтове са legacy sources; manufacturer/supplier/B2B portals са evidence/commercial sources.

Бизнес целта е платформата да подпомага международното развитие, България + Румъния и бъдещи пазари, минимален административен headcount, максимална автоматизация, по-добър cash flow, намаляване на slow-moving stock и целта на M99 Group Master Plan 2036 за приблизително 10 000 EUR чиста месечна печалба.

## 2. Системна архитектура

```text
LEGACY DATA + MANUFACTURERS + SUPPLIERS/B2B + CHANNELS + OPERATOR KNOWLEDGE
                              ↓
                 NORMALIZE / MATCH / EVIDENCE
                              ↓
                    CANONICAL M99 TRUTH
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
  PRODUCT/CONTENT        ERP/CRM/WAREHOUSE     CUSTOMER/SALES
        ↓                     ↓                     ↓
 MULTI-CHANNEL TEST       DOLIBARR              NEXT ACTIONS
        ↓                     ↓                     ↓
 OPERATOR APPROVAL        OPERATIONS          RETENTION/GROWTH
```

## 3. Историческо развитие

| Етап | Фокус | Ключова промяна |
|---|---|---|
| README v1 / Foundation | Knowledge Base | Single Source of Truth, Evidence Based, AI Native. |
| v0.5.x | Migration + ERP | MoneyWork importer, Dolibarr mapping, identity guardrails. |
| v0.6.2–0.6.3 | Evidence/Identity | Manufacturer exact evidence, supplier quarantine, existing-product discovery. |
| v0.6.4–0.6.6 | Content + controlled publishing | Claim taxonomy, multilingual content, DRY_RUN/WRITE_DRAFT/readback. |
| v0.6.6.4.x | Legacy reconciliation | 2076 vs 2100 → canonical build field-by-field. |
| v0.6.7.0–.6.x | Cherokee pilot | Supplier discovery, full content, channel matrix, credentials, live price, BNB FX. |
| v0.6.7.7.x | Real write + quality | Първи реален draft в mela99; установено е, че technical write success ≠ product quality. |
| Current | Constitution + next systems | TEST-first, immutable published identity, dynamic manufacturer discovery, daily price+stock, Customer 360/CRM rules. |

## 4. Canonical Product / Identity / Evidence

M99 ProductGroup е master. Channel product, supplier page, manufacturer page, Dolibarr record и MoneyWork code са mappings/evidence, не canonical identity. ProductGroup lifecycle е `draft → active → paused → retired`; physical DELETE изисква operator approval и ръчно `DELETE`.

Evidence priority: exact official manufacturer → official catalogue/certificate → exact supplier/B2B → verified internal/channel data → operator → AI over verified data. Near-match/wrong colour/conflicting protection class не може да захранва price/stock.

## 5. Migration: MoneyWork + сайтове → M99 → Dolibarr

Migration pipeline: `source inspection → normalization → deduplication → identity mapping → supplier/customer mapping → dry run → import → reconciliation → audit`. MoneyWork code се пази като external/legacy identifier, но не става автоматично M99 SKU. Съществуващите сайтове също са legacy sources и се сравняват field-by-field.

Реалният анализ включва 1 151 product/article rows, 1 070 suppliers, 10 893 customers и 11 963 counterparty source rows. Dolibarr product CSV tests вече са използвани за operational mapping.

## 6. Dolibarr ERP / Warehouse / CRM

Dolibarr е operational representation. Target warehouse flow: supplier order → reception → physical stock increase; customer order → shipment/configured event → physical stock decrease. Stock е variant-aware. Supplier-product relations трябва да пазят supplier SKU, price, currency, VAT, observed_at, availability, lead time и primary/secondary supplier.

Началният CRM flow остава `Първо обаждане → Оферта → Второ обаждане`, разширен с Customer 360, structured satisfaction calls, follow-up emails, reactivation, opportunities и complaint handling.

## 7. Supplier / B2B / Manufacturer Intelligence

Supplier layer поддържа отделни connector-и за public website и B2B portal. При наличен валидиран B2B connector той е предпочитан за commercial facts като B2B price и availability. При липса се използва exact public product page. Stenso B2B и Bultex B2B са целеви first-class integrations; public Stenso/Palltex и други доставчици остават fallback/discovery/commercial sources според доказаната identity.

Manufacturer exact product URL не трябва да е закован. Използва се manufacturer domain + dynamic discovery по model/MPN/aliases; resolved URL се кешира и re-verify-ва, а при 404/mismatch се извършва re-discovery.

## 8. Pricing + Daily Stock/Availability Monitoring

За всеки идентифициран продукт ежедневният commercial refresh проверява **цена и наличност**. Supplier availability и M99 physical warehouse stock са различни величини. Видим, но disabled размер означава съществуващ variant с текущо `OUT_OF_STOCK`, а не variant за изтриване. Unknown state се записва като `UNKNOWN`, не се предполага `IN_STOCK`.

За текущия Cherokee workflow pricing rule е exact Stenso price × 0.987; BGN използва EUR/BGN 1.95583; RO channel prices използват официален BNB EUR/RON, а в неработен ден последния публикуван курс.

## 9. Content / SEO / AEO / Images

Complete package: Product Name/H1, short description, long structured description, meaningful H2/H3, technical specifications, materials table, verified sizes, FAQ, Meta Title, Meta Description, SEO keywords, stable URL/slug policy, schema where possible, images and localized ALT. Supplier prose не се копира verbatim. Facts се използват общо, а prose/SEO се адаптират по channel/language.

Image pipeline: exact-product discovery → verify → download → dedupe → resize ~1200–1400 px → WebP → localized ALT → upload → association → readback.

## 10. Channel / Language Matrix

| Channel | Platform | Languages | Current rule/status |
|---|---|---|---|
| mela99.com | Thirty Bees / PrestaShop family | BG / EN / RU | Primary BG channel; TEST category се намира live; текущо Test ID 93, inactive. Реален draft product 2458 е създаден и е предмет на repair/quality work. |
| medicinski-drehi.com | PrestaShop 1.7.8.11 | BG / EN / RU | Medical clothing; API auth работи; новите продукти трябва да се създават в TEST, не във финални категории. |
| laviro.ro | PrestaShop 1.6.1.24 | RO / EN; BG stored-only | Romania; API auth работи; RON price от официален BNB EUR/RON. |
| alviro.ro | Thirty Bees 1.1.x | RO / EN; BG stored-only | Временно блокиран от TLS/API проблеми. |
| rabotni-drehi.com | WordPress | BG / EN / RU stored in M99 | WAF/Cloudflare/auth проблем; съдържанието се пази в M99 до решаване. |
| m99.eu | WordPress | BG / EN / RU | TASK_ONLY / NO PRODUCT WRITE до отстраняване на текущите технически проблеми. |

Language IDs се откриват live; не се приемат еднакви между сайтовете. Language lifecycle: `ACTIVE / PAUSED / STORED_ONLY`.

## 11. Publishing Constitution

1. Всеки **NEW** product се създава само в **TEST** на съответния сайт.  
2. TEST category се открива live; historical ID е hint, не truth.  
3. Operator определя финални категории/подкатегории и activation.  
4. Existing legacy product: **name + URL/slug LOCKED**.  
5. M99-created product след operator approval/publish също става old product: **name + URL LOCKED**.  
6. Неодобрен TEST draft може автоматично да поправя name, URL, reference, SEO, content, images.  
7. CREATE и UPDATE са различни contracts; duplicate guard преди CREATE.  
8. WRITE_DRAFT остава inactive/draft до operator approval.  
9. Mandatory readback след write.  
10. HTTP success не означава Product Quality PASS.

## 12. Product Quality Gate

Mandatory gates: identity, reference, manufacturer evidence, supplier mapping, price, currency, languages, complete content, materials, sizes, FAQ, SEO metadata/keywords, URL, images/ALT, TEST category, inactive state и readback. Numeric score не може да override-не failed critical gate.

## 13. Customer & Sales Intelligence

Customer 360 обединява клиентите и поръчките независимо от channel. При втора поръчка M99 сигнализира RETURNING_CUSTOMER. За поръчки над 100 EUR equivalent се изпълняват краткосрочен и дългосрочен follow-up cycle, а всички задачи/данни са видими в Dolibarr CRM.

| ID | Правило | Детайл | Статус |
|---|---|---|---|
| CUS-001 | Global Customer Identity | Един клиент се разпознава cross-channel; поръчките от всички сайтове се агрегираат в Customer 360. | DECIDED |
| CUS-002 | Second Order Detection | При втора поръчка, независимо от канала, M99 сигнализира RETURNING_CUSTOMER и показва историята. | DECIDED |
| CUS-003 | MoneyWork History | Историческите клиенти/контрагенти и наличната поръчкова история участват в миграцията към Customer 360. | DECIDED |
| CRM-100 | High-value threshold | Поръчка над 100 EUR equivalent активира специалните follow-up цикли. | DECIDED |
| CRM-110 | +15 day Satisfaction Call | 15 дни след квалифициращата поръчка Dolibarr създава задача за стандартно следпродажбено обаждане. | DECIDED |
| CRM-111 | Structured questionnaire | Проверяват се сайт/поръчване, доставка, продукт, качество, размер, повторна покупка, препоръка и бъдещи нужди. | DECIDED |
| CRM-120 | Negative feedback escalation | Ниска оценка/сериозен проблем създава CRM complaint/problem task и блокира неподходящ маркетинг до resolution. | DECIDED |
| CRM-130 | ~1 month email | Около 1 месец след поръчката се изпраща персонализиран email с закупения продукт и 5 релевантни продукта. | DECIDED |
| CRM-140 | 11-month reactivation | 11 месеца след поръчка >100 EUR се изпраща реактивационен email. | DECIDED |
| CRM-141 | New products in reactivation | 11-месечният email включва подходящи нови продукти, въведени след оригиналната поръчка. | DECIDED |
| CRM-146 | Reactivation call | 15 дни след 11-месечния email Dolibarr създава телефонна задача с Customer 360 и историята. | DECIDED |
| CRM-150 | Seasonality prediction | При достатъчно история M99 да прогнозира сезонен purchase window; 11 месеца остава fallback. | PROPOSED |
| CRM-160 | Customer Score | Динамична оценка по recency/frequency/monetary/margin/satisfaction/opportunity. | PROPOSED |
| CRM-170 | Prospect Discovery | Автоматично откриване и квалифициране на потенциални B2B клиенти по отрасли и география. | PROPOSED |
| CRM-180 | Contact Fatigue Protection | Всички pending actions да минават през conflict/priority check, за да няма прекомерна комуникация. | PROPOSED |
| CRM-190 | Next Best Action | M99 да предлага най-полезното следващо действие, а Dolibarr да е оперативната работна опашка. | PROPOSED |

### +15 day Satisfaction Call — минимален questionnaire

- Получена ли е поръчката без проблем?
- Доволен ли е клиентът от начина на поръчване и функционалността на сайта?
- Имало ли е нещо трудно/неясно в сайта?
- Доволен ли е от срока на доставка?
- Пратката пристигнала ли е в добро състояние?
- Получени ли са точно поръчаните артикули?
- Доволен ли е от качеството?
- Отговаря ли продуктът на описанието/снимките?
- При облекло/обувки: подходящ ли е размерът?
- Какво би променил?
- Ще поръча ли отново?
- Ще препоръча ли M99 на приятели/колеги (0–10)?
- Има ли нужда от други продукти?
- Има ли предстояща бъдеща потребност?

### CRM timeline за order >100 EUR

```text
ORDER >100 EUR
  ├─ +15 days → Satisfaction Call in Dolibarr
  ├─ ~1 month → Email: purchased product + 5 relevant products
  └─ +11 months → Reactivation email: same logic + new relevant products added after order
                     └─ +15 days → Reactivation Call in Dolibarr
```

## 14. Market Intelligence / Prospecting / AI Assistants

Market Intelligence анализира competitors, terminology, assortment, price positioning, category structure, content gaps и search ranking по конкретен market/language. Prospect Engine, Lead Score, Customer Score, Seasonality Prediction, Lost Customer/Sale Intelligence, Contact Fatigue Protection и Next Best Action са текущи proposed extensions и трябва да останат ясно маркирани като такива до формално приемане.

AI SEO Assistant трябва да генерира metadata, H1, descriptions, FAQ, ALT, comparisons, articles и translations от verified Knowledge Base. AI Marketing Assistant използва същата база за Facebook, LinkedIn, Instagram, email и site news.

## 15. Security / Audit / Testing

Credentials: no Git, no plaintext tracked files, no logs/screenshots. Текущо DPAPI local store; production Vault остава DEFERRED. Operational outputs се пазят като audit artifacts, но не са canonical truth. Validation chain: compile → unit/regression → live GET → prewrite → controlled write → readback → operator QA.

## 16. Current State — Cherokee WW601 Gold Integration Test

Текущият benchmark е Cherokee WW601 / supplier ref 08001931. Supplier price/BNB gate мина успешно. Реален draft е създаден в mela99.com като product ID 2458 в Test ID 93, inactive. Visual QA установи wrong internal reference, липсващи SEO keywords/images, недостатъчен real content, липсващи FAQ/materials/sizes и грешна URL policy. Последният GET-only quality gate блокира на hardcoded manufacturer URL; следващият architectural fix е Dynamic Manufacturer Discovery, след което controlled repair на product 2458 и повторен full readback.

## 17. Consolidated Rule Registry

| ID | Област | Нормативно правило | Статус |
|---|---|---|---|
| GOV-001 | Single Source of Truth | Canonical фактът се съхранява веднъж в M99 и се използва навсякъде. | DECIDED |
| GOV-002 | Knowledge First | Първо verified knowledge; след това content, SEO, ERP/CRM и channel payloads. | DECIDED |
| GOV-003 | AI Native, not AI Invented | AI структурира/адаптира проверени данни; не измисля стандарти, материали, stock или технически claims. | DECIDED |
| ID-001 | M99 identity independence | M99 ID е независим от MoneyWork code, supplier ref, manufacturer SKU, Dolibarr ID и channel IDs. | DECIDED |
| ID-002 | No ID reuse | Присвоен M99 ID не се използва повторно за друг ProductGroup. | DECIDED |
| ID-003 | ProductGroup lifecycle | draft → active → paused → retired. | DECIDED |
| ID-004 | Delete gate | Physical DELETE само след operator approval и изрично ръчно действие DELETE. | DECIDED |
| EVID-001 | Evidence hierarchy | Exact manufacturer > official docs/catalog/certificate > exact supplier > verified internal data > operator > AI. | DECIDED |
| MATCH-001 | Commercial quarantine | Near-match, wrong colour, protection mismatch или ambiguous product не може да захранва price/stock. | DECIDED/TESTED |
| MIG-001 | MoneyWork migration | Inspect → normalize → deduplicate → identity map → dry run → import → reconcile → audit. | DECIDED/TESTED |
| MIG-002 | Website legacy migration | Съществуващите сайтове са legacy sources; canonical master се строи field-by-field от най-доброто доказано съдържание. | DECIDED/TESTED |
| ERP-001 | Dolibarr role | M99 е canonical truth; Dolibarr е operational ERP/CRM/warehouse representation. | DECIDED |
| ERP-002 | Variant-aware stock | Складовите операции трябва да са variant-aware. | DECIDED |
| SUP-001 | Supplier connectors | Public site, B2B portal и други supplier sources са отделни connector classes. | DECIDED |
| SUP-002 | Dynamic manufacturer discovery | Manufacturer domain може да е known, но exact product URL трябва да се открива/ревалидира динамично. | DECIDED |
| PRICE-001 | Daily price refresh | Всеки идентифициран продукт се проверява ежедневно за supplier price. | DECIDED |
| STOCK-001 | Daily availability refresh | С ежедневния price refresh се проверява и variant availability. B2B има приоритет; без B2B се използва exact public product page. | DECIDED |
| STOCK-002 | Supplier stock != M99 stock | Supplier availability и собствената физическа наличност в Dolibarr са различни величини. | DECIDED |
| STOCK-003 | No variant deletion on OOS | OUT_OF_STOCK не изтрива variant; availability се обновява и се проверява отново. | DECIDED |
| FX-001 | RON conversion | Румънските channel prices използват официален BNB EUR/RON; в неработен ден последния публикуван курс. | DECIDED/TESTED |
| LANG-001 | Dynamic language IDs | ISO/language ID/active се откриват live; ID не се hardcode-ва между сайтове. | DECIDED/TESTED |
| LANG-002 | Language lifecycle | Езиците могат да са active, paused или stored-only. | DECIDED |
| PUB-001 | New product TEST only | Всеки NEW product се създава само в TEST/staging категорията на съответния канал. | DECIDED |
| PUB-002 | Final category operator-owned | Финалните категории/подкатегории се задават от оператор след review. | DECIDED |
| PUB-003 | Live TEST category resolution | TEST category се намира live; historical ID е само hint, не truth. | DECIDED/TESTED |
| PUB-004 | Existing name/url immutable | При existing legacy product name и URL/slug не се променят автоматично. | DECIDED |
| PUB-005 | Approved M99 product immutable | След operator approval/publish M99-created product се третира като old product; name/url се заключват. | DECIDED |
| PUB-006 | Unapproved TEST repair | Неодобрен M99 TEST draft може автоматично да поправя name, URL, reference, SEO, content и images. | DECIDED |
| PUB-007 | Create vs Update contracts | CREATE и UPDATE са отделни policies; duplicate guard се изпълнява преди CREATE. | DECIDED |
| PUB-008 | Inactive before approval | PrestaShop/Thirty Bees active=0; WordPress=draft преди operator activation. | DECIDED |
| QA-001 | Write success != product success | HTTP 200/201 не е достатъчен; Product Quality Gate трябва да PASS. | DECIDED/TESTED |
| QA-002 | Mandatory readback | След write системата GET-ва продукта и проверява ключовите написани полета. | DECIDED/TESTED |
| CONTENT-001 | Complete product package | Name/H1, short+long description, technical table, materials, sizes, FAQ, SEO, images, ALT и schema когато channel позволява. | DECIDED |
| CONTENT-002 | Channel differentiation | Фактите са общи, но prose/SEO се адаптират по channel и language; без механично duplicate content. | DECIDED/TESTED |
| IMG-001 | Image pipeline | Exact-product discovery → verify → download → dedupe → resize ~1200–1400 → WebP → localized ALT → upload → readback. | DECIDED |
| SEC-001 | No secrets in Git/logs | Credentials не се commit-ват/логват/показват; текущо локален DPAPI, production Vault deferred. | DECIDED/IMPLEMENTED |
| AUDIT-001 | Audit trail | Operational scripts пазят JSON/TXT outputs; observation != canonical truth. | DECIDED |
| TEST-001 | Validation chain | compile → unit/regression → live GET → prewrite → controlled write → readback → operator QA. | DECIDED |

## 18. Open Decisions

- **OPEN/DEFERRED:** Final canonical M99 numbering format
- **OPEN/DEFERRED:** Universal Variant SKU standard
- **OPEN/DEFERRED:** ProductGroup vs colour-variant universal boundary
- **OPEN/DEFERRED:** Exact Dolibarr parent/variant implementation
- **OPEN/DEFERRED:** Exact Dolibarr stock-decrease settings per deployment
- **OPEN/DEFERRED:** Tax mapping per channel
- **OPEN/DEFERRED:** Image rights/source policy per supplier/manufacturer
- **OPEN/DEFERRED:** Production Vault deployment
- **OPEN/DEFERRED:** Exact WordPress commerce implementation per WP channel
- **OPEN/DEFERRED:** Formal acceptance of Customer Score / Prospect Engine / Next Best Action / Contact Fatigue Protection

## 19. Roadmap from current point

1. Freeze README v3 / Platform Constitution
2. Dynamic Manufacturer Discovery
3. Repair Cherokee product 2458 to full Product Quality PASS
4. Complete TEST-first writes to medicinski-drehi.com and laviro.ro
5. Operator QA and approval workflow
6. 10–20 product repeatable batch
7. Daily supplier price + variant availability refresh
8. Stenso B2B + Bultex B2B commercial integrations
9. MoneyWork + channel legacy reconciliation into canonical M99
10. Production M99 → Dolibarr product/customer/supplier migration
11. Dolibarr warehouse + CRM automation
12. Customer 360 + >100 EUR follow-up rules
13. Scale supplier/category/market intelligence
14. International expansion and full M99 Group Master Plan 2036 integration

## 20. Definition of Success

**Single product:** exact identity, evidence, supplier mapping, price/FX, complete localized content, materials/sizes/FAQ, SEO, images/ALT, variants, TEST draft, readback, operator-ready, no invented stock/claims.  
**Bulk:** 10–20 products through the same pipeline without per-product custom code.  
**Migration:** MoneyWork + existing sites reconciled into canonical M99 without losing legacy identity/history.  
**ERP/CRM:** Dolibarr operational records linked to canonical M99 entities, variant-aware stock and Customer 360 tasks.  
**Business:** less manual work, faster catalogue growth, better retention, controlled pricing/stock, international scalability and measurable contribution to M99 Group Master Plan 2036.

---

**M99 Knowledge Platform — Product truth once. Customer truth once. Verified everywhere. Operated through Dolibarr. Governed by humans.**