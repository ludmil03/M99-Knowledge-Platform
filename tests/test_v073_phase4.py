from pathlib import Path
import sys, pytest
from sqlalchemy import select
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path: sys.path.insert(0,str(ADMIN))
from app.persistence.v073_phase2.database import create_temporary_or_explicit_schema as p2schema
from app.persistence.v073_phase4.database import create_test_schema, make_session_factory
from app.persistence.v073_phase4.models import OrganizationDecisionAudit, SupplierSourceConfigurationAudit
from app.services.v073_phase2.organization_registry import propose_organization, seed_reference_stenso
from app.services.v073_phase4.identity_resolver import IncomingIdentity, register_verified_mapping, resolve_identity
from app.services.v073_phase4.identity_review import decide_identity_review, list_identity_review_queue
from app.services.v073_phase4.superadmin_organizations import decide_organization, configure_supplier_source, list_organizations

@pytest.fixture
def db_url(tmp_path):
    u=f"sqlite:///{(tmp_path/'phase4.sqlite3').as_posix()}"; p2schema(u); create_test_schema(u); return u

def test_existing_by_verified_ean(db_url):
    register_verified_mapping(db_url,m99_product_id="M99-100001",mapping_type="EAN_GTIN",external_value="1234567890123")
    r=resolve_identity(db_url,IncomingIdentity("SUPPLIER","src","x",ean_gtin="1234567890123"))
    assert r["state"]=="EXISTING" and r["matched_m99_product_id"]=="M99-100001"

def test_new_stable_unmapped(db_url):
    assert resolve_identity(db_url,IncomingIdentity("SUPPLIER","src","x",manufacturer_reference="ABC-123"))["state"]=="NEW"

def test_unresolved_without_stable_id(db_url):
    r=resolve_identity(db_url,IncomingIdentity("SUPPLIER","src","x",name="Title only"))
    assert r["state"]=="UNRESOLVED" and r["requires_human_review"]

def test_ambiguous_conflicting_verified_ids(db_url):
    register_verified_mapping(db_url,m99_product_id="M99-1",mapping_type="EAN_GTIN",external_value="111")
    register_verified_mapping(db_url,m99_product_id="M99-2",mapping_type="MANUFACTURER_REFERENCE",external_value="MFG-X")
    r=resolve_identity(db_url,IncomingIdentity("SUPPLIER","src","x",ean_gtin="111",manufacturer_reference="MFG-X"))
    assert r["state"]=="AMBIGUOUS" and r["requires_human_review"]

def test_review_link_existing(db_url):
    r=resolve_identity(db_url,IncomingIdentity("LEGACY",None,"legacy/1",name="Unknown"))
    assert list_identity_review_queue(db_url)
    x=decide_identity_review(db_url,resolution_id=r["resolution_id"],reviewer="op",decision="LINK_EXISTING",matched_m99_product_id="M99-77")
    assert x["state"]=="EXISTING"

def test_external_mapping_unique(db_url):
    register_verified_mapping(db_url,m99_product_id="M99-1",mapping_type="SUPPLIER_REFERENCE",external_value="SUP-1")
    with pytest.raises(ValueError):
        register_verified_mapping(db_url,m99_product_id="M99-2",mapping_type="SUPPLIER_REFERENCE",external_value="SUP-1")

def test_superadmin_approval_and_audit(db_url):
    p=propose_organization(db_url,name="NEW SUPPLIER",roles=["SUPPLIER"],created_by="operator")
    decide_organization(db_url,organization_id=p["organization_id"],action="APPROVE",actor="superadmin")
    org=next(x for x in list_organizations(db_url) if x["organization_id"]==p["organization_id"])
    assert org["status"]=="APPROVED" and org["visible_to_operators"]
    f=make_session_factory(db_url)
    with f() as s: assert s.scalar(select(OrganizationDecisionAudit)).action=="APPROVE"

def test_source_remains_read_only(db_url):
    seed_reference_stenso(db_url)
    with pytest.raises(ValueError):
        configure_supplier_source(db_url,organization_id="org-stenso",source_id="src-stenso-public",actor="superadmin",read_only=False)

def test_source_config_audited(db_url):
    seed_reference_stenso(db_url)
    configure_supplier_source(db_url,organization_id="org-stenso",source_id="src-stenso-public",actor="superadmin",status="READY",operator_browsable=True,read_only=True)
    f=make_session_factory(db_url)
    with f() as s: assert s.scalar(select(SupplierSourceConfigurationAudit)).action=="CONFIGURE"

def test_migration_launcher_explicit():
    t=(ROOT/"scripts/m99_phase4/apply_migration.py").read_text(encoding="utf-8-sig")
    assert "M99_ADMIN_DATABASE_URL" in t and "APPLY_V073_PHASE4" in t

def test_architecture_identity_before_content():
    t=(ROOT/"ARCHITECTURE_v0.7.3_PHASE4.md").read_text(encoding="utf-8-sig")
    assert "Identity Before Content" in t and "does not invent identity from title similarity" in t

def test_migration_file_reversible():
    t=(ROOT/"admin-platform/migrations/versions/v073_phase4_identity_and_governance.py").read_text(encoding="utf-8-sig")
    assert 'revision="v073_phase4"' in t and "def upgrade():" in t and "def downgrade():" in t
