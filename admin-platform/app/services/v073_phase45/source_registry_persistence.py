from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


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


class Rev31SourceRegistryBase(DeclarativeBase):
    pass


class SourceProposalRecord(Rev31SourceRegistryBase):
    __tablename__ = "m99_rev31_source_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    proposed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_base_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    proposed_by_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    proposed_by_display: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=ProposalStatus.PROPOSED.value)
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reviewed_by_display: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prior_rejected_proposal_uuid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("proposal_uuid", name="uq_rev31_source_proposal_uuid"),
    )


class ApprovedSourceRecord(Rev31SourceRegistryBase):
    __tablename__ = "m99_rev31_approved_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    activation_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ActivationStatus.ACTIVE.value
    )
    originating_proposal_uuid: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_by_display: Mapped[str] = mapped_column(String(255), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("source_kind", "domain", name="uq_rev31_source_kind_domain"),
    )


class CategoryProposalRecord(Rev31SourceRegistryBase):
    __tablename__ = "m99_rev31_category_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    proposed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_parent_uuid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    proposed_by_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    proposed_by_display: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CategoryProposalStatus.PROPOSED.value
    )
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reviewed_by_display: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prior_rejected_proposal_uuid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class CanonicalCategoryRecord(Rev31SourceRegistryBase):
    __tablename__ = "m99_rev31_canonical_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_uuid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    originating_proposal_uuid: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_by_display: Mapped[str] = mapped_column(String(255), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class SourceAuditRecord(Rev31SourceRegistryBase):
    __tablename__ = "m99_rev31_source_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_display: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_uuid: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


def make_engine(url: str, *, echo: bool = False) -> Engine:
    return create_engine(url, echo=echo, future=True)


def bootstrap_schema(engine: Engine) -> None:
    """Explicit schema bootstrap. Never called automatically on module import."""
    Rev31SourceRegistryBase.metadata.create_all(engine)


def list_tables() -> tuple[str, ...]:
    return tuple(sorted(Rev31SourceRegistryBase.metadata.tables.keys()))
