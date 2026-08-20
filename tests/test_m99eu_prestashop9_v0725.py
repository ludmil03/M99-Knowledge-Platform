from __future__ import annotations

from dataclasses import replace
import xml.etree.ElementTree as ET

import pytest

from integrations.m99eu_prestashop.client import PrestaShopAPIError, PrestaShopWebserviceClient
from integrations.m99eu_prestashop.config import M99EUPrestaShopConfig
from integrations.m99eu_prestashop.publisher import (
    build_inactive_product_xml,
    extract_created_product_id,
    parse_active_language_ids,
    verify_product_readback,
)


def make_blank_schema() -> str:
    root = ET.Element("prestashop")
    product = ET.SubElement(root, "product")

    for tag in (
        "id",
        "id_category_default",
        "reference",
        "price",
        "active",
        "state",
        "available_for_order",
        "show_price",
        "visibility",
        "product_type",
        "minimal_quantity",
    ):
        ET.SubElement(product, tag)

    for tag in ("name", "link_rewrite", "description", "description_short"):
        node = ET.SubElement(product, tag)
        ET.SubElement(node, "language", {"id": "1"})
        ET.SubElement(node, "language", {"id": "2"})

    associations = ET.SubElement(product, "associations")
    categories = ET.SubElement(associations, "categories")
    category = ET.SubElement(categories, "category")
    ET.SubElement(category, "id")

    return ET.tostring(root, encoding="unicode")


def make_languages_xml() -> str:
    root = ET.Element("prestashop")
    languages = ET.SubElement(root, "languages")

    for lang_id, iso in (("1", "bg"), ("2", "en")):
        language = ET.SubElement(languages, "language")
        ET.SubElement(language, "id").text = lang_id
        ET.SubElement(language, "iso_code").text = iso
        ET.SubElement(language, "active").text = "1"

    return ET.tostring(root, encoding="unicode")


def make_readback_xml(*, active: str) -> str:
    root = ET.Element("prestashop")
    product = ET.SubElement(root, "product")

    ET.SubElement(product, "id").text = "55"
    ET.SubElement(product, "active").text = active
    ET.SubElement(product, "reference").text = "M99-TEST-1"
    ET.SubElement(product, "id_category_default").text = "938"

    name = ET.SubElement(product, "name")
    ET.SubElement(name, "language", {"id": "1"}).text = "Test Product"

    return ET.tostring(root, encoding="unicode")


BLANK = make_blank_schema()
LANGS = make_languages_xml()
READBACK_INACTIVE = make_readback_xml(active="0")
READBACK_ACTIVE = make_readback_xml(active="1")


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


@pytest.fixture
def config():
    return M99EUPrestaShopConfig(
        base_url="https://m99.eu",
        api_key="A" * 32,
        test_category_id=938,
    )


def test_programmatic_xml_fixtures_are_well_formed():
    for xml_text in (BLANK, LANGS, READBACK_INACTIVE, READBACK_ACTIVE):
        ET.fromstring(xml_text)


def test_config_blocks_wrong_host(config):
    with pytest.raises(ValueError):
        replace(config, base_url="https://example.com").validate()


def test_config_requires_https(config):
    with pytest.raises(ValueError):
        replace(config, base_url="http://m99.eu").validate()


def test_active_languages_are_discovered():
    assert parse_active_language_ids(LANGS) == ["1", "2"]


def test_builder_forces_inactive_product():
    xml_body, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2"],
        category_id=938,
        sku="M99-TEST-1",
        name="Test Product",
    )
    root = ET.fromstring(xml_body)
    assert root.findtext(".//product/active") == "0"
    assert root.findtext(".//product/available_for_order") == "0"
    assert root.findtext(".//product/visibility") == "none"
    assert root.findtext(".//product/reference") == "M99-TEST-1"
    assert root.findtext(".//product/id_category_default") == "938"
    assert plan.category_id == 938


def test_builder_sets_all_language_names():
    xml_body, _ = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2"],
        category_id=938,
        sku="M99-TEST-1",
        name="Test Product",
    )
    root = ET.fromstring(xml_body)
    names = [n.text for n in root.findall(".//product/name/language")]
    assert names == ["Test Product", "Test Product"]


def test_client_uses_api_key_as_basic_auth_username(config):
    session = FakeSession([FakeResponse(200, "<prestashop/>")])
    client = PrestaShopWebserviceClient(config, session=session)
    client.get_api_root()
    _, _, kwargs = session.calls[0]
    assert kwargs["auth"] == (config.api_key, "")


def test_client_blocks_redirect(config):
    session = FakeSession([FakeResponse(302, "redirect")])
    with pytest.raises(PrestaShopAPIError):
        PrestaShopWebserviceClient(config, session=session).get_api_root()


def test_create_uses_post_xml(config):
    response_xml = make_readback_xml(active="0")
    session = FakeSession([FakeResponse(201, response_xml)])
    client = PrestaShopWebserviceClient(config, session=session)
    client.create_product("<prestashop><product/></prestashop>")
    method, _, kwargs = session.calls[0]
    assert method == "POST"
    assert kwargs["headers"]["Content-Type"] == "application/xml"


def test_extract_created_product_id():
    assert extract_created_product_id(READBACK_INACTIVE) == 55


def test_readback_requires_inactive_and_matching_identity():
    _, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2"],
        category_id=938,
        sku="M99-TEST-1",
        name="Test Product",
    )
    assert verify_product_readback(plan, READBACK_INACTIVE)["pass"] is True


def test_readback_fails_if_product_is_active():
    _, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1"],
        category_id=938,
        sku="M99-TEST-1",
        name="Test Product",
    )
    checks = verify_product_readback(plan, READBACK_ACTIVE)
    assert checks["pass"] is False
    assert checks["active_zero"] is False
