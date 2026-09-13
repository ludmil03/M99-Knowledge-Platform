from __future__ import annotations

from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import re
from typing import Any, Iterable

SCHEMA = "m99.phase46.r7a.calenda_evidence_governance.v1"

_COLOR_WORDS = {
    "blue","navy","black","white","red","green","yellow","orange","purple","pink","grey","gray",
    "royal","sky","burgundy","wine","natural","beige","brown","khaki","lime","aqua","turquoise",
    "син","тъмносин","черен","бял","червен","зелен","жълт","оранжев","лилав","розов","сив",
    "бордо","кафяв","бежов","светлосин","светло-син","тъмно-син",
}
_SIZE_WORDS = {
    "xxs","xs","s","m","l","xl","xxl","xxxl","2xl","3xl","4xl","5xl",
    "6","8","10","12","14","16","18","20","22","24","26","28","30","32","34","36","38","40",
    "42","44","46","48","50","52","54","56","58","60","62","64",
}

def _norm(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v or "").strip()).casefold()

def _compact(v: Any) -> str:
    return re.sub(r"[^a-z0-9а-я]+", "", _norm(v), flags=re.I)

def calenda_product_id_from_url(url: str) -> str:
    m = re.search(r"/products/(\d+)", str(url or ""))
    return m.group(1) if m else ""

def looks_like_color_token(value: Any, *, known_colors: Iterable[Any] = ()) -> bool:
    raw = _norm(value)
    if not raw:
        return False
    compact = _compact(raw)
    known = {_compact(x) for x in known_colors if _compact(x)}
    if compact in known:
        return True
    tokens = [t for t in re.split(r"[\s/_-]+", raw) if t]
    if len(tokens) <= 3 and all(t in _COLOR_WORDS or re.fullmatch(r"\d{1,3}", t or "") for t in tokens):
        return any(t in _COLOR_WORDS for t in tokens)
    return raw in _COLOR_WORDS

def looks_like_size_token(value: Any) -> bool:
    raw = _norm(value)
    return raw in _SIZE_WORDS

def looks_like_unsafe_reference(value: Any, *, known_colors: Iterable[Any] = ()) -> bool:
    raw = _norm(value)
    if not raw:
        return True
    if looks_like_color_token(raw, known_colors=known_colors) or looks_like_size_token(raw):
        return True
    if raw in {"unknown","n/a","none","null","-","—"}:
        return True
    return False

def _get(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def _variants(obj: Any) -> list[dict]:
    vals = _get(obj, "variants", []) or []
    out = []
    for x in vals:
        if isinstance(x, dict):
            out.append(dict(x))
        else:
            out.append({
                "value": getattr(x, "value", None),
                "label": getattr(x, "label", None),
                "code": getattr(x, "code", None),
                "image_url": getattr(x, "image_url", None),
                "sizes": getattr(x, "sizes", None),
            })
    return out

def known_variant_colors(obj: Any) -> list[str]:
    out = []
    for v in _variants(obj):
        for k in ("value","label","color","colour","name"):
            val = v.get(k)
            if val:
                out.append(str(val))
    return out

def classify_identifier_roles(
    supplier: Any,
    *,
    manufacturer_evidence: dict | None = None,
) -> dict:
    manufacturer_evidence = manufacturer_evidence or {}
    url = _get(supplier, "url", "") or _get(supplier, "source_url", "")
    calenda_id = (
        str(_get(supplier, "calenda_product_id", "") or _get(supplier, "product_id", "") or "").strip()
        or calenda_product_id_from_url(url)
    )
    colors = known_variant_colors(supplier)
    raw_supplier_ref = str(
        _get(supplier, "supplier_reference", "")
        or _get(supplier, "supplier_ref", "")
        or _get(supplier, "sku", "")
        or ""
    ).strip()

    supplier_ref = ""
    supplier_ref_status = "MISSING"
    if raw_supplier_ref:
        if looks_like_unsafe_reference(raw_supplier_ref, known_colors=colors):
            supplier_ref_status = "REJECTED_NON_IDENTIFIER_TOKEN"
        else:
            supplier_ref = raw_supplier_ref
            supplier_ref_status = "SUPPLIER_REFERENCE_CANDIDATE"

    exact = (
        manufacturer_evidence.get("status") == "OPERATOR_CONFIRMED_EXACT"
        and manufacturer_evidence.get("manufacturer_product_code_status") == "VERIFIED_EXACT_REFERENCE"
    )
    manufacturer_mpn = str(manufacturer_evidence.get("manufacturer_product_code") or "").strip() if exact else ""

    return {
        "calenda_product_id": calenda_id,
        "supplier_reference_raw": raw_supplier_ref,
        "supplier_reference": supplier_ref,
        "supplier_reference_status": supplier_ref_status,
        "manufacturer_base_mpn": manufacturer_mpn,
        "manufacturer_mpn_status": "VERIFIED_EXACT_REFERENCE" if manufacturer_mpn else "UNRESOLVED",
        "canonical_m99_reference": str(_get(supplier, "canonical_m99_reference", "") or "").strip(),
        "manufacturer_resolution_required": not bool(manufacturer_mpn),
    }

def classify_variant_images(supplier: Any) -> list[dict]:
    variants = _variants(supplier)
    url_to_colors: dict[str, set[str]] = {}
    prepared = []
    for i, v in enumerate(variants):
        color = str(v.get("value") or v.get("label") or v.get("color") or v.get("colour") or "").strip()
        image = str(v.get("image_url") or v.get("image") or "").strip()
        explicit = bool(v.get("image_association_exact") or v.get("explicit_image_for_variant"))
        prepared.append((i, color, image, explicit, v))
        if image:
            url_to_colors.setdefault(image, set()).add(_norm(color))

    out = []
    for i, color, image, explicit, v in prepared:
        if not image:
            provenance = "NO_VARIANT_IMAGE_EVIDENCE"
        elif len(url_to_colors.get(image, set())) > 1:
            provenance = "SUPPLIER_GENERIC_SHARED"
        elif explicit:
            provenance = "SUPPLIER_VARIANT_EXACT"
        else:
            provenance = "SUPPLIER_VARIANT_CANDIDATE"
        out.append({
            "index": i,
            "color": color,
            "variant_code": str(v.get("code") or "").strip(),
            "image_url": image,
            "image_provenance": provenance,
            "safe_as_exact_variant_image": provenance == "SUPPLIER_VARIANT_EXACT",
        })
    return out

def build_calenda_evidence_snapshot(
    supplier: Any,
    *,
    manufacturer_evidence: dict | None = None,
) -> dict:
    ids = classify_identifier_roles(supplier, manufacturer_evidence=manufacturer_evidence)
    images = classify_variant_images(supplier)
    warnings = []
    if ids["supplier_reference_status"] == "REJECTED_NON_IDENTIFIER_TOKEN":
        warnings.append("SUPPLIER_REFERENCE_REJECTED_NON_IDENTIFIER_TOKEN")
    if not ids["manufacturer_base_mpn"]:
        warnings.append("MANUFACTURER_MPN_UNRESOLVED")
    if any(x["image_provenance"] == "SUPPLIER_GENERIC_SHARED" for x in images):
        warnings.append("VARIANT_IMAGES_SHARED_ACROSS_COLORS")
    if any(x["image_provenance"] == "NO_VARIANT_IMAGE_EVIDENCE" for x in images):
        warnings.append("VARIANT_IMAGE_EVIDENCE_MISSING")

    return {
        "schema": SCHEMA,
        "source_role": "SUPPLIER_EVIDENCE_ONLY",
        "identifiers": ids,
        "variant_images": images,
        "warnings": list(dict.fromkeys(warnings)),
        "rules": {
            "supplier_reference_never_becomes_manufacturer_mpn_implicitly": True,
            "manufacturer_mpn_requires_exact_manufacturer_evidence": True,
            "shared_image_never_claimed_as_exact_color_image": True,
            "missing_manufacturer_mpn_does_not_invent_code": True,
        },
    }

def safe_supplier_reference_for_display(supplier: Any) -> str:
    return classify_identifier_roles(supplier)["supplier_reference"]

def validate_snapshot(snapshot: dict) -> None:
    ids = snapshot.get("identifiers") or {}
    if ids.get("supplier_reference_status") == "REJECTED_NON_IDENTIFIER_TOKEN" and ids.get("supplier_reference"):
        raise ValueError("Rejected supplier token leaked into supplier_reference")
    if ids.get("manufacturer_mpn_status") != "VERIFIED_EXACT_REFERENCE" and ids.get("manufacturer_base_mpn"):
        raise ValueError("Unverified manufacturer MPN leaked into canonical evidence")
    for v in snapshot.get("variant_images") or []:
        if v.get("image_provenance") == "SUPPLIER_GENERIC_SHARED" and v.get("safe_as_exact_variant_image"):
            raise ValueError("Shared image mislabeled as exact variant image")
