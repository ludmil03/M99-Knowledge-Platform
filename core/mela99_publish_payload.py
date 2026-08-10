from __future__ import annotations

from dataclasses import dataclass
from html import escape


@dataclass
class PublishDocument:
    name_bg: str
    name_en: str
    short_bg: str
    short_en: str
    long_bg: str
    long_en: str
    meta_title_bg: str
    meta_title_en: str
    meta_description_bg: str
    meta_description_en: str
    reference: str
    category_id: int
    active: bool
    price_ex_vat: float | None = None


def _lang(value_bg: str, value_en: str) -> str:
    # PrestaShop XML language IDs used in this project:
    # 1 = Bulgarian, 2 = English.
    return (
        "<language id=\"1\"><![CDATA[" + value_bg + "]]></language>"
        "<language id=\"2\"><![CDATA[" + value_en + "]]></language>"
    )


def build_product_xml(
    doc: PublishDocument,
    existing_product_id: str | None = None,
    existing_link_rewrite_bg: str | None = None,
    existing_link_rewrite_en: str | None = None,
) -> str:
    if existing_product_id and (
        not existing_link_rewrite_bg or not existing_link_rewrite_en
    ):
        raise ValueError(
            "UPDATE requires existing BG and EN link_rewrite values; "
            "URL/slug must never be regenerated silently."
        )

    # New product slugs are generated once before first create.
    if not existing_product_id:
        raise ValueError(
            "CREATE payload requires explicit generated slugs via "
            "build_create_product_xml()."
        )

    price_xml = (
        f"<price>{doc.price_ex_vat:.6f}</price>"
        if doc.price_ex_vat is not None else ""
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
  <product>
    <id>{escape(str(existing_product_id))}</id>
    <active>{1 if doc.active else 0}</active>
    <reference><![CDATA[{doc.reference}]]></reference>
    {price_xml}
    <name>{_lang(doc.name_bg, doc.name_en)}</name>
    <link_rewrite>{_lang(existing_link_rewrite_bg, existing_link_rewrite_en)}</link_rewrite>
    <meta_title>{_lang(doc.meta_title_bg, doc.meta_title_en)}</meta_title>
    <meta_description>{_lang(doc.meta_description_bg, doc.meta_description_en)}</meta_description>
    <description_short>{_lang(doc.short_bg, doc.short_en)}</description_short>
    <description>{_lang(doc.long_bg, doc.long_en)}</description>
  </product>
</prestashop>
"""


def build_create_product_xml(
    doc: PublishDocument,
    slug_bg: str,
    slug_en: str,
) -> str:
    if not slug_bg or not slug_en:
        raise ValueError("CREATE requires explicit BG and EN slugs")

    price_xml = (
        f"<price>{doc.price_ex_vat:.6f}</price>"
        if doc.price_ex_vat is not None else ""
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
  <product>
    <active>{1 if doc.active else 0}</active>
    <reference><![CDATA[{doc.reference}]]></reference>
    {price_xml}
    <id_category_default>{doc.category_id}</id_category_default>
    <name>{_lang(doc.name_bg, doc.name_en)}</name>
    <link_rewrite>{_lang(slug_bg, slug_en)}</link_rewrite>
    <meta_title>{_lang(doc.meta_title_bg, doc.meta_title_en)}</meta_title>
    <meta_description>{_lang(doc.meta_description_bg, doc.meta_description_en)}</meta_description>
    <description_short>{_lang(doc.short_bg, doc.short_en)}</description_short>
    <description>{_lang(doc.long_bg, doc.long_en)}</description>
    <associations>
      <categories>
        <category><id>{doc.category_id}</id></category>
      </categories>
    </associations>
  </product>
</prestashop>
"""


def _set_language_values(parent, values_by_id):
    languages = parent.findall(".//language")
    if not languages:
        raise ValueError(f"No language nodes found for {parent.tag}")
    for lang in languages:
        lang_id = str(lang.attrib.get("id"))
        if lang_id in values_by_id and values_by_id[lang_id] is not None:
            lang.text = str(values_by_id[lang_id])


def mutate_existing_product_xml(
    original_xml: str,
    doc: PublishDocument,
    *,
    change_name: bool,
) -> str:
    """
    Mutate the complete current PrestaShop product snapshot.
    link_rewrite is intentionally never modified here.
    Product ID and current reference are also preserved.
    """
    import xml.etree.ElementTree as ET

    root = ET.fromstring(original_xml)
    product = root.find(".//product")
    if product is None:
        raise ValueError("Product node not found in existing XML snapshot")

    def child(tag):
        node = product.find(tag)
        if node is None:
            node = ET.SubElement(product, tag)
        return node

    child("active").text = "1" if doc.active else "0"

    # Existing reference / legacy identity is protected.
    # Only set a reference when it is truly empty.
    reference = child("reference")
    if not (reference.text or "").strip():
        reference.text = doc.reference

    if doc.price_ex_vat is not None:
        child("price").text = f"{doc.price_ex_vat:.6f}"

    if change_name:
        _set_language_values(
            child("name"),
            {"1": doc.name_bg, "2": doc.name_en},
        )

    _set_language_values(
        child("meta_title"),
        {"1": doc.meta_title_bg, "2": doc.meta_title_en},
    )
    _set_language_values(
        child("meta_description"),
        {
            "1": doc.meta_description_bg,
            "2": doc.meta_description_en,
        },
    )
    _set_language_values(
        child("description_short"),
        {"1": doc.short_bg, "2": doc.short_en},
    )
    _set_language_values(
        child("description"),
        {"1": doc.long_bg, "2": doc.long_en},
    )

    # Explicit invariant: link_rewrite is present but untouched.
    if product.find("link_rewrite") is None:
        raise ValueError(
            "Existing product has no link_rewrite; UPDATE blocked to protect URL"
        )

    return ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    ).decode("utf-8")
