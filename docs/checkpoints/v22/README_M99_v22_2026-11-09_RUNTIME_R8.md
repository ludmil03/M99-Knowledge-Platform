# M99 Knowledge Platform — README v22

**Дата:** 2026-11-09  
**Статус:** DOCUMENTATION PREPARED / GITHUB WRITE BLOCKED (403) / NOT PUSHED

## Потвърден актуален runtime от разговорите 1–9 ноември

- Проект: `C:\Users\user\Documents\GitHub\M99-Knowledge-Platform`
- Работна директория: `C:\Users\user\Documents\GitHub\M99-Knowledge-Platform\admin-platform`
- Стартиране: `.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Актуален адрес: `http://127.0.0.1:8000/`
- Операторски екран: `http://127.0.0.1:8000/operator/add-products`
- Порт `8070` е legacy и успешен тест там НЕ доказва работата на актуалната версия.

На 4 ноември е установен клон `dev/stage5-unified-ui-vat-r1`, HEAD `2c77945`, с локални непубликувани промени. Това е исторически checkpoint, а не актуално проверен Git status.

На 8 ноември е съобщено, че настройките за ДДС на седем канала са 20%. Това не доказва правилно прилагане на данъчните групи при реално публикуване.

## Continuous Execution — README v17

„Правилото за непрекъснато изпълнение остава активно: когато не е нужно операторско решение, работата продължава автоматично.“

Не се иска повторно информация, която вече е установена. Продължава се самостоятелно с безопасен анализ, подготовка, тестове и документация. Изрично разрешение се изисква само за действия, които действително го налагат. Задължителните проверки не се пропускат:

`STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE`

Git checkpoint: `COMMIT → PUSH → REMOTE_VERIFY`.

## R8 — задължителни решения

1. Работим по актуалния runtime на порт 8000, не по legacy 8070.
2. Един Unified Product Intake Engine; използват се доказаните решения от Bultex99, Calenda и Palltex, без четвърти импортер.
3. Доставчик, производител и марка са отделни роли. Supplier reference не е автоматично manufacturer MPN.
4. Всички регистрирани дестинации се виждат в избора на канали, независимо дали има избран продукт; Dolibarr се обозначава като ERP, не като публичен магазин.
5. `WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`. Изборът на канал не е разрешение за запис. Няма автоматично предварително избиране на всички READY канали.
6. CREATE и UPDATE са отделни; без дублиране, без silent UPDATE→CREATE, задължителен readback и audit.
7. Прилага се selective persistence M99-SP-001: ограничен кеш, трайно съхранение на избраните продукти и проверените доказателства, не цели каталози.
8. Пилотът за `rabotni-drehi.com` е с друг реален продукт, първоначално скрит, след API/quality preflight и изрично операторско разрешение за реален запис.
9. Съществуващият скрит продукт `m99.eu` ID 2042 / `M99 100019` не се създава повторно.
10. ProductGroup lifecycle: `draft → active → paused → retired`; hard DELETE само с отделно операторско одобрение, ръчно `DELETE` и audit.

## Достоверност и безопасност

При конфликт важи по-късното изрично отменящо решение, не по-големият номер на README. `DECIDED != IMPLEMENTED != TESTED != WINDOWS_ACCEPTED != PRODUCTION_READY`.

Документът не променя код, сайтове, бази данни, локални файлове или процеси. Не удостоверява ново Windows acceptance. GitHub API отказа създаването на този документ с HTTP 403 `Resource not accessible by integration`; файлът НЕ е качен в GitHub. R8 остава `NOT_RELEASEABLE`.
