# M99 Knowledge Platform — README v12 — 05.09.2026

## 1. Статус

M99 Knowledge Platform е canonical knowledge/governance платформа за управление на продуктова идентичност, supplier/manufacturer evidence, channel content, цени, наличности, ERP/CRM интеграции и контролирано публикуване.

Текущата доказана линия е:

`Approved Supplier -> Supplier Browser -> Live Hydration -> Operator Selection -> Identity Resolution -> DRAFT ImportJob -> Canonical Preview -> Channel Preflight -> Publish`

Към 05.09.2026 текущият работен milestone е **Revision 31 / Phase 4.3 / R3.7R7A1**.

## 2. Последно приета версия

**R3.7R7A1 — Stale R7 Test Compat Fix**

Успешни gates:

- 10 dedicated R7/R7A/R7A1 tests — PASS
- 560 maintained regression tests — PASS
- Complete Identity model discovery — PASS
- Complete Identity schema reconciliation — PASS
- R7 Manufacturer + Variant Image runtime patch — applied
- No DRAFT created by installer
- No m99.eu publish
- No Dolibarr / M99-owned stock write
- No automatic Git commit/push

Identity ORM contract, открит от реалния runtime:

- `m99_v073_identity_external_mappings`
- `m99_v073_identity_resolutions`

Преди R7A1 липсваше `m99_v073_identity_resolutions`. Тя беше създадена чрез controlled schema reconciliation след backup.

Последен backup:
`admin-platform/data/backups/m99_admin_before_r37r7a_identity_20260904T210737Z.db`

## 3. Git / stable baseline

Последният доказано pushed Git baseline преди Phase 4.x е:

`cf2007cd1c6973dbc63c54dcfe83fca5b8a021b8`

Описание:
`Revision 31 Phase 3 R5 R5 - source and category governance GUI accepted`

Phase 4.x / R3.7 работата все още не трябва да се счита за финално приета за Git push, докато live Identity -> DRAFT -> Canonical Preview не бъде доказана.

Operational DB, backups и local audit файлове не се commit-ват.

## 4. Canonical governance

Canonical chain:

`ProductGroup -> ProductVariant -> SupplierOffer / SupplierMapping -> Evidence / Observation -> ChannelPresence -> ChannelContent -> ChannelPrice -> InventoryMapping`

Identity states:

`NEW / EXISTING / AMBIGUOUS / UNRESOLVED`

AMBIGUOUS изисква human decision.

ProductGroup lifecycle:

`draft -> active -> paused -> retired`

Hard DELETE е изключение и изисква operator approval + ръчно изписване `DELETE` + audit.

External IDs са mappings, а не canonical identity.

## 5. Supplier / Manufacturer / Brand

Supplier и Manufacturer са отделни роли. Approved Supplier не означава автоматично Approved Manufacturer.

Governance v11:

- Operator може да предлага Supplier / Manufacturer.
- Proposal е PENDING и не може да се използва като approved source.
- Само Super Admin одобрява/отхвърля.
- Manufacturer <-> Supplier Product mapping е отделен audited mapping.
- Brand е отделен canonical concept; supplier-provided brand string не трябва тихо да се превръща в legal Manufacturer.

### Текущ проблем

В PREPARE има Manufacturer/Brand evidence поле, но **няма отделно поле за URL към официалния сайт на производителя**.

Това е OPEN REQUIREMENT за следващата revision:

- Manufacturer name
- Manufacturer official website URL
- optional official product URL
- governance state: approved / proposed / pending / not attached
- provenance: supplier evidence / operator-confirmed / official manufacturer evidence

URL не трябва автоматично да approve-ва Manufacturer.

## 6. Calenda control product

Контролен продукт:

- Supplier: Calenda
- Product: `МЪЖКА РИЗА RIVER`
- Supplier reference: `93100`
- Calenda Product ID: `31809`
- Supplier brand evidence: `PROMO STARS`

Доказани variant данни:

- 4 colors
- 6 sizes на color
- 24 Color x Size rows
- 20 available rows
- 4 OUT_OF_STOCK rows
- size-level supplier availability
- size-level prices

Доказани цветови изображения:

- white / code 20 -> `https://calenda.bg/storage/products/93100_20a.jpg`
- black / code 26 -> `https://calenda.bg/storage/products/93100_26a.jpg`
- dark blue / code 42 -> `https://calenda.bg/storage/products/93100_42a.jpg`
- sky blue / code 46 -> `https://calenda.bg/storage/products/93100_46a.jpg`

## 7. OPEN DEFECT — Variant Images

Въпреки че Calenda connector доказано извлича 4 отделни color images, текущият GUI verification/prepare flow показва само **едно изображение**.

Статус: **OPEN DEFECT — НЕ Е РЕШЕН.**

Не трябва:

- да се дублира едно изображение към всички variants;
- да се губят variant-image associations;
- да се publish-ва продуктът, преди image preservation да бъде доказано end-to-end.

Търсената верига е:

`4 colors -> 24 Color x Size evidence rows -> 4 color-specific images -> Identity -> DRAFT -> Canonical Preview`

## 8. Текущ runtime blocker — Internal Server Error

При натискане на бутона в `/add-products/r37/prepare` на 05.09.2026 браузърът показва:

`Internal Server Error`

URL:
`http://127.0.0.1:8070/add-products/r37/prepare`

Това означава, че live acceptance все още НЕ е завършена.

Следващата revision трябва първо да диагностицира traceback-а на POST `/add-products/r37/prepare`, преди да се прави нов DRAFT attempt.

Не трябва да се натиска многократно create/confirm бутонът, докато не бъде установено дали request-ът е извършил частичен write.

## 9. m99.eu

Platform:
PrestaShop 9.1.5

Active languages:
EN / BG / RU

API category used in tests:
26

Доказано отделно:
HTTP 201 create path за един inactive test product.

Това НЕ означава, че пълният Supplier -> Canonical -> Channel publish pipeline е приет.

Първият реален publish остава блокиран до:

1. успешен live Identity -> DRAFT;
2. Canonical Preview;
3. Manufacturer evidence governance;
4. доказани variant images;
5. explicit operator publish decision.

## 10. Следваща стъпка

Следваща revision:

**R3.7R8 — Prepare 500 Diagnostic + Manufacturer Official URL + Variant Image Trace**

Цели:

1. Safe diagnostic на Internal Server Error в POST `/add-products/r37/prepare`.
2. Проверка дали failed request е създал Identity resolution или DRAFT row.
3. Добавяне на Manufacturer official website URL в operator flow без silent approval.
4. Trace на variant images през:
   `connector -> hydration -> prepare_context -> DRAFT serialization -> canonical preview`.
5. RIVER acceptance: 4 colors / 24 rows / 4 images.
6. Никакъв publish към m99.eu.
7. Никакъв Dolibarr или M99-owned stock write.
8. Никакъв automatic Git push.

## 11. Operator flow

Нормалният оператор не трябва да използва Python, PowerShell, HTTP, JSON или SQL.

Основният UX остава:

`Add Products -> Supplier -> Category/Product Selection -> PREPARE -> Identity -> DRAFT -> Canonical Preview`

Sidebar остава:

- Add Products
- Suppliers / Browse
- Import Jobs

## 12. Safety rules

- One live product before batch.
- No silent canonical identity changes.
- No silent Supplier/Manufacturer creation.
- No publish without explicit operator action.
- External supplier availability != M99 physical stock.
- Source failure != zero stock.
- Keep last verified supplier observation on source failure.
- Do not commit operational DB/backups/audit files.
- Do not reopen accepted milestones without new evidence.

## 13. Resume marker

When continuing in a new conversation, use:

`M99_RESUME_R31_P43_R37_R7A1_2026-09-05`

Machine-readable state file:
`M99_CURRENT_STATE_R31_P43_R37_R7A1.json`
