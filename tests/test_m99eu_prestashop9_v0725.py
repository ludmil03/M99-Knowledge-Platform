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
    ET.SubElement(root, "product")
    return ET.tostring(root, encoding="unicode")


def make_languages_xml() -> str:
    root = ET.Element("prestashop")
    languages = ET.SubElement(root, "languages")
    for lang_id, iso in (("1", "en"), ("2", "bg"), ("3", "ru")):
        language = ET.SubElement(languages, "language")
        ET.SubElement(language, "id").text = lang_id
        ET.SubElement(language, "iso_code").text = iso
        ET.SubElement(language, "active").text = "1"
    return ET.tostring(root, encoding="unicode")


def make_readback(plan, *, active="0") -> str:
    root = ET.Element("prestashop")
    product = ET.SubElement(root, "product")
    ET.SubElement(product, "id").text = "55"
    ET.SubElement(product, "active").text = active
    ET.SubElement(product, "reference").text = plan.reference
    ET.SubElement(product, "id_category_default").text = str(plan.category_id)
    name = ET.SubElement(product, "name")
    for language_id in plan.language_ids:
        ET.SubElement(name, "language", {"id": language_id}).text = plan.names[language_id]
    return ET.tostring(root, encoding="unicode")


BLANK = make_blank_schema()
LANGS = make_languages_xml()


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


def test_config_blocks_wrong_host(config):
    with pytest.raises(ValueError):
        replace(config, base_url="https://example.com").validate()


def test_config_requires_https(config):
    with pytest.raises(ValueError):
        replace(config, base_url="http://m99.eu").validate()


def test_active_languages_are_discovered():
    assert parse_active_language_ids(LANGS) == ["1", "2", "3"]


def test_builder_forces_inactive_product():
    xml_body, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2", "3"],
        category_id=938,
        sku="M99-1000001",
    )
    root = ET.fromstring(xml_body)
    assert root.findtext(".//product/active") == "0"
    assert root.findtext(".//product/available_for_order") == "0"
    assert root.findtext(".//product/visibility") == "none"
    assert root.findtext(".//product/reference") == "M99-1000001"
    assert root.findtext(".//product/id_category_default") == "938"
    assert plan.category_id == 938


def test_builder_sets_all_language_names():
    xml_body, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2", "3"],
        category_id=938,
        sku="M99-1000001",
    )
    root = ET.fromstring(xml_body)
    names = {
        n.attrib["id"]: n.text
        for n in root.findall(".//product/name/language")
    }
    assert names == plan.names
    assert len(names) == 3
    assert len(set(names.values())) == 3


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
    session = FakeSession([
        FakeResponse(201, "<prestashop><product><id>55</id></product></prestashop>")
    ])
    client = PrestaShopWebserviceClient(config, session=session)
    client.create_product("<prestashop><product/></prestashop>")
    method, _, kwargs = session.calls[0]
    assert method == "POST"
    assert kwargs["headers"]["Content-Type"] == "application/xml"


def test_extract_created_product_id():
    assert extract_created_product_id(
        "<prestashop><product><id>55</id></product></prestashop>"
    ) == 55


def test_readback_requires_inactive_and_matching_identity():
    _, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2", "3"],
        category_id=938,
        sku="M99-1000001",
    )
    assert verify_product_readback(plan, make_readback(plan, active="0"))["pass"] is True


def test_readback_fails_if_product_is_active():
    _, plan = build_inactive_product_xml(
        BLANK,
        language_ids=["1", "2", "3"],
        category_id=938,
        sku="M99-1000001",
    )
    checks = verify_product_readback(plan, make_readback(plan, active="1"))
    assert checks["pass"] is False
    assert checks["active_zero"] is False


def test_legacy_alphanumeric_test_reference_is_rejected():
    with pytest.raises(ValueError):
        build_inactive_product_xml(
            BLANK,
            language_ids=["1", "2", "3"],
            category_id=938,
            sku="M99-TEST-1",
        )
