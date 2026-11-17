"""Product readback must prove the reviewed facts, not only a successful API call."""
import xml.etree.ElementTree as ET

import pytest

from app.services import stage5_final_ui_publish as publish


def payload():
    return """<prestashop><product>
      <reference>M99 100020</reference><id_category_default>26</id_category_default>
      <price>48.441667</price><id_tax_rules_group>3</id_tax_rules_group>
      <active>0</active><available_for_order>0</available_for_order><visibility>none</visibility>
      <id_manufacturer>8</id_manufacturer><weight>0.570</weight><ean13/>
      <name><language id="7">Safety shoe</language><language id="4">Защитна обувка</language></name>
      <description><language id="7">&lt;p&gt;Verified EN facts.&lt;/p&gt;</language><language id="4">Проверени факти.</language></description>
      <description_short><language id="7">Short EN.</language><language id="4">Кратко BG.</language></description_short>
      <meta_title><language id="7">EN title</language><language id="4">BG заглавие</language></meta_title>
      <meta_description><language id="7">EN metadata.</language><language id="4">BG метаданни.</language></meta_description>
      <link_rewrite><language id="7">safety-shoe</language><language id="4">zashtitna-obuvka</language></link_rewrite>
      <associations><categories><category><id>26</id></category><category><id>29</id></category></categories>
        <images><image><id>301</id></image></images>
        <combinations><combination><id>401</id></combination><combination><id>402</id></combination></combinations>
      </associations>
    </product></prestashop>"""


def response():
    root = ET.fromstring(payload())
    ET.SubElement(root.find("product"), "id").text = "2043"
    return root


def check(monkeypatch, actual, expected=None):
    calls = []

    def get(cfg, path):
        calls.append(path)
        return ET.tostring(actual, encoding="unicode")

    monkeypatch.setattr(publish, "_get_once", get)
    assert publish._readback(None, "2043", "M99 100020", expected or payload()) is True
    assert calls == ["/api/products/2043"]


def test_equal_reviewed_product_passes_with_server_generated_fields(monkeypatch):
    actual = response()
    ET.SubElement(actual.find("product"), "date_add").text = "2026-11-17"
    check(monkeypatch, actual)


@pytest.mark.parametrize("field", [
    "name", "description", "description_short", "meta_title", "meta_description", "link_rewrite",
])
def test_changed_localized_field_is_not_a_success(monkeypatch, field):
    actual = response()
    actual.find(f"product/{field}/language").text = "Wrong customer-facing value"
    with pytest.raises(publish.ReadbackFailed, match="READBACK_MISMATCH:" + field):
        check(monkeypatch, actual)


@pytest.mark.parametrize("kind", ["wrong_id", "missing", "duplicate", "extra"])
def test_language_identity_and_completeness_are_checked(monkeypatch, kind):
    actual = response()
    name = actual.find("product/name")
    if kind == "wrong_id":
        name[0].set("id", "99")
    elif kind == "missing":
        name.remove(name[0])
    elif kind == "duplicate":
        name[1].set("id", name[0].get("id"))
    else:
        ET.SubElement(name, "language", {"id": "99"}).text = "Unexpected language"
    with pytest.raises(publish.ReadbackFailed):
        check(monkeypatch, actual)


@pytest.mark.parametrize("association", ["categories/category", "images/image", "combinations/combination"])
def test_missing_or_changed_association_is_blocked(monkeypatch, association):
    actual = response()
    actual.find("product/associations/" + association + "/id").text = "999"
    with pytest.raises(publish.ReadbackFailed, match="READBACK_MISMATCH:associations"):
        check(monkeypatch, actual)


def test_association_and_language_order_and_numeric_format_are_not_changes(monkeypatch):
    actual = response()
    product = actual.find("product")
    product.find("price").text = "48.441667000"
    product.find("weight").text = "0.57"
    product.find("id_tax_rules_group").text = "03"
    for node in product:
        node[:] = reversed(list(node))
    categories = product.find("associations/categories")
    categories[:] = reversed(list(categories))
    product[:] = reversed(list(product))
    check(monkeypatch, actual)


def test_category_only_payload_preserves_unasserted_remote_assets(monkeypatch):
    expected = ET.fromstring(payload())
    associations = expected.find("product/associations")
    associations.remove(associations.find("images"))
    associations.remove(associations.find("combinations"))
    check(monkeypatch, response(), ET.tostring(expected, encoding="unicode"))


def test_extra_category_is_a_membership_mismatch(monkeypatch):
    actual = response()
    category = ET.SubElement(actual.find("product/associations/categories"), "category")
    ET.SubElement(category, "id").text = "30"
    with pytest.raises(publish.ReadbackFailed, match="READBACK_MISMATCH:associations/categories"):
        check(monkeypatch, actual)


@pytest.mark.parametrize("field,value", [
    ("price", "0"), ("price", "NaN"), ("price", "Infinity"),
    ("id_tax_rules_group", "0"), ("id_manufacturer", "9"), ("active", "1"),
    ("available_for_order", "1"), ("visibility", "both"), ("weight", "0.7"),
])
def test_commercial_identity_and_safety_facts_are_verified(monkeypatch, field, value):
    actual = response()
    actual.find("product/" + field).text = value
    with pytest.raises(publish.ReadbackFailed):
        check(monkeypatch, actual)


def test_missing_reviewed_field_is_blocked(monkeypatch):
    actual = response()
    product = actual.find("product")
    product.remove(product.find("name"))
    with pytest.raises(publish.ReadbackFailed, match="READBACK_FIELD_MISSING:name"):
        check(monkeypatch, actual)


def test_remote_product_id_is_verified(monkeypatch):
    actual = response()
    actual.find("product/id").text = "2042"
    with pytest.raises(publish.ReadbackFailed, match="PRODUCT_ID_READBACK_MISMATCH"):
        check(monkeypatch, actual)


def test_duplicate_scalar_does_not_hide_mismatch(monkeypatch):
    actual = response()
    ET.SubElement(actual.find("product"), "price").text = "0"
    with pytest.raises(publish.ReadbackFailed, match="READBACK_FIELD_DUPLICATED:price"):
        check(monkeypatch, actual)


def test_safety_fields_are_required_before_network(monkeypatch):
    expected = ET.fromstring(payload())
    expected.find("product").remove(expected.find("product/active"))
    monkeypatch.setattr(publish, "_get_once", lambda *a: pytest.fail("No network expected"))
    with pytest.raises(publish.ReadbackFailed, match="SAFETY_FIELD_NOT_IN_PAYLOAD:active"):
        publish._readback(None, "2043", "M99 100020", ET.tostring(expected, encoding="unicode"))


def test_invalid_xml_is_reported_as_readback_failure(monkeypatch):
    monkeypatch.setattr(publish, "_get_once", lambda *a: "not XML")
    with pytest.raises(publish.ReadbackFailed, match="PRODUCT_READBACK_INVALID_XML"):
        publish._readback(None, "2043", "M99 100020", payload())
