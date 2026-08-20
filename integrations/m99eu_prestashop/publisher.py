from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class DraftPlan:
    reference: str
    category_id: int
    price: str
    language_ids: tuple[str, ...]
    names: dict[str, str]
    meta_titles: dict[str, str]
    meta_descriptions: dict[str, str]


def _numeric_m99_reference() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"M99-{stamp}"


def _safe_slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-") or "m99-product"


def _lang_map(language_ids: list[str]) -> dict[str, str]:
    known = {"1": "en", "2": "bg", "3": "ru"}
    missing = [lid for lid in language_ids if lid not in known]
    if missing:
        raise ValueError(
            "Unknown m99.eu language IDs: " + ", ".join(missing) +
            ". Update live language mapping before write."
        )
    return {lid: known[lid] for lid in language_ids}


def _localized_contract(reference: str, language_ids: list[str]) -> dict[str, dict[str, str]]:
    iso_by_id = _lang_map(language_ids)

    content = {
        "en": {
            "name": "M99 PrestaShop API Test Product",
            "description": "<p>M99 Knowledge Platform controlled PrestaShop API test product. Created inactive for technical validation only.</p>",
            "description_short": "<p>M99 controlled API test product.</p>",
            "meta_title": "M99 PrestaShop API Test Product",
            "meta_description": "Inactive M99 test product used to validate the PrestaShop API publishing workflow.",
        },
        "bg": {
            "name": "M99 тестов продукт за PrestaShop API",
            "description": "<p>Контролиран тестов продукт на M99 Knowledge Platform за проверка на PrestaShop API. Създава се неактивен само за техническа валидация.</p>",
            "description_short": "<p>Контролиран M99 тестов продукт за API.</p>",
            "meta_title": "M99 тестов продукт за PrestaShop API",
            "meta_description": "Неактивен M99 тестов продукт за проверка на процеса за публикуване през PrestaShop API.",
        },
        "ru": {
            "name": "Тестовый продукт M99 для PrestaShop API",
            "description": "<p>Контролируемый тестовый продукт M99 Knowledge Platform для проверки PrestaShop API. Создаётся неактивным только для технической валидации.</p>",
            "description_short": "<p>Контролируемый тестовый продукт M99 для API.</p>",
            "meta_title": "Тестовый продукт M99 для PrestaShop API",
            "meta_description": "Неактивный тестовый продукт M99 для проверки процесса публикации через PrestaShop API.",
        },
    }

    result = {}
    for language_id, iso in iso_by_id.items():
        item = dict(content[iso])
        item["link_rewrite"] = _safe_slug(reference + "-" + iso)
        result[language_id] = item
    return result


def _add_multilang(product: ET.Element, tag: str, values: dict[str, str]) -> None:
    node = ET.SubElement(product, tag)
    for language_id, value in values.items():
        ET.SubElement(node, "language", {"id": str(language_id)}).text = value


def build_inactive_product_xml(
    blank_xml: str,
    *,
    language_ids: list[str],
    category_id: int,
    sku: str | None = None,
    name: str | None = None,
) -> tuple[str, DraftPlan]:
    blank_root = ET.fromstring(blank_xml)
    if blank_root.find("product") is None:
        raise ValueError("Blank schema did not contain product node")
    if category_id <= 0:
        raise ValueError("category_id must be positive")
    if not language_ids:
        raise ValueError("At least one active language is required")

    reference = sku or _numeric_m99_reference()
    if not re.fullmatch(r"M99-\d+", reference):
        raise ValueError("M99 reference must match M99- followed by digits only")

    localized = _localized_contract(reference, language_ids)
    if name:
        if len(language_ids) != 1:
            raise ValueError("Explicit name override is not allowed for multilingual payloads")
        localized[language_ids[0]]["name"] = name

    root = ET.Element("prestashop")
    product = ET.SubElement(root, "product")

    for tag, value in (
        ("id_category_default", str(category_id)),
        ("reference", reference),
        ("price", "1.00"),
        ("active", "0"),
        ("state", "1"),
        ("available_for_order", "0"),
        ("show_price", "1"),
        ("visibility", "none"),
        ("product_type", "standard"),
        ("minimal_quantity", "1"),
    ):
        ET.SubElement(product, tag).text = value

    for tag, key in (
        ("name", "name"),
        ("link_rewrite", "link_rewrite"),
        ("description", "description"),
        ("description_short", "description_short"),
        ("meta_title", "meta_title"),
        ("meta_description", "meta_description"),
    ):
        _add_multilang(product, tag, {lid: localized[lid][key] for lid in language_ids})

    associations = ET.SubElement(product, "associations")
    categories = ET.SubElement(associations, "categories")
    category = ET.SubElement(categories, "category")
    ET.SubElement(category, "id").text = str(category_id)

    plan = DraftPlan(
        reference=reference,
        category_id=category_id,
        price="1.00",
        language_ids=tuple(language_ids),
        names={lid: localized[lid]["name"] for lid in language_ids},
        meta_titles={lid: localized[lid]["meta_title"] for lid in language_ids},
        meta_descriptions={lid: localized[lid]["meta_description"] for lid in language_ids},
    )

    return ET.tostring(root, encoding="unicode"), plan


def inspect_draft_plan(plan: DraftPlan) -> dict[str, object]:
    return {
        "reference": plan.reference,
        "category_id": plan.category_id,
        "price": plan.price,
        "active": 0,
        "visibility": "none",
        "language_ids": list(plan.language_ids),
        "names": plan.names,
        "meta_titles": plan.meta_titles,
    }


def parse_active_language_ids(languages_xml: str) -> list[str]:
    root = ET.fromstring(languages_xml)
    ids = []
    for language in root.findall(".//language"):
        id_node = language.find("id")
        active_node = language.find("active")
        if id_node is None or not (id_node.text or "").strip():
            continue
        if active_node is None or (active_node.text or "1").strip() == "1":
            ids.append((id_node.text or "").strip())
    if not ids:
        raise ValueError("No active language IDs returned")
    return ids


def extract_created_product_id(xml_text: str) -> int:
    root = ET.fromstring(xml_text)
    node = root.find(".//product/id")
    if node is None or not (node.text or "").strip():
        raise ValueError("Created product response has no ID")
    return int((node.text or "").strip())


def verify_product_readback(expected: DraftPlan, product_xml: str) -> dict[str, object]:
    root = ET.fromstring(product_xml)
    product = root.find(".//product")
    if product is None:
        raise ValueError("Read-back did not contain product")

    def text(tag: str) -> str:
        node = product.find(tag)
        return (node.text or "").strip() if node is not None else ""

    names = {
        node.attrib.get("id", ""): (node.text or "").strip()
        for node in product.findall("name/language")
    }

    checks = {
        "id_present": bool(text("id")),
        "active_zero": text("active") == "0",
        "reference_match": text("reference") == expected.reference,
        "category_match": text("id_category_default") == str(expected.category_id),
        "all_names_match": all(
            names.get(language_id) == expected.names[language_id]
            for language_id in expected.language_ids
        ),
    }
    checks["pass"] = all(checks.values())
    return checks
