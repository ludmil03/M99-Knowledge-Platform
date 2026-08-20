from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class DraftPlan:
    sku: str
    name: str
    category_id: int
    price: str = "1.00"


def _safe_slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-") or "m99-api-test"


def _set_text(parent: ET.Element, tag: str, value: str) -> ET.Element:
    node = parent.find(tag)
    if node is None:
        node = ET.SubElement(parent, tag)
    node.text = value
    return node


def _ensure_multilang(parent: ET.Element, tag: str, language_ids: list[str], value: str) -> None:
    node = parent.find(tag)
    if node is None:
        node = ET.SubElement(parent, tag)
    for child in list(node):
        node.remove(child)
    for language_id in language_ids:
        lang = ET.SubElement(node, "language", {"id": str(language_id)})
        lang.text = value


def build_inactive_product_xml(
    blank_xml: str,
    *,
    language_ids: list[str],
    category_id: int,
    sku: str | None = None,
    name: str | None = None,
) -> tuple[str, DraftPlan]:
    root = ET.fromstring(blank_xml)
    product = root.find("product")
    if product is None:
        raise ValueError("Blank schema did not contain product node")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    sku = sku or f"M99-PS-TEST-{stamp}"
    name = name or f"M99 PrestaShop API Sandbox Test {stamp}"
    plan = DraftPlan(sku=sku, name=name, category_id=category_id)

    _set_text(product, "id_category_default", str(category_id))
    _set_text(product, "reference", sku)
    _set_text(product, "price", plan.price)
    _set_text(product, "active", "0")
    _set_text(product, "state", "1")
    _set_text(product, "available_for_order", "0")
    _set_text(product, "show_price", "1")
    _set_text(product, "visibility", "none")
    _set_text(product, "product_type", "standard")
    _set_text(product, "minimal_quantity", "1")

    _ensure_multilang(product, "name", language_ids, name)
    _ensure_multilang(product, "link_rewrite", language_ids, _safe_slug(sku))
    _ensure_multilang(
        product,
        "description",
        language_ids,
        "<p>M99 Knowledge Platform PrestaShop API sandbox test. Inactive test product.</p>",
    )
    _ensure_multilang(
        product,
        "description_short",
        language_ids,
        "<p>M99 PrestaShop sandbox test.</p>",
    )

    associations = product.find("associations")
    if associations is None:
        associations = ET.SubElement(product, "associations")

    categories = associations.find("categories")
    if categories is None:
        categories = ET.SubElement(associations, "categories")

    for child in list(categories):
        categories.remove(child)

    category = ET.SubElement(categories, "category")
    ET.SubElement(category, "id").text = str(category_id)

    return ET.tostring(root, encoding="unicode"), plan


def inspect_draft_plan(plan: DraftPlan) -> dict[str, object]:
    return {
        "sku": plan.sku,
        "name": plan.name,
        "category_id": plan.category_id,
        "price": plan.price,
        "active": 0,
        "visibility": "none",
    }


def parse_active_language_ids(languages_xml: str) -> list[str]:
    root = ET.fromstring(languages_xml)
    ids: list[str] = []
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

    first_name = product.find("name/language")
    actual_name = (first_name.text or "").strip() if first_name is not None else ""

    checks = {
        "id_present": bool(text("id")),
        "active_zero": text("active") == "0",
        "reference_match": text("reference") == expected.sku,
        "name_match": actual_name == expected.name,
        "category_match": text("id_category_default") == str(expected.category_id),
    }
    checks["pass"] = all(checks.values())
    return checks
