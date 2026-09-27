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
