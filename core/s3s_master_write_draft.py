from __future__ import annotations
import xml.etree.ElementTree as ET


def _lang_node(parent, lang_id: str):
    for lang in parent.findall(".//language"):
        if str(lang.attrib.get("id")) == str(lang_id):
            return lang
    return None


def _set_lang(product, tag, bg, en):
    node = product.find(tag)
    if node is None:
        raise ValueError(f"Existing product missing required multilingual field: {tag}")
    bg_node = _lang_node(node, "1")
    en_node = _lang_node(node, "2")
    if bg_node is None or en_node is None:
        raise ValueError(f"Existing product missing BG/EN language nodes in {tag}")
    bg_node.text = bg
    en_node.text = en


def _category_ids(product):
    return [
        (x.findtext("id") or "").strip()
        for x in product.findall("./associations/categories/category")
        if (x.findtext("id") or "").strip()
    ]


def mutate_master_to_review_draft(
    original_xml: str,
    *,
    content: dict,
    review_category_id: str,
    change_name: bool = False,
) -> tuple[str, dict]:
    root = ET.fromstring(original_xml)
    product = root.find(".//product")
    if product is None:
        raise ValueError("Product node missing")

    pid = (product.findtext("id") or "").strip()
    if pid != "2076":
        raise ValueError(f"WRITE_DRAFT is hard-locked to product ID 2076, got {pid}")

    # Capture protected identity before mutation.
    protected = {
        "product_id": pid,
        "reference": (product.findtext("reference") or "").strip(),
        "name_bg": (_lang_node(product.find("name"), "1").text or "").strip(),
        "name_en": (_lang_node(product.find("name"), "2").text or "").strip(),
        "slug_bg": (_lang_node(product.find("link_rewrite"), "1").text or "").strip(),
        "slug_en": (_lang_node(product.find("link_rewrite"), "2").text or "").strip(),
        "original_category_ids": _category_ids(product),
    }

    # Draft means inactive until reviewed.
    active = product.find("active")
    if active is None:
        active = ET.SubElement(product, "active")
    active.text = "0"

    # Name is protected by default. SEO/content fields may be enriched.
    if change_name:
        _set_lang(
            product, "name",
            content["bg"]["name"],
            content["en"]["name"],
        )

    _set_lang(
        product, "meta_title",
        content["bg"]["seo_title"],
        content["en"]["seo_title"],
    )
    _set_lang(
        product, "meta_description",
        content["bg"]["meta_description"],
        content["en"]["meta_description"],
    )
    _set_lang(
        product, "description_short",
        content["bg"]["short_description"],
        content["en"]["short_description"],
    )
    _set_lang(
        product, "description",
        content["bg"]["long_description"],
        content["en"]["long_description"],
    )

    # URL protection: link_rewrite is intentionally never touched.
    link = product.find("link_rewrite")
    if link is None:
        raise ValueError("link_rewrite missing; update blocked")

    # Central operator queue. Existing categories remain and review category is added.
    associations = product.find("associations")
    if associations is None:
        associations = ET.SubElement(product, "associations")
    categories = associations.find("categories")
    if categories is None:
        categories = ET.SubElement(associations, "categories")

    existing_ids = _category_ids(product)
    if review_category_id not in existing_ids:
        category = ET.SubElement(categories, "category")
        ET.SubElement(category, "id").text = str(review_category_id)

    written_ids = _category_ids(product)

    result = ET.tostring(
        root, encoding="utf-8", xml_declaration=True
    ).decode("utf-8")

    return result, {
        "protected_identity": protected,
        "write_category_ids": written_ids,
        "review_category_id": str(review_category_id),
        "name_changed": bool(change_name),
        "slug_changed": False,
        "url_policy": "KEEP",
        "reference_policy": "KEEP",
        "active_after_write": False,
    }
