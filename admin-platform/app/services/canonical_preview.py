from __future__ import annotations

import re
import unicodedata
from typing import Any


def _text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")[:128]


def canonical_name(title: str, supplier_reference: str) -> str:
    name = _text(title)
    ref = _text(supplier_reference)
    if ref:
        name = re.sub(rf"\s+{re.escape(ref)}\s*$", "", name, flags=re.I).strip()
    return name


def normalize_specifications(rows: list[dict] | None) -> list[dict]:
    result = []
    seen = set()
    for row in rows or []:
        name = _text(row.get("name"))
        value = _text(row.get("value"))
        if not name or not value:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append({"name": name, "value": value})
    return result


def normalize_variants(rows: list[dict] | None) -> list[dict]:
    result = []
    for row in rows or []:
        value = _text(row.get("value"))
        if not value:
            continue
        result.append({
            "type": _text(row.get("type") or "VARIANT"),
            "value": value,
            "availability": _text(row.get("availability") or "UNKNOWN"),
        })
    return result


def prepare_canonical_preview(product: dict, target_code: str = "m99eu") -> dict:
    """Build a read-only, evidence-grounded canonical preview.

    This function intentionally does NOT translate, publish, activate, write
    stock or mutate a channel. It only prepares operator-visible evidence.
    """
    ref = _text(product.get("supplier_reference"))
    name = canonical_name(product.get("title", ""), ref)
    specs = normalize_specifications(product.get("specifications"))
    variants = normalize_variants(product.get("variants"))
    images = list(dict.fromkeys(x for x in (product.get("images") or []) if x))
    description = _text(product.get("description"))

    blockers = []
    warnings = []
    if not name:
        blockers.append("CANONICAL_NAME_MISSING")
    if not ref:
        blockers.append("SUPPLIER_REFERENCE_MISSING")
    if not images:
        blockers.append("IMAGES_MISSING")
    if not specs:
        warnings.append("SPECIFICATIONS_SPARSE")
    if not variants:
        warnings.append("VARIANTS_NOT_DETECTED")
    warnings.append("MANUFACTURER_EVIDENCE_NOT_ATTACHED")
    warnings.append("FINAL_EN_CONTENT_NOT_GENERATED")

    heading_plan = [
        {"level": "H1", "text": name},
        {"level": "H2", "text": "Description"},
        {"level": "H2", "text": "Technical specifications"},
        {"level": "H2", "text": "Sizes and availability"},
        {"level": "H2", "text": "FAQ"},
    ]

    return {
        "status": "BLOCKED" if blockers else "PREVIEW_READY",
        "target": target_code,
        "publishable": False,
        "canonical_identity": {
            "name": name,
            "supplier_reference": ref,
        },
        "supplier_evidence": {
            "url": _text(product.get("url")),
            "title": _text(product.get("title")),
            "supplier_reference": ref,
            "price": _text(product.get("price_text")),
            "availability": _text(product.get("availability_text") or "UNKNOWN"),
            "description": description,
            "specifications": specs,
            "variants": variants,
            "images": images,
            "image_count": len(images),
        },
        "m99_draft": {
            "language": "EN",
            "translation_status": "NOT_GENERATED",
            "title_source": name,
            "h1_source": name,
            "slug_source": _slug(name),
            "meta_title_source": name[:60],
            "meta_description_source": description[:155],
            "heading_plan": heading_plan,
            "alt_text_source": [
                f"{name} - image {i + 1}" for i in range(len(images))
            ],
        },
        "quality_gate": {
            "blockers": blockers,
            "warnings": warnings,
            "operator_review_required": True,
            "website_write_allowed": False,
        },
    }
