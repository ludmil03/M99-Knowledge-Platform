"""M99 v0.7.3 Phase 4 identity/governance persistence."""
from alembic import op
import sqlalchemy as sa
revision="v073_phase4"
down_revision="0001_v072_canonical"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("m99_v073_identity_resolutions",
      sa.Column("id",sa.String(64),primary_key=True),sa.Column("source_type",sa.String(64),nullable=False),
      sa.Column("source_id",sa.String(64)),sa.Column("source_record_key",sa.String(2000),nullable=False),
      sa.Column("source_snapshot_id",sa.String(64)),sa.Column("supplier_reference",sa.String(255)),
      sa.Column("manufacturer_reference",sa.String(255)),sa.Column("ean_gtin",sa.String(64)),
      sa.Column("normalized_name",sa.String(1000)),sa.Column("brand_name",sa.String(255)),
      sa.Column("resolution_state",sa.String(32),nullable=False),sa.Column("matched_m99_product_id",sa.String(64)),
      sa.Column("confidence",sa.Integer(),nullable=False,server_default="0"),sa.Column("match_reasons_json",sa.Text(),nullable=False,server_default="[]"),
      sa.Column("conflict_reasons_json",sa.Text(),nullable=False,server_default="[]"),sa.Column("requires_human_review",sa.Boolean(),nullable=False,server_default=sa.false()),
      sa.Column("reviewed_by",sa.String(255)),sa.Column("reviewed_at",sa.DateTime(timezone=True)),sa.Column("review_decision",sa.String(64)),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("m99_v073_identity_external_mappings",
      sa.Column("id",sa.String(64),primary_key=True),sa.Column("m99_product_id",sa.String(64),nullable=False),
      sa.Column("mapping_type",sa.String(64),nullable=False),sa.Column("external_value",sa.String(2000),nullable=False),
      sa.Column("organization_id",sa.String(64)),sa.Column("source_id",sa.String(64)),
      sa.Column("verified",sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column("verified_at",sa.DateTime(timezone=True)),
      sa.UniqueConstraint("mapping_type","external_value",name="uq_v073_external_identity"))
    op.create_table("m99_v073_organization_decision_audit",
      sa.Column("id",sa.String(64),primary_key=True),sa.Column("organization_id",sa.String(64),nullable=False),
      sa.Column("action",sa.String(64),nullable=False),sa.Column("actor",sa.String(255),nullable=False),
      sa.Column("reason",sa.Text()),sa.Column("merge_target_organization_id",sa.String(64)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("m99_v073_supplier_source_config_audit",
      sa.Column("id",sa.String(64),primary_key=True),sa.Column("organization_id",sa.String(64),nullable=False),
      sa.Column("source_id",sa.String(64),nullable=False),sa.Column("actor",sa.String(255),nullable=False),
      sa.Column("action",sa.String(64),nullable=False),sa.Column("config_summary_json",sa.Text(),nullable=False,server_default="{}"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
def downgrade():
    op.drop_table("m99_v073_supplier_source_config_audit")
    op.drop_table("m99_v073_organization_decision_audit")
    op.drop_table("m99_v073_identity_external_mappings")
    op.drop_table("m99_v073_identity_resolutions")
