# M99 Knowledge Platform — README v17

## M99 FULL TEST & SIMULATION RULE — NORMATIVE / MANDATORY

Това правило важи за **всяка** следваща изпълнима M99 версия: ZIP, BAT/CMD, PowerShell, Python installer, reconstruction, recovery, checkpoint, migration и publish пакет.

Преди пакетът да бъде подаден на оператора, трябва **пълно** да се изпълни следната верига:

`STATIC → SYNTAX_AST → KNOWN_DEFECT_REGRESSION → STATE_SIMULATIONS → SAFETY_FAIL_CLOSED → FOCUSED_TESTS → FULL_REGRESSION → PACKAGE_INTEGRITY → WINDOWS_PRE_GATES → WINDOWS_ACCEPTANCE`

За Git checkpoint към нея задължително се добавя:

`→ COMMIT → PUSH → REMOTE_VERIFY`

**Нито един етап не може да бъде пропускан заради скорост.** Ако задължителен етап липсва, статусът е `NOT_RELEASEABLE`. Неуспешна версия никога не става stable baseline.

### 1. STATIC
Проверяват се структура, contract, manifest, имена/пътища, protected paths, forbidden operations и обхватът на пакета.

### 2. SYNTAX_AST
Всеки генериран скрипт се parse/compile-ва с реалния parser/runtime, когато той е наличен. Ако Windows PowerShell не е наличен в generation environment, пакетът задължително съдържа **реален Windows PowerShell AST pre-gate**, който се изпълнява преди mutation/main script. AST failure блокира изпълнението.

### 3. KNOWN_DEFECT_REGRESSION
Всеки вече срещнат релевантен дефект получава regression check. Минималният исторически каталог включва: PowerShell `foreach` parser дефекти; automatic `$args` collision; diverged `git diff` discovery; arbitrary staged-file threshold; Unicode-dependent matching; грешен pytest root/import context; unexpected Git dirty state; ambiguous write/retry.

### 4. STATE_SIMULATIONS
Задължителни според приложимостта: happy path; zero-change/idempotent; single-change; multi-change; partial previous run; dirty tree; unexpected staged/unstaged/untracked; missing source/path/object; wrong branch; wrong HEAD; wrong origin; remote moved/conflict.

### 5. SAFETY_FAIL_CLOSED
Fail-closed при protected-path mutation, identity/duplicate ambiguity, unauthorized website write, DB migration, process control, secret leakage, unintended CREATE/DELETE, UPDATE→CREATE fallback и ambiguous write outcome. Не се прави auto-retry след двусмислен write.

### 6. FOCUSED_TESTS
Изпълнява се пълният package-specific focused suite. За product/publish промени се включват релевантните Product 2041 / M99 100018 тестове и директно засегнатите модули.

### 7. FULL_REGRESSION
Когато пакетът може да влияе на repository behavior, се изпълнява целият repository regression suite. Focused PASS не заменя full regression.

### 8. PACKAGE_INTEGRITY
Проверяват се ZIP/archive integrity, очакваните файлове/manifest и SHA-256.

### 9. WINDOWS_PRE_GATES
Тест, който не може реално да се изпълни в generation environment, се маркира `WINDOWS_ONLY`, никога предварително като PASS. Той трябва да бъде автоматизиран като fail-closed pre-gate преди съответната mutation/action.

### 10. EVIDENCE
Отчетът посочва точните test counts и разделя STATIC, SIMULATION, RUNTIME и WINDOWS ACCEPTANCE. Не се твърди commit/push/remote verification без доказателство.

## Continuous Execution
Правилото за непрекъснато изпълнение остава активно: когато не е нужно операторско решение, работата продължава автоматично. Това **никога не позволява пропускане на тестов слой**. Свързаните технически промени се обединяват, когато е безопасно, за да се намалят Windows acceptance циклите.

## Current proven reconstruction state
R2.6 е доказан от Windows acceptance: PowerShell AST PASS; focused Product 2041 regression **66 passed**; full regression **1064 passed, 6 warnings**; Windows acceptance PASS; website write FALSE; DB migration FALSE; process kill FALSE. R2.6 не е извършил commit/push.

Това правило е нормативно за всички следващи M99 executable deliveries.
