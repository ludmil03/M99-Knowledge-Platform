from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
import re

from core.product_acquisition import (
    ProductGroup,
    ProductGroupLifecycle,
    ProductVariant,
    LegacyIdentifier,
    SupplierOffer,
    ChannelAssignment,
)
from core.channel_policy_v2 import ChannelPolicy


SCHEMA_VERSION = "0.6.2.1"


class AcquisitionValidationError(ValueError):
    pass


def _require_text(data, key):
    value = str(data.get(key, "")).strip()
    if not value:
        raise AcquisitionValidationError(f"Missing required field: {key}")
    return value


def normalize_m99_id(raw):
    raw = raw.strip()
    m = re.fullmatch(r"M99\s+(\d{6})", raw)
    if not m:
        raise AcquisitionValidationError(
            "M99 ID must use format 'M99 ' + six digits"
        )
    return f"M99 {m.group(1)}"


def normalize_applications(values):
    if not isinstance(values, list) or not values:
        raise AcquisitionValidationError(
            "applications must be a non-empty list"
        )
    return {str(v).strip() for v in values if str(v).strip()}


def normalize_variants(values, parent_m99_id):
    if not isinstance(values, list) or not values:
        raise AcquisitionValidationError("variants must be a non-empty list")

    parent_m99_id = normalize_m99_id(parent_m99_id)
    result, seen = [], set()

    for idx, item in enumerate(values, 1):
        if not isinstance(item, dict):
            raise AcquisitionValidationError(
                f"variant #{idx} must be an object"
            )

        variant_id = normalize_m99_id(
            str(item.get("variant_id", "")).strip()
        )
        if variant_id == parent_m99_id:
            raise AcquisitionValidationError(
                f"variant #{idx} cannot reuse parent M99 ID"
            )
        if variant_id in seen:
            raise AcquisitionValidationError(
                f"duplicate variant_id: {variant_id}"
            )
        seen.add(variant_id)

        supplier_codes = item.get("supplier_codes") or {}
        if not isinstance(supplier_codes, dict):
            raise AcquisitionValidationError(
                f"variant #{idx} supplier_codes must be an object"
            )

        explicit_parent = item.get("parent_m99_id")
        if explicit_parent:
            explicit_parent = normalize_m99_id(str(explicit_parent))
            if explicit_parent != parent_m99_id:
                raise AcquisitionValidationError(
                    f"variant #{idx} parent_m99_id does not match ProductGroup"
                )

        result.append(
            ProductVariant(
                variant_id=variant_id,
                parent_m99_id=parent_m99_id,
                size=(
                    str(item["size"]).strip()
                    if item.get("size") is not None
                    else None
                ),
                color=(
                    str(item["color"]).strip()
                    if item.get("color") is not None
                    else None
                ),
                supplier_codes={
                    str(k): str(v) for k, v in supplier_codes.items()
                },
                ean=(
                    str(item["ean"]).strip()
                    if item.get("ean")
                    else None
                ),
            )
        )

    return result


def build_product_group(source, channel_policy_path):
    parent_m99_id = normalize_m99_id(_require_text(source, "m99_id"))

    p = ProductGroup(
        m99_id=parent_m99_id,
        name=_require_text(source, "name"),
        brand=_require_text(source, "brand"),
        applications=normalize_applications(source.get("applications")),
        lifecycle=ProductGroupLifecycle.DRAFT,
        variants=normalize_variants(
            source.get("variants"),
            parent_m99_id,
        ),
    )

    for x in source.get("legacy_identifiers", []):
        if x.get("system") and x.get("value"):
            p.legacy_identifiers.append(
                LegacyIdentifier(
                    str(x["system"]),
                    str(x["value"]),
                )
            )

    for x in source.get("supplier_offers", []):
        p.supplier_offers.append(
            SupplierOffer(
                supplier=str(x.get("supplier", "")).strip(),
                supplier_product_id=(
                    str(x["supplier_product_id"]).strip()
                    if x.get("supplier_product_id") is not None
                    else None
                ),
                purchase_price_ex_vat=x.get("purchase_price_ex_vat"),
                recommended_price_ex_vat=x.get(
                    "recommended_price_ex_vat"
                ),
                public_price_inc_vat=x.get("public_price_inc_vat"),
                stock_qty=x.get("stock_qty"),
                source=x.get("source"),
            )
        )

    policy = ChannelPolicy(channel_policy_path)
    existing = source.get("existing_channels") or {}

    for channel in policy.eligible_channels(p.applications):
        old = existing.get(channel) or {}
        p.channels.append(
            ChannelAssignment(
                channel=channel,
                enabled=False,
                operator_approved=False,
                existing_product_id=(
                    str(old["existing_product_id"])
                    if old.get("existing_product_id") is not None
                    else None
                ),
                legacy_identifier=(
                    str(old["legacy_identifier"])
                    if old.get("legacy_identifier") is not None
                    else None
                ),
                protected_url=old.get("protected_url"),
                seo_change_allowed=False,
            )
        )

    return p


def build_preview(source, channel_policy_path):
    product = build_product_group(source, channel_policy_path)
    previews = []
    content = source.get("content_by_channel", {}) or {}

    for assignment in product.channels:
        previews.append(
            {
                "channel": assignment.channel,
                "status": "REVIEW",
                "operator_approved": False,
                "publish_allowed": False,
                "existing_product_id": assignment.existing_product_id,
                "legacy_identifier": assignment.legacy_identifier,
                "protected_url": assignment.protected_url,
                "url_action": (
                    "KEEP"
                    if assignment.protected_url
                    else "CREATE_ON_FIRST_PUBLISH"
                ),
                "seo_action": "KEEP_UNTIL_EVIDENCE",
                "content_preview": content.get(
                    assignment.channel, {}
                ),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "PREVIEW_ONLY",
        "writes": {
            "dolibarr": False,
            "channels": False,
            "supplier": False,
        },
        "productgroup": {
            "m99_id": product.m99_id,
            "lifecycle": product.lifecycle.value,
            "name": product.name,
            "brand": product.brand,
            "applications": sorted(product.applications),
            "legacy_identifiers": [
                asdict(x) for x in product.legacy_identifiers
            ],
        },
        "variants": [asdict(x) for x in product.variants],
        "supplier_offers": [
            asdict(x) for x in product.supplier_offers
        ],
        "channel_preview": previews,
        "review": {
            "operator_required": True,
            "decision": None,
            "allowed_actions": ["APPROVE", "REJECT", "EDIT"],
            "product_identity_status": "PENDING_EVIDENCE",
            "manufacturer_content_status": "PENDING_EVIDENCE",
            "supplier_mapping_status": "PENDING",
            "pricing_status": "BLOCKED",
            "availability_status": "BLOCKED",
            "publication_status": "REVIEW",
            "blocking_flags": [],
        },
        "existing_product_discovery": {
            "status": "PENDING",
            "required_before_first_publish": True,
        },
    }


def build_preview_from_file(source_path, channel_policy_path):
    data = json.loads(
        Path(source_path).read_text(encoding="utf-8")
    )
    return build_preview(data, channel_policy_path)
