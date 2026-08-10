from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum


class PublishMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    WRITE_DRAFT = "WRITE_DRAFT"
    PUBLISH_LIVE = "PUBLISH_LIVE"


class PublishAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    BLOCK = "BLOCK"


@dataclass
class ExistingChannelIdentity:
    product_id: str | None
    product_name: str | None
    slug: str | None
    url: str | None
    legacy_identifiers: list[str]


@dataclass
class NameChangeProposal:
    current_name: str | None
    proposed_name: str | None
    evidence_status: str
    operator_approved: bool = False


def decide_name_action(
    existing: ExistingChannelIdentity | None,
    proposal: NameChangeProposal | None,
) -> dict:
    if existing is None:
        return {
            "action": "GENERATE_FOR_NEW_PRODUCT",
            "name_to_write": proposal.proposed_name if proposal else None,
            "operator_approval_required": False,
        }

    if not proposal or not proposal.proposed_name:
        return {
            "action": "KEEP",
            "name_to_write": existing.product_name,
            "operator_approval_required": False,
        }

    changed = (
        (existing.product_name or "").strip()
        != (proposal.proposed_name or "").strip()
    )
    if not changed:
        return {
            "action": "KEEP",
            "name_to_write": existing.product_name,
            "operator_approval_required": False,
        }

    # Name changes on existing products require BOTH evidence and operator approval.
    if (
        proposal.evidence_status == "PROVEN_BETTER"
        and proposal.operator_approved
    ):
        return {
            "action": "CHANGE_APPROVED",
            "name_to_write": proposal.proposed_name,
            "operator_approval_required": True,
        }

    return {
        "action": "KEEP",
        "name_to_write": existing.product_name,
        "suggested_name": proposal.proposed_name,
        "suggestion_status": "INFORMATION_ONLY",
        "operator_approval_required": True,
    }


def build_identity_lock(
    existing: ExistingChannelIdentity | None,
    name_decision: dict,
) -> dict:
    if existing is None:
        return {
            "existing_product": False,
            "product_id": None,
            "product_name": name_decision.get("name_to_write"),
            "slug": None,
            "url": None,
            "legacy_identifiers": [],
            "url_locked": False,
            "slug_locked": False,
            "name_locked": False,
        }

    return {
        "existing_product": True,
        "product_id": existing.product_id,
        "product_name": name_decision.get(
            "name_to_write", existing.product_name
        ),
        "original_product_name": existing.product_name,
        "slug": existing.slug,
        "url": existing.url,
        "legacy_identifiers": list(existing.legacy_identifiers),
        "url_locked": True,
        "slug_locked": True,
        "name_locked": name_decision.get("action") != "CHANGE_APPROVED",
        "name_change_action": name_decision.get("action"),
    }


def required_confirmation(mode: PublishMode, action: PublishAction) -> str:
    return f"{mode.value} {action.value} M99 100002 MELA99"


def validate_publish_gates(gates: dict) -> list[str]:
    failures = []
    required_true = (
        "single_product_scope",
        "target_channel_is_mela99",
        "content_ready",
        "internal_discovery_complete",
        "audit_enabled",
        "rollback_enabled",
    )
    for key in required_true:
        if not gates.get(key):
            failures.append(f"GATE_FAILED:{key}")

    mode = gates.get("publish_mode")
    # No operator approval for a strictly no-write DRY_RUN.
    if mode in (PublishMode.WRITE_DRAFT.value, PublishMode.PUBLISH_LIVE.value):
        if not gates.get("operator_approved"):
            failures.append("GATE_FAILED:operator_approved")

    # Pricing is deliberately a separate gate. LIVE requires approved
    # pricing and availability.
    if mode == PublishMode.PUBLISH_LIVE.value:
        if not gates.get("pricing_approved"):
            failures.append("GATE_FAILED:pricing_approved")
        if not gates.get("availability_approved"):
            failures.append("GATE_FAILED:availability_approved")

    return failures
