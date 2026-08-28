from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.v073_phase45.source_registry_persistence import (
    ActivationStatus,
    ApprovedSourceRecord,
    CategoryProposalRecord,
    CategoryProposalStatus,
    CanonicalCategoryRecord,
    ProposalStatus,
    SourceAuditRecord,
    SourceKind,
    SourceProposalRecord,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class QueueActor:
    user_id: str
    display_name: str
    is_superadmin: bool = False


class ApprovalPermissionError(PermissionError):
    pass


class ApprovalStateError(RuntimeError):
    pass


def _require_superadmin(actor: QueueActor) -> None:
    if not actor.is_superadmin:
        raise ApprovalPermissionError("Super Admin approval permission required.")


def _audit(
    session: Session,
    *,
    actor: QueueActor,
    correlation_id: str,
    action: str,
    entity_type: str,
    entity_uuid: str,
    previous_value: Optional[dict],
    new_value: Optional[dict],
    result: str = "SUCCESS",
) -> SourceAuditRecord:
    row = SourceAuditRecord(
        audit_uuid=str(uuid.uuid4()),
        correlation_id=correlation_id,
        actor_user_id=actor.user_id,
        actor_display=actor.display_name,
        action=action,
        entity_type=entity_type,
        entity_uuid=entity_uuid,
        previous_value=json.dumps(previous_value, sort_keys=True) if previous_value is not None else None,
        new_value=json.dumps(new_value, sort_keys=True) if new_value is not None else None,
        result=result,
        created_at=utcnow(),
    )
    session.add(row)
    return row


def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    for prefix in ("https://", "http://"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    value = value.split("/", 1)[0]
    if value.startswith("www."):
        value = value[4:]
    return value.rstrip(".")


def propose_source(
    session: Session,
    *,
    actor: QueueActor,
    source_kind: SourceKind | str,
    name: str,
    domain: str,
    base_url: str,
    prior_rejected_proposal_uuid: Optional[str] = None,
) -> SourceProposalRecord:
    kind = SourceKind(source_kind).value
    normalized_domain = normalize_domain(domain or base_url)
    if not normalized_domain:
        raise ValueError("Source domain is required.")

    approved = session.scalar(
        select(ApprovedSourceRecord).where(
            ApprovedSourceRecord.source_kind == kind,
            ApprovedSourceRecord.domain == normalized_domain,
        )
    )
    if approved is not None:
        raise ApprovalStateError("An approved source already exists for this kind/domain.")

    row = SourceProposalRecord(
        proposal_uuid=str(uuid.uuid4()),
        source_kind=kind,
        proposed_name=name.strip(),
        proposed_domain=normalized_domain,
        proposed_base_url=base_url.strip(),
        proposed_by_user_id=actor.user_id,
        proposed_by_display=actor.display_name,
        proposed_at=utcnow(),
        status=ProposalStatus.PROPOSED.value,
        prior_rejected_proposal_uuid=prior_rejected_proposal_uuid,
    )
    session.add(row)
    session.flush()
    _audit(
        session,
        actor=actor,
        correlation_id=str(uuid.uuid4()),
        action="SOURCE_PROPOSE",
        entity_type="SOURCE_PROPOSAL",
        entity_uuid=row.proposal_uuid,
        previous_value=None,
        new_value={"kind": kind, "domain": normalized_domain, "name": row.proposed_name},
    )
    session.commit()
    session.refresh(row)
    return row


def pending_source_proposals(session: Session, *, actor: QueueActor) -> list[SourceProposalRecord]:
    _require_superadmin(actor)
    return list(
        session.scalars(
            select(SourceProposalRecord)
            .where(SourceProposalRecord.status == ProposalStatus.PROPOSED.value)
            .order_by(SourceProposalRecord.proposed_at.asc(), SourceProposalRecord.id.asc())
        )
    )


def approve_source(
    session: Session,
    *,
    actor: QueueActor,
    proposal_uuid: str,
    decision_note: Optional[str] = None,
) -> ApprovedSourceRecord:
    _require_superadmin(actor)
    proposal = session.scalar(
        select(SourceProposalRecord).where(SourceProposalRecord.proposal_uuid == proposal_uuid)
    )
    if proposal is None:
        raise LookupError("Source proposal not found.")
    if proposal.status != ProposalStatus.PROPOSED.value:
        raise ApprovalStateError("Only PROPOSED source proposals can be approved.")

    duplicate = session.scalar(
        select(ApprovedSourceRecord).where(
            ApprovedSourceRecord.source_kind == proposal.source_kind,
            ApprovedSourceRecord.domain == proposal.proposed_domain,
        )
    )
    if duplicate is not None:
        raise ApprovalStateError("Approved source already exists for this kind/domain.")

    now = utcnow()
    source = ApprovedSourceRecord(
        source_uuid=str(uuid.uuid4()),
        source_kind=proposal.source_kind,
        name=proposal.proposed_name,
        domain=proposal.proposed_domain,
        base_url=proposal.proposed_base_url,
        activation_status=ActivationStatus.ACTIVE.value,
        originating_proposal_uuid=proposal.proposal_uuid,
        approved_by_user_id=actor.user_id,
        approved_by_display=actor.display_name,
        approved_at=now,
        updated_at=now,
    )
    session.add(source)

    proposal.status = ProposalStatus.APPROVED.value
    proposal.reviewed_by_user_id = actor.user_id
    proposal.reviewed_by_display = actor.display_name
    proposal.reviewed_at = now
    proposal.decision_note = decision_note

    correlation_id = str(uuid.uuid4())
    _audit(
        session,
        actor=actor,
        correlation_id=correlation_id,
        action="SOURCE_APPROVE",
        entity_type="SOURCE_PROPOSAL",
        entity_uuid=proposal.proposal_uuid,
        previous_value={"status": ProposalStatus.PROPOSED.value},
        new_value={"status": ProposalStatus.APPROVED.value, "source_uuid": source.source_uuid},
    )
    session.commit()
    session.refresh(source)
    return source


def reject_source(
    session: Session,
    *,
    actor: QueueActor,
    proposal_uuid: str,
    decision_note: Optional[str] = None,
) -> SourceProposalRecord:
    _require_superadmin(actor)
    proposal = session.scalar(
        select(SourceProposalRecord).where(SourceProposalRecord.proposal_uuid == proposal_uuid)
    )
    if proposal is None:
        raise LookupError("Source proposal not found.")
    if proposal.status != ProposalStatus.PROPOSED.value:
        raise ApprovalStateError("Only PROPOSED source proposals can be rejected.")

    proposal.status = ProposalStatus.REJECTED.value
    proposal.reviewed_by_user_id = actor.user_id
    proposal.reviewed_by_display = actor.display_name
    proposal.reviewed_at = utcnow()
    proposal.decision_note = decision_note
    _audit(
        session,
        actor=actor,
        correlation_id=str(uuid.uuid4()),
        action="SOURCE_REJECT",
        entity_type="SOURCE_PROPOSAL",
        entity_uuid=proposal.proposal_uuid,
        previous_value={"status": ProposalStatus.PROPOSED.value},
        new_value={"status": ProposalStatus.REJECTED.value},
    )
    session.commit()
    session.refresh(proposal)
    return proposal


def propose_category(
    session: Session,
    *,
    actor: QueueActor,
    name: str,
    parent_uuid: Optional[str] = None,
    prior_rejected_proposal_uuid: Optional[str] = None,
) -> CategoryProposalRecord:
    row = CategoryProposalRecord(
        proposal_uuid=str(uuid.uuid4()),
        proposed_name=name.strip(),
        proposed_parent_uuid=parent_uuid,
        proposed_by_user_id=actor.user_id,
        proposed_by_display=actor.display_name,
        proposed_at=utcnow(),
        status=CategoryProposalStatus.PROPOSED.value,
        prior_rejected_proposal_uuid=prior_rejected_proposal_uuid,
    )
    session.add(row)
    session.flush()
    _audit(
        session,
        actor=actor,
        correlation_id=str(uuid.uuid4()),
        action="CATEGORY_PROPOSE",
        entity_type="CATEGORY_PROPOSAL",
        entity_uuid=row.proposal_uuid,
        previous_value=None,
        new_value={"name": row.proposed_name, "parent_uuid": parent_uuid},
    )
    session.commit()
    session.refresh(row)
    return row


def pending_category_proposals(session: Session, *, actor: QueueActor) -> list[CategoryProposalRecord]:
    _require_superadmin(actor)
    return list(
        session.scalars(
            select(CategoryProposalRecord)
            .where(CategoryProposalRecord.status == CategoryProposalStatus.PROPOSED.value)
            .order_by(CategoryProposalRecord.proposed_at.asc(), CategoryProposalRecord.id.asc())
        )
    )


def approve_category(
    session: Session,
    *,
    actor: QueueActor,
    proposal_uuid: str,
    decision_note: Optional[str] = None,
) -> CanonicalCategoryRecord:
    _require_superadmin(actor)
    proposal = session.scalar(
        select(CategoryProposalRecord).where(CategoryProposalRecord.proposal_uuid == proposal_uuid)
    )
    if proposal is None:
        raise LookupError("Category proposal not found.")
    if proposal.status != CategoryProposalStatus.PROPOSED.value:
        raise ApprovalStateError("Only PROPOSED category proposals can be approved.")

    now = utcnow()
    category = CanonicalCategoryRecord(
        category_uuid=str(uuid.uuid4()),
        name=proposal.proposed_name,
        parent_uuid=proposal.proposed_parent_uuid,
        active=True,
        originating_proposal_uuid=proposal.proposal_uuid,
        approved_by_user_id=actor.user_id,
        approved_by_display=actor.display_name,
        approved_at=now,
    )
    session.add(category)
    proposal.status = CategoryProposalStatus.APPROVED.value
    proposal.reviewed_by_user_id = actor.user_id
    proposal.reviewed_by_display = actor.display_name
    proposal.reviewed_at = now
    proposal.decision_note = decision_note
    _audit(
        session,
        actor=actor,
        correlation_id=str(uuid.uuid4()),
        action="CATEGORY_APPROVE",
        entity_type="CATEGORY_PROPOSAL",
        entity_uuid=proposal.proposal_uuid,
        previous_value={"status": CategoryProposalStatus.PROPOSED.value},
        new_value={"status": CategoryProposalStatus.APPROVED.value, "category_uuid": category.category_uuid},
    )
    session.commit()
    session.refresh(category)
    return category
