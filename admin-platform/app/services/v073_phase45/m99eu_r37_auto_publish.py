from __future__ import annotations

import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

from sqlalchemy.orm import Session, object_session

from app.models.entities import AuditLog, ImportJob, ImportJobItem, Product, User
from app.services.v073_phase45.m99eu_operator_single_publish import (
    Candidate,
    PublishSafetyError,
    _curl,
    _find_existing,
    active_languages,
    build_payload,
    ensure_category,
)

DEFAULT_CATEGORY_ID = 26
ENABLE_ENV = "M99EU_AUTO_PUBLISH_ENABLED"
API_KEY_ENV = "M99EU_API_KEY"
CATEGORY_ENV = "M99EU_CATEGORY_ID"

R1_CONFIRMATION = "PUBLISH ONE PRODUCT"
M99_REFERENCE_RE = re.compile(r"^M99-[0-9]+$")

# R1 FINAL proves a real channel write without exposing the pilot to customers.
PILOT_ACTIVE = "1"
PILOT_AVAILABLE_FOR_ORDER = "0"
PILOT_VISIBILITY = "none"


class AutoPublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class AutoPublishConfig:
    enabled: bool
    api_key: str
    category_id: int


@dataclass(frozen=True)
class FinalPublishResult:
    created: bool
    product_id: str
    reference: str
    active: str
    available_for_order: str
    visibility: str
    category_id: str
    http_status: str
    correlation_id: str


def load_config(category_id: int | None = None) -> AutoPublishConfig:
    enabled = os.getenv(ENABLE_ENV, "").strip() == "1"
    api_key = os.getenv(API_KEY_ENV, "").strip()
    if not enabled:
        raise AutoPublishError(
            "Automatic m99.eu publishing is disabled. "
            "Set M99EU_AUTO_PUBLISH_ENABLED=1 in the Windows User environment."
        )
    if not re.fullmatch(r"[A-Za-z0-9]{32}", api_key):
        raise AutoPublishError(
            "M99EU_API_KEY is missing or invalid. It must be exactly 32 alphanumeric characters."
        )

    raw_category = str(
        category_id
        if category_id is not None
        else os.getenv(CATEGORY_ENV, str(DEFAULT_CATEGORY_ID))
    ).strip()
    try:
        target_category = int(raw_category)
    except ValueError as exc:
        raise AutoPublishError("M99EU_CATEGORY_ID must be a positive integer.") from exc
    if target_category <= 0:
        raise AutoPublishError("m99.eu category ID must be a positive integer.")
    return AutoPublishConfig(True, api_key, target_category)


def _price_from_supplier_product(data: dict[str, Any]) -> str:
    raw = str(data.get("price_text") or "").strip()
    if not raw:
        return ""
    normalized = (
        raw.replace("\xa0", " ")
        .replace("BGN", "")
        .replace("EUR", "")
        .replace("€", "")
    )
    match = re.search(r"(?<!\d)(\d+(?:[.,]\d{1,4})?)(?!\d)", normalized)
    if not match:
        return ""
    try:
        value = Decimal(match.group(1).replace(",", "."))
    except (InvalidOperation, ValueError):
        return ""
    return f"{value:.2f}" if value > 0 else ""


def _iter_identity_values(value: Any, depth: int = 0) -> Iterable[str]:
    if depth > 5 or value is None:
        return
    explicit_keys = {
        "m99_reference",
        "canonical_reference",
        "resolved_m99_reference",
        "canonical_m99_reference",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in explicit_keys:
                yield str(child or "").strip()
            elif isinstance(child, (dict, list, tuple)):
                yield from _iter_identity_values(child, depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for child in value:
            yield from _iter_identity_values(child, depth + 1)
        return
    for attr in explicit_keys:
        if hasattr(value, attr):
            yield str(getattr(value, attr) or "").strip()


def canonical_reference_from_identity_context(
    *,
    identity_result: Any,
    job: ImportJob | None = None,
) -> str:
    candidates: set[str] = set()
    for raw in _iter_identity_values(identity_result):
        if M99_REFERENCE_RE.fullmatch(raw):
            candidates.add(raw)

    if job is not None:
        for attr in (
            "m99_reference",
            "canonical_reference",
            "resolved_m99_reference",
            "canonical_m99_reference",
        ):
            if hasattr(job, attr):
                raw = str(getattr(job, attr) or "").strip()
                if M99_REFERENCE_RE.fullmatch(raw):
                    candidates.add(raw)

    if not candidates:
        raise AutoPublishError(
            "Identity resolver created the DRAFT but did not expose a permanent canonical "
            "M99 reference. R1 FINAL refuses to publish with a provisional ImportJobItem reference."
        )
    if len(candidates) != 1:
        raise AutoPublishError(
            "Identity context contains multiple canonical M99 references: "
            + ", ".join(sorted(candidates))
        )
    return next(iter(candidates))


def candidate_from_supplier_product(
    item: ImportJobItem,
    supplier_product: dict[str, Any],
    *,
    canonical_reference: str,
) -> Candidate:
    if not M99_REFERENCE_RE.fullmatch(str(canonical_reference or "").strip()):
        raise AutoPublishError(
            "Permanent canonical M99 reference is missing or invalid; expected M99- + digits."
        )

    title = str(
        supplier_product.get("title")
        or supplier_product.get("name")
        or item.source_title
        or ""
    ).strip()
    supplier_ref = str(
        supplier_product.get("supplier_reference")
        or item.supplier_reference
        or ""
    ).strip()
    description = str(supplier_product.get("description") or "").strip()
    source_url = str(supplier_product.get("url") or item.source_url or "").strip()
    price = _price_from_supplier_product(supplier_product)

    blockers: list[str] = []
    if not title:
        blockers.append("Missing hydrated product title")
    if not supplier_ref:
        blockers.append("Missing supplier reference / SKU")
    if not price:
        blockers.append("Missing or invalid positive price")

    # Candidate's legacy field name is provisional_m99_reference, but in R1 FINAL
    # it contains only the permanent canonical reference proven by Identity.
    return Candidate(
        item_id=int(item.id),
        title=title or f"Import item #{item.id}",
        supplier_reference=supplier_ref,
        price=price,
        description=description,
        source_url=source_url,
        provisional_m99_reference=canonical_reference,
        publishable=not blockers,
        blockers=tuple(blockers),
    )


def _pilot_payload(
    candidate: Candidate,
    category_id: int,
    langs: list[tuple[str, str]],
) -> str:
    payload = build_payload(candidate, category_id, langs)

    expected_active = "<active><![CDATA[0]]></active>"
    expected_order = "<available_for_order><![CDATA[0]]></available_for_order>"
    expected_visibility = "<visibility><![CDATA[none]]></visibility>"

    if expected_active not in payload:
        raise AutoPublishError(
            "Base m99.eu payload contract changed: inactive flag not found."
        )
    if expected_order not in payload:
        raise AutoPublishError(
            "Base m99.eu payload contract changed: available_for_order=0 not found."
        )
    if expected_visibility not in payload:
        raise AutoPublishError(
            "Base m99.eu payload contract changed: visibility=none not found. "
            "R1 FINAL refuses a potentially public first-product write."
        )

    payload = payload.replace(
        expected_active,
        "<active><![CDATA[1]]></active>",
        1,
    )
    # available_for_order remains 0 and visibility remains none by design.
    return payload


def _xml_text(root: ET.Element, tag: str) -> str:
    node = root.find(f".//{tag}")
    return (node.text or "").strip() if node is not None else ""


def readback_publish_state(api_key: str, product_id: str) -> tuple[str, str, str, str, str]:
    status, content = _curl(api_key, f"/api/products/{int(product_id)}")
    if status != "200":
        raise AutoPublishError(f"Read-back failed with HTTP {status}.")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise AutoPublishError("Read-back returned invalid XML.") from exc

    return (
        _xml_text(root, "reference"),
        _xml_text(root, "active"),
        _xml_text(root, "available_for_order"),
        _xml_text(root, "visibility"),
        _xml_text(root, "id_category_default"),
    )


def _validate_readback(
    *,
    state: tuple[str, str, str, str, str],
    canonical_reference: str,
    category_id: int,
) -> None:
    ref, active, available, visibility, category = state
    expected = (
        canonical_reference,
        PILOT_ACTIVE,
        PILOT_AVAILABLE_FOR_ORDER,
        PILOT_VISIBILITY,
        str(category_id),
    )
    if state != expected:
        raise AutoPublishError(
            "Read-back mismatch. "
            f"expected={expected!r}, actual={state!r}"
        )


def _audit(
    db: Session,
    *,
    user: User,
    job: ImportJob,
    action_result: str,
    details: dict[str, Any],
) -> None:
    safe = {
        **details,
        "job_id": int(job.id),
        "job_code": str(job.job_code),
        "channel": "m99.eu",
        "secret_logged": False,
    }
    db.add(
        AuditLog(
            user_id=int(user.id),
            action="PHASE46_R1_FINAL_PUBLISH_M99EU",
            entity_type="ImportJob",
            entity_id=str(job.id),
            result=action_result,
            details=json.dumps(safe, ensure_ascii=False, sort_keys=True),
        )
    )
    db.commit()


def _publish_pilot(
    candidate: Candidate,
    config: AutoPublishConfig,
) -> FinalPublishResult:
    if not candidate.publishable:
        raise AutoPublishError(
            "Selected DRAFT item is not publishable: " + "; ".join(candidate.blockers)
        )

    correlation_id = uuid.uuid4().hex
    langs = active_languages(config.api_key)
    ensure_category(config.api_key, config.category_id)

    existing = _find_existing(
        config.api_key,
        candidate.provisional_m99_reference,
    )
    if existing:
        state = readback_publish_state(config.api_key, existing)
        _validate_readback(
            state=state,
            canonical_reference=candidate.provisional_m99_reference,
            category_id=config.category_id,
        )
        ref, active, available, visibility, category = state
        return FinalPublishResult(
            False,
            str(existing),
            ref,
            active,
            available,
            visibility,
            category,
            "EXISTING_SAFE_PILOT",
            correlation_id,
        )

    payload = _pilot_payload(candidate, config.category_id, langs)
    status, content = _curl(
        config.api_key,
        "/api/products",
        method="POST",
        body=payload,
    )
    if status not in ("200", "201"):
        snippet = re.sub(r"\s+", " ", content)[:600]
        raise AutoPublishError(
            f"PrestaShop rejected create with HTTP {status}: {snippet}"
        )

    product_id = _find_existing(
        config.api_key,
        candidate.provisional_m99_reference,
    )
    if not product_id:
        raise AutoPublishError(
            "POST succeeded but product ID could not be recovered by canonical M99 reference."
        )

    state = readback_publish_state(config.api_key, product_id)
    _validate_readback(
        state=state,
        canonical_reference=candidate.provisional_m99_reference,
        category_id=config.category_id,
    )
    ref, active, available, visibility, category = state
    return FinalPublishResult(
        True,
        str(product_id),
        ref,
        active,
        available,
        visibility,
        category,
        status,
        correlation_id,
    )


def publish_draft_job(
    db: Session,
    *,
    user: User,
    job: ImportJob,
    identity_result: Any,
    supplier_product: dict[str, Any],
    category_id: int | None = None,
    confirmation: str,
) -> FinalPublishResult:
    if not bool(getattr(user, "is_superuser", False)):
        raise AutoPublishError(
            "Phase 4.6 R1 FINAL first live product is Super Admin only."
        )

    if str(confirmation or "").strip() != R1_CONFIRMATION:
        raise AutoPublishError(
            f"Exact confirmation required: {R1_CONFIRMATION}"
        )

    if str(job.status).upper() != "DRAFT":
        raise AutoPublishError(f"Expected DRAFT job, got {job.status!r}.")

    try:
        requested = set(json.loads(job.requested_targets or "[]"))
        authorized = set(json.loads(job.authorized_targets or "[]"))
    except Exception as exc:
        raise AutoPublishError("ImportJob target metadata is invalid.") from exc

    if "m99eu" not in requested or "m99eu" not in authorized:
        raise AutoPublishError("DRAFT job is not authorized for m99.eu.")

    rows = (
        db.query(ImportJobItem)
        .filter(
            ImportJobItem.import_job_id == int(job.id),
            ImportJobItem.selected.is_(True),
        )
        .order_by(ImportJobItem.id.asc())
        .all()
    )
    if len(rows) != 1:
        raise AutoPublishError(
            "R1 FINAL requires exactly one selected ImportJobItem; "
            f"found {len(rows)}."
        )

    canonical_reference = canonical_reference_from_identity_context(
        identity_result=identity_result,
        job=job,
    )
    config = load_config(category_id)
    candidate = candidate_from_supplier_product(
        rows[0],
        supplier_product,
        canonical_reference=canonical_reference,
    )

    try:
        result = _publish_pilot(candidate, config)
    except (AutoPublishError, PublishSafetyError) as exc:
        _audit(
            db,
            user=user,
            job=job,
            action_result="BLOCKED",
            details={
                "canonical_reference": canonical_reference,
                "supplier_reference": candidate.supplier_reference,
                "reason": str(exc),
                "created": False,
            },
        )
        if isinstance(exc, AutoPublishError):
            raise
        raise AutoPublishError(str(exc)) from exc

    _audit(
        db,
        user=user,
        job=job,
        action_result="OK",
        details={
            "canonical_reference": result.reference,
            "supplier_reference": candidate.supplier_reference,
            "channel_product_id": result.product_id,
            "active": result.active,
            "available_for_order": result.available_for_order,
            "visibility": result.visibility,
            "category_id": result.category_id,
            "created": result.created,
            "correlation_id": result.correlation_id,
        },
    )
    return result


# ---------------------------------------------------------------------------
# Phase 4.6 R1 FINAL post-DRAFT control-plane helpers.
# R37 remains frozen Identity -> DRAFT -> Canonical Preview and never calls these.
# ---------------------------------------------------------------------------

def _jsonish(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return text
    return value


def _object_snapshot(obj: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if obj is None:
        return result
    for key in (
        "m99_reference",
        "canonical_reference",
        "resolved_m99_reference",
        "canonical_m99_reference",
        "detection",
        "identity",
        "identity_result",
        "resolution",
        "metadata_json",
        "payload",
        "snapshot",
        "source_title",
        "supplier_reference",
        "source_url",
        "price_text",
        "description",
    ):
        if hasattr(obj, key):
            result[key] = _jsonish(getattr(obj, key))
    return result


def canonical_reference_from_draft(*, job: ImportJob, item: ImportJobItem) -> str:
    candidates: set[str] = set()
    contexts = [_object_snapshot(job), _object_snapshot(item)]
    for context in contexts:
        for raw in _iter_identity_values(context):
            if M99_REFERENCE_RE.fullmatch(raw):
                candidates.add(raw)
    if not candidates:
        # R7E: a governed canonical Product linked by matched_product_id is a durable
        # identity carrier. Supplier reference / MPN are never promoted to M99 identity.
        session = None
        try:
            session = object_session(item)
        except Exception:
            # SAFE R2: non-ORM / detached / test-double objects are equivalent
            # to "no attached Session" and must preserve the old safe BLOCK path.
            session = None
        matched_id = getattr(item, "matched_product_id", None)
        if session is not None and matched_id:
            linked = session.get(Product, int(matched_id))
            linked_ref = str(getattr(linked, "m99_reference", "") or "").strip() if linked else ""
            if M99_REFERENCE_RE.fullmatch(linked_ref):
                candidates.add(linked_ref)
    if not candidates:
        raise AutoPublishError(
            "DRAFT does not expose a permanent canonical M99 reference. "
            "Phase 4.6 R1 FINAL stops safely; R37 remains unchanged and no provisional reference is synthesized."
        )
    if len(candidates) != 1:
        raise AutoPublishError(
            "DRAFT exposes multiple permanent canonical M99 references: "
            + ", ".join(sorted(candidates))
        )
    return next(iter(candidates))


def _find_first_key(value: Any, keys: set[str], depth: int = 0) -> str:
    if depth > 6 or value is None:
        return ""
    value = _jsonish(value)
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in keys and child not in (None, ""):
                return str(child).strip()
        for child in value.values():
            found = _find_first_key(child, keys, depth + 1)
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for child in value:
            found = _find_first_key(child, keys, depth + 1)
            if found:
                return found
    return ""


def supplier_product_from_draft_item(item: ImportJobItem) -> dict[str, Any]:
    snapshot = _object_snapshot(item)
    detection = snapshot.get("detection")
    title = str(getattr(item, "source_title", "") or "").strip()
    supplier_reference = str(getattr(item, "supplier_reference", "") or "").strip()
    source_url = str(getattr(item, "source_url", "") or "").strip()
    return {
        "title": title or _find_first_key(detection, {"title", "name", "product_name"}),
        "supplier_reference": supplier_reference
        or _find_first_key(detection, {"supplier_reference", "reference", "sku"}),
        "url": source_url or _find_first_key(detection, {"url", "source_url", "product_url"}),
        "price_text": _find_first_key(
            detection, {"price_text", "price", "selling_price", "retail_price"}
        ),
        "description": _find_first_key(
            detection, {"description", "description_long", "long_description"}
        ),
    }


def eligible_draft_jobs(db: Session, *, limit: int = 50) -> list[ImportJob]:
    return (
        db.query(ImportJob)
        .filter(ImportJob.status == "DRAFT")
        .order_by(ImportJob.id.desc())
        .limit(int(limit))
        .all()
    )


def publish_existing_draft_job(
    db: Session,
    *,
    user: User,
    job: ImportJob,
    category_id: int | None = None,
    confirmation: str,
) -> FinalPublishResult:
    if not bool(getattr(user, "is_superuser", False)):
        raise AutoPublishError(
            "Phase 4.6 R1 FINAL first live product is Super Admin only."
        )
    if str(confirmation or "").strip() != R1_CONFIRMATION:
        raise AutoPublishError(f"Exact confirmation required: {R1_CONFIRMATION}")
    if str(getattr(job, "status", "")).upper() != "DRAFT":
        raise AutoPublishError(f"Expected DRAFT job, got {getattr(job, 'status', None)!r}.")

    try:
        requested = set(json.loads(getattr(job, "requested_targets", "[]") or "[]"))
        authorized = set(json.loads(getattr(job, "authorized_targets", "[]") or "[]"))
    except Exception as exc:
        raise AutoPublishError("ImportJob target metadata is invalid.") from exc
    if "m99eu" not in requested or "m99eu" not in authorized:
        raise AutoPublishError("DRAFT job is not requested and authorized for m99.eu.")

    rows = (
        db.query(ImportJobItem)
        .filter(
            ImportJobItem.import_job_id == int(job.id),
            ImportJobItem.selected.is_(True),
        )
        .order_by(ImportJobItem.id.asc())
        .all()
    )
    if len(rows) != 1:
        raise AutoPublishError(
            "R1 FINAL requires exactly one selected ImportJobItem; "
            f"found {len(rows)}."
        )

    item = rows[0]
    canonical_reference = canonical_reference_from_draft(job=job, item=item)
    supplier_product = supplier_product_from_draft_item(item)
    config = load_config(category_id)
    candidate = candidate_from_supplier_product(
        item,
        supplier_product,
        canonical_reference=canonical_reference,
    )
    try:
        result = _publish_pilot(candidate, config)
    except (AutoPublishError, PublishSafetyError) as exc:
        _audit(
            db,
            user=user,
            job=job,
            action_result="BLOCKED",
            details={
                "canonical_reference": canonical_reference,
                "supplier_reference": candidate.supplier_reference,
                "reason": str(exc),
                "created": False,
                "control_plane": "phase46_post_draft",
            },
        )
        if isinstance(exc, AutoPublishError):
            raise
        raise AutoPublishError(str(exc)) from exc

    _audit(
        db,
        user=user,
        job=job,
        action_result="OK",
        details={
            "canonical_reference": result.reference,
            "supplier_reference": candidate.supplier_reference,
            "channel_product_id": result.product_id,
            "active": result.active,
            "available_for_order": result.available_for_order,
            "visibility": result.visibility,
            "category_id": result.category_id,
            "created": result.created,
            "correlation_id": result.correlation_id,
            "control_plane": "phase46_post_draft",
        },
    )
    return result
