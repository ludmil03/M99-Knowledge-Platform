from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import ImportJobItem, Supplier, User
from app.services.import_jobs import authorized_target_codes, create_draft_job
from app.services.v073_phase4.identity_resolver import IncomingIdentity, resolve_identity
from app.services.v073_phase45.unified_add_products import require_source, hydrate_product


ALLOWED_R37_TARGETS = ("m99eu",)


@dataclass(frozen=True)
class OperationalBridge:
    approved_source_uuid: str
    approved_source_name: str
    legacy_supplier_id: int | None
    legacy_supplier_name: str | None
    bridge_ready: bool
    message: str


@dataclass(frozen=True)
class OperationalSupplierProvisioningResult:
    created: bool
    supplier_id: int | None
    supplier_name: str | None
    message: str


def _host(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = "https://" + raw
    host = (urlparse(raw).hostname or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host


def _eligible_operational_suppliers(db: Session) -> list[Supplier]:
    return list(db.scalars(
        select(Supplier).where(
            Supplier.active.is_(True),
            Supplier.browser_enabled.is_(True),
        )
    ))


def _supplier_domain_candidates(supplier: Supplier) -> set[str]:
    values = {
        _host(getattr(supplier, "base_url", None)),
        _host(getattr(supplier, "website", None)),
        _host(getattr(supplier, "domain", None)),
    }
    values.discard("")
    return values


def operational_supplier_bridge(db: Session, source_uuid: str) -> OperationalBridge:
    """
    Bridge an approved governance Source to an already-existing operational
    Supplier. R3.7R4 never creates, activates, edits, or duplicates Supplier rows.

    Matching rule:
    - normalize approved source domain/base_url;
    - match only active + browser-enabled operational Suppliers;
    - READY only when exactly one supplier matches the canonical domain;
    - zero matches => operator-visible blocked state;
    - multiple matches => operator-visible ambiguous blocked state.

    This is deterministic and audit-friendly. It preserves the approved source
    as the governance identity while reusing the pre-existing operational runtime.
    """
    source = require_source(db, source_uuid)
    wanted = {_host(source.domain), _host(source.base_url)}
    wanted.discard("")

    matches = []
    for supplier in _eligible_operational_suppliers(db):
        if wanted.intersection(_supplier_domain_candidates(supplier)):
            matches.append(supplier)

    if len(matches) == 1:
        supplier = matches[0]
        return OperationalBridge(
            approved_source_uuid=source.source_uuid,
            approved_source_name=source.name,
            legacy_supplier_id=int(supplier.id),
            legacy_supplier_name=str(supplier.name),
            bridge_ready=True,
            message=(
                f"READY — approved source is bridged to existing operational "
                f"Supplier #{supplier.id} ({supplier.name})."
            ),
        )

    if len(matches) > 1:
        names = ", ".join(f"#{x.id} {x.name}" for x in matches)
        return OperationalBridge(
            approved_source_uuid=source.source_uuid,
            approved_source_name=source.name,
            legacy_supplier_id=None,
            legacy_supplier_name=None,
            bridge_ready=False,
            message=(
                "AMBIGUOUS operational bridge — multiple active/browser-enabled "
                f"Suppliers match the approved source domain: {names}. "
                "R3.7R4 will not choose silently."
            ),
        )

    return OperationalBridge(
        approved_source_uuid=source.source_uuid,
        approved_source_name=source.name,
        legacy_supplier_id=None,
        legacy_supplier_name=None,
        bridge_ready=False,
        message=(
            "No existing active/browser-enabled operational Supplier matches "
            "the approved source domain. R3.7R4 will not create one silently."
        ),
    )



def _r37_operational_audit_path(db: Session) -> Path:
    bind = db.get_bind()
    db_path = getattr(bind.url, "database", None)
    root = Path(db_path).resolve().parent if db_path else Path("data").resolve()
    path = root / "audit" / "r37_operational_supplier_provisioning.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _append_r37_operational_audit(
    db: Session,
    *,
    user: User,
    action: str,
    source_uuid: str,
    source_name: str,
    source_domain: str,
    supplier_id: int | None,
    supplier_name: str | None,
    outcome: str,
) -> None:
    record = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "outcome": outcome,
        "actor_user_id": int(user.id),
        "actor_email": getattr(user, "email", None),
        "approved_source_uuid": source_uuid,
        "approved_source_name": source_name,
        "approved_source_domain": source_domain,
        "operational_supplier_id": supplier_id,
        "operational_supplier_name": supplier_name,
    }
    with _r37_operational_audit_path(db).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")



def _operational_supplier_code_for_domain(db: Session, domain: str) -> str:
    """
    Build a deterministic, human-readable operational Supplier code from domain.

    Example:
      calenda.bg -> CALENDA-BG

    The code is required by the existing suppliers table. We never overwrite an
    existing code. If the deterministic base is already occupied by another
    Supplier, suffix -2, -3, ... is selected.
    """
    base = re.sub(r"[^A-Z0-9]+", "-", domain.upper()).strip("-")
    if not base:
        raise ValueError("Cannot derive operational Supplier code from source domain.")

    existing = {
        str(code).upper()
        for code in db.scalars(select(Supplier.code))
        if code
    }
    if base not in existing:
        return base

    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"

def provision_operational_supplier_for_approved_source(
    db: Session,
    *,
    user: User,
    source_uuid: str,
) -> OperationalSupplierProvisioningResult:
    if not getattr(user, "is_superuser", False):
        raise PermissionError("Super Admin permission is required.")

    source = require_source(db, source_uuid)
    domain = _host(source.domain or source.base_url)
    if not domain:
        raise ValueError("Approved source has no canonical domain.")

    current = operational_supplier_bridge(db, source_uuid)
    if current.bridge_ready:
        _append_r37_operational_audit(
            db, user=user,
            action="PROVISION_OPERATIONAL_SUPPLIER",
            source_uuid=source.source_uuid,
            source_name=source.name,
            source_domain=domain,
            supplier_id=current.legacy_supplier_id,
            supplier_name=current.legacy_supplier_name,
            outcome="ALREADY_EXISTS",
        )
        return OperationalSupplierProvisioningResult(
            created=False,
            supplier_id=current.legacy_supplier_id,
            supplier_name=current.legacy_supplier_name,
            message="Operational Supplier already exists; no duplicate created.",
        )

    matches = [
        row for row in _eligible_operational_suppliers(db)
        if domain in _supplier_domain_candidates(row)
    ]
    if matches:
        raise ValueError("Operational Supplier match exists but bridge is not uniquely READY.")

    supplier_code = _operational_supplier_code_for_domain(db, domain)

    supplier = Supplier(
        code=supplier_code,
        name=source.name,
        base_url=f"https://{domain}",
        active=True,
        browser_enabled=True,
    )
    db.add(supplier)
    try:
        db.flush()
    except Exception:
        db.rollback()
        raise

    post_matches = [
        row for row in _eligible_operational_suppliers(db)
        if domain in _supplier_domain_candidates(row)
    ]
    if len(post_matches) != 1 or int(post_matches[0].id) != int(supplier.id):
        db.rollback()
        raise ValueError("Provisioning uniqueness check failed; no Supplier was committed.")

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(supplier)

    _append_r37_operational_audit(
        db, user=user,
        action="PROVISION_OPERATIONAL_SUPPLIER",
        source_uuid=source.source_uuid,
        source_name=source.name,
        source_domain=domain,
        supplier_id=int(supplier.id),
        supplier_name=str(supplier.name),
        outcome="CREATED",
    )

    return OperationalSupplierProvisioningResult(
        created=True,
        supplier_id=int(supplier.id),
        supplier_name=str(supplier.name),
        message=f"Created operational Supplier #{supplier.id} ({supplier.name}) for approved source {domain}.",
    )

def authorized_r37_targets(db: Session, user: User) -> tuple[str, ...]:
    allowed = set(str(x) for x in authorized_target_codes(db, user))
    return tuple(x for x in ALLOWED_R37_TARGETS if x in allowed)


def _database_url(db: Session) -> str:
    bind = db.get_bind()
    return bind.url.render_as_string(hide_password=False)



def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "__dict__"):
        return {str(k): _json_safe(v) for k, v in vars(value).items() if not str(k).startswith("_")}
    return str(value)


def _decode_detection(value):
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return dict(parsed) if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def supplier_evidence_snapshot(hydrated) -> dict:
    variants = [_json_safe(dict(v)) for v in (hydrated.variants or ())]
    images = []
    for variant in variants:
        image = str(variant.get("image_url") or "").strip()
        if image and image not in images:
            images.append(image)
    for image in (hydrated.images or ()):
        image = str(image or "").strip()
        if image and image not in images:
            images.append(image)

    size_rows = 0
    available_rows = 0
    unavailable_rows = 0
    for variant in variants:
        for row in (variant.get("sizes") or []):
            size_rows += 1
            observed = (row.get("supplier_availability") or {}).get("total_observed_qty")
            try:
                observed_value = float(observed)
            except (TypeError, ValueError):
                observed_value = None
            if observed_value is not None and observed_value > 0:
                available_rows += 1
            elif observed_value == 0:
                unavailable_rows += 1

    return {
        "schema": "m99.phase46.r2.supplier_evidence.v1",
        "snapshot_source": "DRAFT",
        "url": hydrated.url,
        "title": hydrated.name,
        "name": hydrated.name,
        "supplier_reference": hydrated.supplier_reference or "",
        "source_key": hydrated.source_key or "",
        "calenda_product_id": getattr(hydrated, "calenda_product_id", None),
        "brand": hydrated.brand or "",
        "price_text": hydrated.price_text or "",
        "currency": hydrated.currency or "",
        "availability_text": hydrated.availability_text or "UNKNOWN",
        "description": hydrated.description or "",
        "specifications": _json_safe(list(getattr(hydrated, "specifications", ()) or ())),
        "images": images,
        "variants": variants,
        "warnings": _json_safe(list(hydrated.warnings or ())),
        "evidence_summary": {
            "variant_count": len(variants),
            "color_size_rows": size_rows,
            "available_rows": available_rows,
            "unavailable_rows": unavailable_rows,
            "unique_images": len(images),
            "supplier_availability_not_owned": True,
        },
    }


def _detection_storage_value(model_cls, snapshot: dict):
    column = getattr(getattr(model_cls, "__table__", None), "c", {}).get("detection") if getattr(model_cls, "__table__", None) is not None else None
    if column is not None:
        try:
            if column.type.python_type is str:
                return json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
        except (AttributeError, NotImplementedError):
            pass
    return snapshot


def persist_draft_evidence(db: Session, *, job, identity, hydrated) -> None:
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
        raise ValueError(f"Expected exactly one selected DRAFT item for evidence persistence; found {len(rows)}.")

    row = rows[0]
    current = _decode_detection(getattr(row, "detection", None))
    evidence = supplier_evidence_snapshot(hydrated)
    current.update({
        "identity": _json_safe(identity),
        "supplier_evidence": evidence,
        "commercial": {
            "price_text": evidence["price_text"],
            "currency": evidence["currency"],
            "availability_text": evidence["availability_text"],
        },
    })
    row.detection = _detection_storage_value(ImportJobItem, current)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def product_for_canonical_preview_from_draft(
    db: Session, *, job_id: int, source_uuid: str, product_url: str
) -> dict:
    rows = (
        db.query(ImportJobItem)
        .filter(
            ImportJobItem.import_job_id == int(job_id),
            ImportJobItem.selected.is_(True),
        )
        .order_by(ImportJobItem.id.asc())
        .all()
    )
    if len(rows) == 1:
        detection = _decode_detection(getattr(rows[0], "detection", None))
        evidence = detection.get("supplier_evidence")
        if isinstance(evidence, dict) and evidence.get("schema") == "m99.phase46.r2.supplier_evidence.v1":
            result = dict(evidence)
            result["snapshot_source"] = "DRAFT"
            return result

    # Compatibility fallback for pre-R2 DRAFTs only. New R2 DRAFTs must persist evidence.
    result = product_for_canonical_preview(db, source_uuid=source_uuid, product_url=product_url)
    result["snapshot_source"] = "LIVE_FALLBACK_PRE_R2_DRAFT"
    return result

def prepare_context(db: Session, *, user: User, source_uuid: str, product_url: str):
    source = require_source(db, source_uuid)
    hydrated = hydrate_product(source, product_url)
    if not hydrated.hydration_pass:
        raise ValueError("Hydrated supplier evidence is not sufficient for R3.7.")
    bridge = operational_supplier_bridge(db, source_uuid)
    targets = authorized_r37_targets(db, user)
    return source, hydrated, bridge, targets


def resolve_identity_then_create_draft(
    db: Session,
    *,
    user: User,
    source_uuid: str,
    product_url: str,
    target: str,
    manufacturer_name: str = "",
):
    if target not in ALLOWED_R37_TARGETS:
        raise ValueError("R3.7 target is not allowed.")
    if target not in authorized_r37_targets(db, user):
        raise PermissionError("Operator is not authorized for the requested target.")

    source, hydrated, bridge, _targets = prepare_context(
        db, user=user, source_uuid=source_uuid, product_url=product_url
    )
    if not bridge.bridge_ready or bridge.legacy_supplier_id is None:
        raise ValueError(bridge.message)

    confirmed_manufacturer = (manufacturer_name or hydrated.brand or "").strip()

    identity = resolve_identity(
        _database_url(db),
        IncomingIdentity(
            source_type="SUPPLIER",
            source_id=source.source_uuid,
            source_record_key=str(hydrated.source_key or hydrated.url),
            supplier_reference=hydrated.supplier_reference,
            name=hydrated.name,
            brand_name=confirmed_manufacturer or hydrated.brand,
        ),
    )

    # Governance: AMBIGUOUS/UNRESOLVED cannot proceed to DRAFT.
    if identity["state"] not in {"NEW", "EXISTING"}:
        return {
            "created": False,
            "identity": identity,
            "job": None,
            "source": source,
            "hydrated": hydrated,
            "bridge": bridge,
        }

    item = {
        "url": hydrated.url,
        "title": hydrated.name,
        "supplier_reference": hydrated.supplier_reference or "",
        "manufacturer_name": confirmed_manufacturer,
        "manufacturer_evidence_scope": "OPERATOR_CONFIRMED_SUPPLIER_EVIDENCE",
    }
    job = create_draft_job(
        db,
        user=user,
        supplier_id=bridge.legacy_supplier_id,
        source_type="product",
        source_url=hydrated.url,
        items=[item],
        requested_targets=[target],
    )
    persist_draft_evidence(db, job=job, identity=identity, hydrated=hydrated)
    return {
        "created": True,
        "identity": identity,
        "job": job,
        "source": source,
        "hydrated": hydrated,
        "bridge": bridge,
    }


def product_for_canonical_preview(db: Session, *, source_uuid: str, product_url: str) -> dict:
    source = require_source(db, source_uuid)
    hydrated = hydrate_product(source, product_url)
    if not hydrated.hydration_pass:
        raise ValueError("Supplier hydration failed before Canonical Preview.")

    variant_images = []
    variant_image_evidence = []
    for variant in (hydrated.variants or ()):
        image_url = str(variant.get("image_url") or "").strip()
        if image_url and image_url not in variant_images:
            variant_images.append(image_url)
        if image_url:
            variant_image_evidence.append({
                "code": str(variant.get("code") or ""),
                "value": str(variant.get("value") or variant.get("label") or ""),
                "image_url": image_url,
            })
    all_images = []
    for image_url in list(hydrated.images or ()) + variant_images:
        if image_url and image_url not in all_images:
            all_images.append(image_url)

    return {
        "url": hydrated.url,
        "title": hydrated.name,
        "name": hydrated.name,
        "supplier_reference": hydrated.supplier_reference or "",
        "price_text": hydrated.price_text or "",
        "currency": hydrated.currency or "",
        "availability_text": hydrated.availability_text or "UNKNOWN",
        "images": all_images,
        "variant_images": variant_images,
        "variant_image_evidence": variant_image_evidence,
        "manufacturer_name": hydrated.brand or "",
        "manufacturer_evidence_scope": "SUPPLIER_EVIDENCE_UNTIL_OPERATOR_CONFIRMED",
        "description": hydrated.description or "",
        "specifications": list(getattr(hydrated, "specifications", ()) or ()),
        "variants": [dict(v) for v in (hydrated.variants or ())],
        "brand": hydrated.brand or "",
        "warnings": list(hydrated.warnings or ()),
    }
