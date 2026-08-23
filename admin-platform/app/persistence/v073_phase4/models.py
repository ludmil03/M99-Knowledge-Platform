from __future__ import annotations
from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Phase4Base(DeclarativeBase):
    pass

def utcnow():
    return datetime.now(timezone.utc)

def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:20]}"

class IdentityResolution(Phase4Base):
    __tablename__ = "m99_v073_identity_resolutions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_record_key: Mapped[str] = mapped_column(String(2000), nullable=False)
    source_snapshot_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supplier_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ean_gtin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    normalized_name: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolution_state: Mapped[str] = mapped_column(String(32), nullable=False)
    matched_m99_product_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    match_reasons_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    conflict_reasons_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    requires_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_decision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class IdentityExternalMapping(Phase4Base):
    __tablename__ = "m99_v073_identity_external_mappings"
    __table_args__ = (UniqueConstraint("mapping_type", "external_value", name="uq_v073_external_identity"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    m99_product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    mapping_type: Mapped[str] = mapped_column(String(64), nullable=False)
    external_value: Mapped[str] = mapped_column(String(2000), nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class OrganizationDecisionAudit(Phase4Base):
    __tablename__ = "m99_v073_organization_decision_audit"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    merge_target_organization_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class SupplierSourceConfigurationAudit(Phase4Base):
    __tablename__ = "m99_v073_supplier_source_config_audit"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    config_summary_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
