from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from integrations.m99eu_prestashop.publisher import build_inactive_product_xml


def blank_schema() -> str:
    root = ET.Element("prestashop")
    ET.SubElement(root, "product")
    return ET.tostring(root, encoding="unicode")


def test_reference_is_numeric_only():
    xml_body, plan = build_inactive_product_xml(
        blank_schema(),
        language_ids=["1", "2", "3"],
        category_id=26,
    )
    assert re.fullmatch(r"M99-\d+", plan.reference)
    assert ET.fromstring(xml_body).findtext(".//product/reference") == plan.reference


def test_real_multilingual_names_and_meta_fields():
    xml_body, _ = build_inactive_product_xml(
        blank_schema(),
        language_ids=["1", "2", "3"],
        category_id=26,
    )
    root = ET.fromstring(xml_body)
    names = {n.attrib["id"]: n.text for n in root.findall(".//product/name/language")}
    assert names["1"] == "M99 PrestaShop API Test Product"
    assert names["2"] == "M99 тестов продукт за PrestaShop API"
    assert names["3"] == "Тестовый продукт M99 для PrestaShop API"
    assert len(set(names.values())) == 3
    assert all((n.text or "").strip() for n in root.findall(".//product/meta_title/language"))
    assert all((n.text or "").strip() for n in root.findall(".//product/meta_description/language"))


def test_only_category_association_is_sent():
    xml_body, _ = build_inactive_product_xml(
        blank_schema(),
        language_ids=["1", "2", "3"],
        category_id=26,
    )
    root = ET.fromstring(xml_body)
    associations = root.find(".//product/associations")
    assert associations is not None
    assert [child.tag for child in list(associations)] == ["categories"]
    assert root.findtext(".//product/associations/categories/category/id") == "26"


def test_server_owned_fields_are_not_sent():
    xml_body, _ = build_inactive_product_xml(
        blank_schema(),
        language_ids=["1", "2", "3"],
        category_id=26,
    )
    product = ET.fromstring(xml_body).find("product")
    assert product is not None
    for tag in ("id", "quantity", "date_add", "date_upd", "id_default_image", "position_in_category"):
        assert product.find(tag) is None


def test_unknown_language_id_blocks_contract():
    with pytest.raises(ValueError):
        build_inactive_product_xml(
            blank_schema(),
            language_ids=["1", "2", "3", "9"],
            category_id=26,
        )
