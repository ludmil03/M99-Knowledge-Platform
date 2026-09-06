from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path: sys.path.insert(0,str(ADMIN))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.services.v073_phase45.source_registry_persistence import bootstrap_schema, ApprovedSourceRecord, CanonicalCategoryRecord
from app.services.v073_phase45.approved_source_category_bridge import approved_operational_sources, approved_canonical_categories, find_approved_source_by_domain, require_approved_supplier

def test_bridge_filters_active(tmp_path):
    engine=create_engine(f"sqlite:///{tmp_path/'x.sqlite'}")
    bootstrap_schema(engine)
    with Session(engine) as db:
        db.add_all([
            ApprovedSourceRecord(
                source_uuid="s1",
                source_kind="SUPPLIER",
                name="Good",
                domain="good.example",
                base_url="https://good.example/",
                activation_status="ACTIVE",
                originating_proposal_uuid="p1",
                approved_by_user_id="admin-1",
                approved_by_display="Phase4 Test Admin",
            ),
            ApprovedSourceRecord(
                source_uuid="s2",
                source_kind="SUPPLIER",
                name="Off",
                domain="off.example",
                base_url="https://off.example/",
                activation_status="DEACTIVATED",
                originating_proposal_uuid="p2",
                approved_by_user_id="admin-1",
                approved_by_display="Phase4 Test Admin",
            ),
            CanonicalCategoryRecord(
                category_uuid="c1",
                name="Shoes",
                parent_uuid=None,
                active=True,
                originating_proposal_uuid="cp1",
                approved_by_user_id="admin-1",
                approved_by_display="Phase4 Test Admin",
            ),
            CanonicalCategoryRecord(
                category_uuid="c2",
                name="Hidden",
                parent_uuid=None,
                active=False,
                originating_proposal_uuid="cp2",
                approved_by_user_id="admin-1",
                approved_by_display="Phase4 Test Admin",
            ),
        ])
        db.commit()
        assert [x.name for x in approved_operational_sources(db,source_kind="SUPPLIER")]==["Good"]
        assert [x.name for x in approved_canonical_categories(db)]==["Shoes"]
        assert find_approved_source_by_domain(db,"https://www.good.example/path").name=="Good"
        assert require_approved_supplier(db,"good.example").source_uuid=="s1"

def test_unapproved_rejected(tmp_path):
    engine=create_engine(f"sqlite:///{tmp_path/'y.sqlite'}")
    bootstrap_schema(engine)
    with Session(engine) as db:
        try: require_approved_supplier(db,"unknown.example")
        except ValueError: pass
        else: raise AssertionError("unapproved supplier must be rejected")
