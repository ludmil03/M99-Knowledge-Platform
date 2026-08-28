from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "admin-platform" / "app" / "services" / "v073_phase45"
ADMIN_ROOT = ROOT / "admin-platform"


def ensure_app_path():
    if str(ADMIN_ROOT) not in sys.path:
        sys.path.insert(0, str(ADMIN_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception:
        sys.modules.pop(spec.name, None)
        raise


def modules():
    ensure_app_path()
    p = load_module(
        "app.services.v073_phase45.source_registry_persistence",
        SERVICE_DIR / "source_registry_persistence.py",
    )
    q = load_module(
        "app.services.v073_phase45.source_registry_approval_queue",
        SERVICE_DIR / "source_registry_approval_queue.py",
    )
    return p, q


def actors(q):
    return (
        q.QueueActor("operator-1", "Operator One", False),
        q.QueueActor("superadmin-1", "Super Admin", True),
    )


def make_db(p):
    engine = p.make_engine("sqlite+pysqlite:///:memory:")
    p.bootstrap_schema(engine)
    return engine


def test_schema_contains_expected_tables():
    p, _ = modules()
    assert set(p.list_tables()) == {
        "m99_rev31_approved_sources",
        "m99_rev31_canonical_categories",
        "m99_rev31_category_proposals",
        "m99_rev31_source_audit",
        "m99_rev31_source_proposals",
    }


def test_operator_proposal_is_persisted_and_not_approved():
    p, q = modules()
    engine = make_db(p)
    op, _ = actors(q)
    with Session(engine) as s:
        proposal = q.propose_source(
            s, actor=op, source_kind="SUPPLIER",
            name="Example Supplier", domain="https://www.example.test/catalog",
            base_url="https://example.test/",
        )
        assert proposal.status == "PROPOSED"
        assert proposal.proposed_domain == "example.test"
        assert s.scalar(select(p.ApprovedSourceRecord)) is None


def test_non_superadmin_cannot_read_approval_queue():
    p, q = modules()
    engine = make_db(p)
    op, _ = actors(q)
    with Session(engine) as s:
        with pytest.raises(q.ApprovalPermissionError):
            q.pending_source_proposals(s, actor=op)


def test_superadmin_queue_approve_and_audit():
    p, q = modules()
    engine = make_db(p)
    op, sa = actors(q)
    with Session(engine) as s:
        proposal = q.propose_source(
            s, actor=op, source_kind="MANUFACTURER",
            name="Example Manufacturer", domain="manufacturer.test",
            base_url="https://manufacturer.test/",
        )
        proposal_uuid = proposal.proposal_uuid

    with Session(engine) as s:
        pending = q.pending_source_proposals(s, actor=sa)
        assert [x.proposal_uuid for x in pending] == [proposal_uuid]
        source = q.approve_source(s, actor=sa, proposal_uuid=proposal_uuid, decision_note="Verified")
        source_uuid = source.source_uuid

    with Session(engine) as s:
        source = s.scalar(select(p.ApprovedSourceRecord).where(p.ApprovedSourceRecord.source_uuid == source_uuid))
        proposal = s.scalar(select(p.SourceProposalRecord).where(p.SourceProposalRecord.proposal_uuid == proposal_uuid))
        audits = list(s.scalars(select(p.SourceAuditRecord).where(p.SourceAuditRecord.entity_uuid == proposal_uuid)))
        assert source is not None
        assert source.activation_status == "ACTIVE"
        assert proposal.status == "APPROVED"
        assert any(a.action == "SOURCE_APPROVE" for a in audits)
        assert q.pending_source_proposals(s, actor=sa) == []


def test_rejected_source_leaves_history_and_can_be_reproposed():
    p, q = modules()
    engine = make_db(p)
    op, sa = actors(q)
    with Session(engine) as s:
        first = q.propose_source(
            s, actor=op, source_kind="SUPPLIER",
            name="Rejected Supplier", domain="rejected.test",
            base_url="https://rejected.test/",
        )
        first_uuid = first.proposal_uuid
        q.reject_source(s, actor=sa, proposal_uuid=first_uuid, decision_note="Need verification")
        second = q.propose_source(
            s, actor=op, source_kind="SUPPLIER",
            name="Rejected Supplier", domain="rejected.test",
            base_url="https://rejected.test/",
            prior_rejected_proposal_uuid=first_uuid,
        )
        assert second.proposal_uuid != first_uuid
        assert second.prior_rejected_proposal_uuid == first_uuid
        assert second.status == "PROPOSED"


def test_approved_duplicate_kind_domain_is_blocked():
    p, q = modules()
    engine = make_db(p)
    op, sa = actors(q)
    with Session(engine) as s:
        first = q.propose_source(
            s, actor=op, source_kind="SUPPLIER",
            name="Supplier A", domain="dup.test", base_url="https://dup.test/"
        )
        q.approve_source(s, actor=sa, proposal_uuid=first.proposal_uuid)
        with pytest.raises(q.ApprovalStateError):
            q.propose_source(
                s, actor=op, source_kind="SUPPLIER",
                name="Supplier B", domain="https://www.dup.test/path", base_url="https://dup.test/"
            )


def test_category_queue_requires_superadmin_and_approval_persists():
    p, q = modules()
    engine = make_db(p)
    op, sa = actors(q)
    with Session(engine) as s:
        proposal = q.propose_category(s, actor=op, name="Safety Footwear")
        proposal_uuid = proposal.proposal_uuid
        with pytest.raises(q.ApprovalPermissionError):
            q.pending_category_proposals(s, actor=op)

    with Session(engine) as s:
        pending = q.pending_category_proposals(s, actor=sa)
        assert [x.proposal_uuid for x in pending] == [proposal_uuid]
        cat = q.approve_category(s, actor=sa, proposal_uuid=proposal_uuid)
        cat_uuid = cat.category_uuid

    with Session(engine) as s:
        cat = s.scalar(select(p.CanonicalCategoryRecord).where(p.CanonicalCategoryRecord.category_uuid == cat_uuid))
        assert cat is not None
        assert cat.active is True
        assert q.pending_category_proposals(s, actor=sa) == []
