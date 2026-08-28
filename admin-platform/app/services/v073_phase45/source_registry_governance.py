from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable
from urllib.parse import urlparse
import uuid


class SourceKind(str, Enum):
    SUPPLIER = "SUPPLIER"
    MANUFACTURER = "MANUFACTURER"


class ProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ActivationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"


class CategoryProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:20]}"


def normalize_domain(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    host = (urlparse(value).hostname or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host


@dataclass(frozen=True)
class Actor:
    user_id: str
    display_name: str
    is_superadmin: bool = False


@dataclass
class SourceProposal:
    id: str
    kind: SourceKind
    organization_name: str
    domain: str
    status: ProposalStatus
    proposed_by_user_id: str
    proposed_at: datetime
    reviewed_by_user_id: str | None = None
    reviewed_at: datetime | None = None
    review_reason: str | None = None
    prior_rejected_proposal_id: str | None = None

    @property
    def operational(self) -> bool:
        return self.status == ProposalStatus.APPROVED

    @property
    def visible_in_operator_registry(self) -> bool:
        return self.status == ProposalStatus.APPROVED


@dataclass
class ApprovedSource:
    id: str
    kind: SourceKind
    organization_name: str
    domain: str
    activation: ActivationStatus = ActivationStatus.ACTIVE
    approved_from_proposal_id: str | None = None
    previous_domains: list[str] = field(default_factory=list)

    @property
    def operational(self) -> bool:
        return self.activation == ActivationStatus.ACTIVE


@dataclass
class CanonicalCategory:
    id: str
    name: str
    approved: bool = True


@dataclass
class CanonicalCategoryProposal:
    id: str
    name: str
    status: CategoryProposalStatus
    proposed_by_user_id: str
    proposed_at: datetime
    reviewed_by_user_id: str | None = None
    reviewed_at: datetime | None = None
    review_reason: str | None = None
    prior_rejected_proposal_id: str | None = None


@dataclass(frozen=True)
class AuditRecord:
    id: str
    timestamp: datetime
    actor_user_id: str
    actor_name: str
    action: str
    entity_type: str
    entity_id: str
    previous_value: str | None
    new_value: str | None
    result: str
    correlation_id: str


class GovernanceViolation(ValueError):
    pass


def propose_source(
    *,
    actor: Actor,
    kind: SourceKind,
    organization_name: str,
    domain: str,
    approved_sources: Iterable[ApprovedSource] = (),
    rejected_history: Iterable[SourceProposal] = (),
) -> SourceProposal:
    normalized = normalize_domain(domain)
    if not organization_name.strip():
        raise GovernanceViolation("ORGANIZATION_NAME_REQUIRED")
    if not normalized:
        raise GovernanceViolation("SOURCE_DOMAIN_REQUIRED")

    for source in approved_sources:
        if source.kind == kind and normalize_domain(source.domain) == normalized:
            raise GovernanceViolation("SOURCE_ALREADY_APPROVED")

    prior = None
    for proposal in reversed(list(rejected_history)):
        if (
            proposal.kind == kind
            and proposal.status == ProposalStatus.REJECTED
            and normalize_domain(proposal.domain) == normalized
        ):
            prior = proposal.id
            break

    return SourceProposal(
        id=new_id("src-proposal"),
        kind=kind,
        organization_name=organization_name.strip(),
        domain=normalized,
        status=ProposalStatus.PROPOSED,
        proposed_by_user_id=actor.user_id,
        proposed_at=utcnow(),
        prior_rejected_proposal_id=prior,
    )


def review_source_proposal(
    *,
    actor: Actor,
    proposal: SourceProposal,
    approve: bool,
    reason: str = "",
) -> SourceProposal:
    if not actor.is_superadmin:
        raise GovernanceViolation("SUPERADMIN_REQUIRED")
    if proposal.status != ProposalStatus.PROPOSED:
        raise GovernanceViolation("PROPOSAL_ALREADY_REVIEWED")

    proposal.status = ProposalStatus.APPROVED if approve else ProposalStatus.REJECTED
    proposal.reviewed_by_user_id = actor.user_id
    proposal.reviewed_at = utcnow()
    proposal.review_reason = reason.strip() or None
    return proposal


def approved_source_from_proposal(proposal: SourceProposal) -> ApprovedSource:
    if proposal.status != ProposalStatus.APPROVED:
        raise GovernanceViolation("APPROVED_PROPOSAL_REQUIRED")
    return ApprovedSource(
        id=new_id("source"),
        kind=proposal.kind,
        organization_name=proposal.organization_name,
        domain=proposal.domain,
        activation=ActivationStatus.ACTIVE,
        approved_from_proposal_id=proposal.id,
    )


def edit_approved_source_domain(*, actor: Actor, source: ApprovedSource, new_domain: str) -> ApprovedSource:
    if not actor.is_superadmin:
        raise GovernanceViolation("SUPERADMIN_REQUIRED")
    normalized = normalize_domain(new_domain)
    if not normalized:
        raise GovernanceViolation("SOURCE_DOMAIN_REQUIRED")
    if normalized == normalize_domain(source.domain):
        return source
    if source.domain and source.domain not in source.previous_domains:
        source.previous_domains.append(source.domain)
    source.domain = normalized
    return source


def set_source_activation(*, actor: Actor, source: ApprovedSource, active: bool) -> ApprovedSource:
    if not actor.is_superadmin:
        raise GovernanceViolation("SUPERADMIN_REQUIRED")
    source.activation = ActivationStatus.ACTIVE if active else ActivationStatus.DEACTIVATED
    return source


def can_operator_use_source(source: ApprovedSource) -> bool:
    return source.operational


def build_mapping_audit(
    *,
    actor: Actor,
    action: str,
    supplier_product_id: str,
    manufacturer_product_id: str | None,
    previous_value: str | None,
    correlation_id: str | None = None,
) -> AuditRecord:
    if action not in {"CREATE", "CORRECT", "REMOVE"}:
        raise GovernanceViolation("INVALID_MAPPING_AUDIT_ACTION")
    return AuditRecord(
        id=new_id("audit"),
        timestamp=utcnow(),
        actor_user_id=actor.user_id,
        actor_name=actor.display_name,
        action=action,
        entity_type="MANUFACTURER_SUPPLIER_PRODUCT_MAPPING",
        entity_id=supplier_product_id,
        previous_value=previous_value,
        new_value=manufacturer_product_id,
        result="RECORDED",
        correlation_id=correlation_id or new_id("corr"),
    )


def propose_canonical_category(
    *,
    actor: Actor,
    name: str,
    approved_categories: Iterable[CanonicalCategory] = (),
    rejected_history: Iterable[CanonicalCategoryProposal] = (),
) -> CanonicalCategoryProposal:
    clean = " ".join((name or "").split())
    if not clean:
        raise GovernanceViolation("CATEGORY_NAME_REQUIRED")
    norm = clean.casefold()
    if any(c.approved and c.name.casefold() == norm for c in approved_categories):
        raise GovernanceViolation("CANONICAL_CATEGORY_ALREADY_APPROVED")
    prior = None
    for p in reversed(list(rejected_history)):
        if p.status == CategoryProposalStatus.REJECTED and p.name.casefold() == norm:
            prior = p.id
            break
    return CanonicalCategoryProposal(
        id=new_id("cat-proposal"),
        name=clean,
        status=CategoryProposalStatus.PROPOSED,
        proposed_by_user_id=actor.user_id,
        proposed_at=utcnow(),
        prior_rejected_proposal_id=prior,
    )


def review_category_proposal(
    *,
    actor: Actor,
    proposal: CanonicalCategoryProposal,
    approve: bool,
    reason: str = "",
) -> CanonicalCategoryProposal:
    if not actor.is_superadmin:
        raise GovernanceViolation("SUPERADMIN_REQUIRED")
    if proposal.status != CategoryProposalStatus.PROPOSED:
        raise GovernanceViolation("PROPOSAL_ALREADY_REVIEWED")
    proposal.status = CategoryProposalStatus.APPROVED if approve else CategoryProposalStatus.REJECTED
    proposal.reviewed_by_user_id = actor.user_id
    proposal.reviewed_at = utcnow()
    proposal.review_reason = reason.strip() or None
    return proposal


def can_map_supplier_category(target: CanonicalCategory) -> bool:
    return bool(target.approved)


def bulk_selection_defaults(product_ids: Iterable[str]) -> dict:
    ids = list(product_ids)
    return {
        "discovered_count": len(ids),
        "selected_ids": [],
        "selected_count": 0,
        "select_all_requires_explicit_operator_action": True,
        "direct_publish_allowed": False,
    }
