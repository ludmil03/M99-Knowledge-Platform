from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Phase2Base(DeclarativeBase):
    """Isolated v0.7.3 Phase 2 metadata.

    Production migration is intentionally deferred to a separately approved
    Alembic milestone. Tests create these tables only in temporary SQLite DBs.
    """


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:20]}"


class Organization(Phase2Base):
    __tablename__ = "m99_v073_organizations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="PENDING_SUPER_ADMIN_APPROVAL"
    )
    visible_to_operators: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list["OrganizationRole"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan", lazy="selectin"
    )
    sources: Mapped[list["SupplierSource"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan", lazy="selectin"
    )


class OrganizationRole(Phase2Base):
    __tablename__ = "m99_v073_organization_roles"
    __table_args__ = (
        UniqueConstraint("organization_id", "role", name="uq_v073_org_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_organizations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    organization: Mapped[Organization] = relationship(back_populates="roles")


class SupplierSource(Phase2Base):
    __tablename__ = "m99_v073_supplier_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_organizations.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_key: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="NOT_CONFIGURED")
    capabilities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    catalog_roots_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    operator_browsable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    organization: Mapped[Organization] = relationship(back_populates="sources")


class SupplierObservation(Phase2Base):
    __tablename__ = "m99_v073_supplier_observations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_supplier_sources.id"), nullable=False
    )
    source_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    conflict_state: Mapped[str] = mapped_column(String(64), nullable=False, default="NONE")


class ImportJob(Phase2Base):
    __tablename__ = "m99_v073_import_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    operator_role: Mapped[str] = mapped_column(String(64), nullable=False, default="OPERATOR")
    source_organization_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_organizations.id"), nullable=False
    )
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_supplier_sources.id"), nullable=False
    )
    selection_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    selected_products_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    selected_categories_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    observation_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    product_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    identity_status: Mapped[str] = mapped_column(String(64), nullable=False, default="PENDING")
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="DRAFT")
    audit_log_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    targets: Mapped[list["ImportJobTarget"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )


class ImportJobTarget(Phase2Base):
    __tablename__ = "m99_v073_import_job_targets"
    __table_args__ = (
        UniqueConstraint("import_job_id", "target_key", name="uq_v073_import_job_target"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_job_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("m99_v073_import_jobs.id", ondelete="CASCADE"), nullable=False
    )
    target_key: Mapped[str] = mapped_column(String(255), nullable=False)
    requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    authorized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    result_status: Mapped[str] = mapped_column(String(64), nullable=False, default="PENDING")

    job: Mapped["ImportJob"] = relationship(back_populates="targets")
