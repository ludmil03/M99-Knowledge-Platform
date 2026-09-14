from __future__ import annotations

import json
import re
from dataclasses import asdict
from urllib.parse import urlparse

from app.models.entities import AuditLog
from app.services.v073_phase46.canonical_live_pilot import (
    CONFIRMATION as CANONICAL_PILOT_CONFIRMATION,
    CanonicalPilotError,
    CanonicalPilotResult,
    publish_canonical_pilot,
    validate_preview,
)

R7K_CONFIRMATION = "PUBLISH PALLTEX CONTROLLED PRODUCT TO M99.EU"
R7K_ACTION = "PHASE46_R7K_PALLTEX_CONTROLLED_PUBLISH"
_ALLOWED_PALLTEX_HOSTS = {"palltex.bg", "www.palltex.bg"}
_BLOCKED_CANONICAL_REFERENCES = {"M99-1", "M99-2"}
_M99_RE = re.compile(r"^(?:M99 [0-9]{6}|M99-[0-9]+)$")


class PalltexControlledPublishError(RuntimeError):
    pass


def _text(value) -> str:
    return str(value or "").strip()


def _is_palltex_product_url(url: str) -> bool:
    try:
        parsed = urlparse(_text(url))
    except Exception:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    return (
        parsed.scheme.lower() == "https"
        and host in _ALLOWED_PALLTEX_HOSTS
        and "/p/" in (parsed.path or "")
        and re.search(r"/\d+/?$", parsed.path or "") is not None
    )


def validate_palltex_controlled_context(*, job, item, preview: dict, confirmation: str) -> dict:
    """Fail-closed Palltex-specific gate before the proven canonical publisher.

    This gate does not perform a channel write. It proves that the selected DRAFT
    item is a Palltex product, that canonical identity is permanent/fresh enough
    for the first controlled path, and that supplier/variant evidence remains
    separate from M99 physical stock semantics.
    """
    if _text(confirmation) != R7K_CONFIRMATION:
        raise PalltexControlledPublishError(
            f"Exact confirmation required: {R7K_CONFIRMATION}"
        )

    if _text(getattr(job, "status", "")).upper() != "DRAFT":
        raise PalltexControlledPublishError("R7K requires a DRAFT ImportJob.")

    source_url = _text(getattr(item, "source_url", ""))
    if not _is_palltex_product_url(source_url):
        raise PalltexControlledPublishError(
            "R7K is Palltex-only. Selected item must carry an HTTPS palltex.bg product URL."
        )

    try:
        validate_preview(preview)
    except CanonicalPilotError as exc:
        raise PalltexControlledPublishError(str(exc)) from exc

    if int(preview.get("job_id") or 0) != int(getattr(job, "id", 0)):
        raise PalltexControlledPublishError("Canonical preview/job mismatch.")
    if int(preview.get("item_id") or 0) != int(getattr(item, "id", 0)):
        raise PalltexControlledPublishError("Canonical preview/item mismatch.")

    ids = dict(preview.get("identifiers") or {})
    canonical_ref = _text(ids.get("channel_reference"))
    supplier_ref = _text(ids.get("supplier_reference"))
    item_supplier_ref = _text(getattr(item, "supplier_reference", ""))

    if not _M99_RE.fullmatch(canonical_ref):
        raise PalltexControlledPublishError("Permanent canonical M99 reference is invalid.")
    if canonical_ref in _BLOCKED_CANONICAL_REFERENCES:
        raise PalltexControlledPublishError(
            f"Canonical reference {canonical_ref} is protected historical identity and must never be republished."
        )
    if not supplier_ref:
        raise PalltexControlledPublishError("Verified Palltex Supplier Reference is missing.")
    if item_supplier_ref and supplier_ref != item_supplier_ref:
        raise PalltexControlledPublishError(
            "Palltex Supplier Reference mismatch between DRAFT item and canonical preview."
        )

    variants = dict(preview.get("variants") or {})
    groups = int(variants.get("groups") or 0)
    rows = list(variants.get("rows") or [])
    rows_count = int(variants.get("rows_count") or 0)
    if groups < 1 or rows_count < 1 or not rows:
        raise PalltexControlledPublishError("Palltex variant evidence is missing.")
    if rows_count != len(rows):
        raise PalltexControlledPublishError("Palltex variant row count/readback mismatch.")

    for row in rows:
        if not isinstance(row, dict):
            raise PalltexControlledPublishError("Palltex variant row has invalid structure.")
        if not _text(row.get("size")):
            raise PalltexControlledPublishError("Palltex variant row is missing size evidence.")
        # Availability is evidence only. R7K deliberately refuses any M99-owned
        # quantity field in the canonical preview rows.
        for forbidden in ("quantity", "stock", "physical_stock", "m99_stock"):
            if forbidden in row and _text(row.get(forbidden)):
                raise PalltexControlledPublishError(
                    "Palltex supplier availability must not be converted into M99 physical stock."
                )

    return {
        "source_url": source_url,
        "canonical_reference": canonical_ref,
        "supplier_reference": supplier_ref,
        "variant_groups": groups,
        "variant_rows": rows_count,
        "image_count": int((preview.get("images") or {}).get("count") or 0),
    }


def publish_palltex_controlled(
    db,
    *,
    user,
    job,
    item,
    preview: dict,
    category_id: int,
    price_override: str,
    confirmation: str,
) -> CanonicalPilotResult:
    gate = validate_palltex_controlled_context(
        job=job, item=item, preview=preview, confirmation=confirmation
    )

    try:
        result = publish_canonical_pilot(
            db,
            user=user,
            job=job,
            item=item,
            preview=preview,
            category_id=category_id,
            price_override=price_override,
            confirmation=CANONICAL_PILOT_CONFIRMATION,
        )
    except CanonicalPilotError as exc:
        raise PalltexControlledPublishError(str(exc)) from exc

    if (
        _text(result.active) != "0"
        or _text(result.available_for_order) != "0"
        or _text(result.visibility) != "none"
    ):
        raise PalltexControlledPublishError(
            "R7K postcondition failed: published product is not hidden/non-orderable."
        )

    # Add a Palltex-specific audit record after the generic canonical publisher
    # has completed strict API truth verification and its own audit.
    details = {
        **gate,
        "channel_product_id": _text(result.product_id),
        "category_id": _text(result.category_id),
        "price": _text(result.price),
        "created": bool(result.created),
        "active": _text(result.active),
        "available_for_order": _text(result.available_for_order),
        "visibility": _text(result.visibility),
        "api_truth_verified": bool(result.api_truth_verified),
        "correlation_id": _text(result.correlation_id),
        "secret_logged": False,
    }
    db.add(
        AuditLog(
            user_id=int(user.id),
            action=R7K_ACTION,
            entity_type="ImportJob",
            entity_id=str(job.id),
            result="OK" if result.api_truth_verified else "NOT_VERIFIED",
            details=json.dumps(details, ensure_ascii=False, sort_keys=True),
        )
    )
    db.commit()
    return result
