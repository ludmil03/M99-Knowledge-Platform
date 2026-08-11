from __future__ import annotations
import xml.etree.ElementTree as ET


def _lang(root, tag, lang_id):
    node = root.find(f".//{tag}")
    if node is None:
        return None
    for lang in node.findall(".//language"):
        if str(lang.attrib.get("id")) == str(lang_id):
            return (lang.text or "").strip()
    return None


def summarize_product_xml(product_xml: str) -> dict:
    root = ET.fromstring(product_xml)

    def text(tag):
        node = root.find(f".//{tag}")
        return (node.text or "").strip() if node is not None and node.text else None

    categories = [
        (x.findtext("id") or "").strip()
        for x in root.findall(".//associations/categories/category")
        if (x.findtext("id") or "").strip()
    ]

    combinations = [
        (x.findtext("id") or "").strip()
        for x in root.findall(".//associations/combinations/combination")
        if (x.findtext("id") or "").strip()
    ]

    images = [
        (x.findtext("id") or "").strip()
        for x in root.findall(".//associations/images/image")
        if (x.findtext("id") or "").strip()
    ]

    return {
        "id": text("id"),
        "reference": text("reference"),
        "ean13": text("ean13"),
        "active": text("active"),
        "price": text("price"),
        "id_category_default": text("id_category_default"),
        "date_add": text("date_add"),
        "date_upd": text("date_upd"),
        "name_bg": _lang(root, "name", 1),
        "name_en": _lang(root, "name", 2),
        "slug_bg": _lang(root, "link_rewrite", 1),
        "slug_en": _lang(root, "link_rewrite", 2),
        "description_short_bg": _lang(root, "description_short", 1),
        "description_short_en": _lang(root, "description_short", 2),
        "description_bg": _lang(root, "description", 1),
        "description_en": _lang(root, "description", 2),
        "categories": categories,
        "combination_ids": combinations,
        "image_ids": images,
        "combination_count": len(combinations),
        "image_count": len(images),
    }


def add_snapshot_quality(snapshot: dict) -> dict:
    s = dict(snapshot)
    score = 0
    reasons = []

    if s.get("active") == "1":
        score += 10
        reasons.append("ACTIVE")
    if s.get("reference"):
        score += 10
        reasons.append("HAS_REFERENCE")
    if s.get("description_bg"):
        score += 10
        reasons.append("HAS_BG_DESCRIPTION")
    if s.get("combination_count", 0) > 0:
        score += 15
        reasons.append("HAS_COMBINATIONS")
    if s.get("image_count", 0) > 0:
        score += 10
        reasons.append("HAS_IMAGES")
    if s.get("date_add"):
        score += 5
        reasons.append("HAS_DATE_ADD")

    s["snapshot_quality_score"] = score
    s["snapshot_quality_reasons"] = reasons
    return s
