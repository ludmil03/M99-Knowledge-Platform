# M99 Knowledge Platform

# SCHEMA_STANDARDS.md

Version: 1.0.0

Status: Approved

---

# Purpose

Този документ определя задължителните стандарти за всички JSON Schema файлове в M99 Knowledge Platform.

Всеки schema файл трябва да следва тези правила.

Никакви изключения не се допускат без промяна на този документ.

---

# 1. Design Philosophy

Всички схеми трябва да бъдат:

- устойчиви
- разширяеми
- независими
- повторно използваеми
- валидируеми
- AI Ready

---

# 2. Architecture

Всички schema файлове наследяват:

base.schema.json

чрез

$ref

Не се допуска копиране на общи полета.

---

# 3. Required Fields

Всеки обект задължително съдържа:

id

uuid

code

status

version

audit

source

confidence

---

# 4. Object ID

Всеки обект има неизменяем ID.

Примери:

BR-000001

PR-000001

TECH-000001

STD-000001

MAT-000001

COL-000001

RISK-000001

PROF-000001

SUP-000001

---

# 5. UUID

Всеки обект получава UUID v4.

UUID никога не се променя.

---

# 6. Status Lifecycle

Допустими стойности:

draft

imported

validated

official

approved

deprecated

---

# 7. Source Priority

Всяко знание има източник.

Приоритет:

1 Official Manufacturer

2 Official Catalog

3 Official Certificate

4 Official Documentation

5 Supplier

6 M99 Expert

7 AI Generated

---

# 8. Confidence Score

Всеки Knowledge Object има:

confidence

от

0

до

100

Пример:

Official Certificate

100

Official Manufacturer

99

Supplier

95

AI Generated

75

---

# 9. Version

Всеки обект използва Semantic Versioning.

Структура:

major

minor

patch

---

# 10. Audit

Всеки запис съдържа:

created_at

updated_at

created_by

updated_by

---

# 11. Language

Всички текстови полета могат да бъдат многоезични.

Основен език:

bg

След това:

en

ro

de

...

---

# 12. Relations

Никога не се записват дублирани знания.

Използват се връзки.

Пример:

Product

↓

Technology

↓

Material

↓

Standard

---

# 13. Naming Convention

snake_case

за всички полета.

Пример:

official_name

created_at

updated_at

knowledge_score

---

# 14. Dates

ISO 8601

Пример

2026-08-03T20:15:00Z

---

# 15. File Naming

Всички schema файлове:

lowercase

пример:

brand.schema.json

technology.schema.json

material.schema.json

---

# 16. Validation

Всеки schema файл трябва да бъде валидиран по JSON Schema Draft 2020-12.

---

# 17. Breaking Changes

Промени в schema файловете се правят само чрез:

Major Version

---

# 18. AI Compatibility

Schema файловете трябва да бъдат използваеми от:

Python

FastAPI

ERP

CRM

LLM

AI Agents

Vector Database

Knowledge Graph

---

# 19. Future Compatibility

Не се допуска добавяне на полета, които могат да нарушат обратната съвместимост.

---

# 20. Golden Rule

Всеки факт съществува само веднъж.

Всички останали обекти сочат към него.

Never duplicate knowledge.

Always reference knowledge.
