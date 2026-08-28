from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile

from sqlalchemy import select
from sqlalchemy.orm import Session


def fail(message: str, code: int = 2):
    print(f"[FAIL] {message}")
    raise SystemExit(code)


def main():
    repo = Path.cwd()
    admin_root = repo / "admin-platform"
    if not admin_root.exists():
        fail("Run this acceptance script from the M99 repository root.")

    sys.path.insert(0, str(admin_root))
    from app.services.v073_phase45 import source_registry_persistence as p
    from app.services.v073_phase45 import source_registry_approval_queue as q

    temp_dir = Path(tempfile.mkdtemp(prefix="m99_rev31_phase2_"))
    db_path = temp_dir / "acceptance.sqlite3"
    engine = p.make_engine(f"sqlite+pysqlite:///{db_path.as_posix()}")
    p.bootstrap_schema(engine)

    operator = q.QueueActor("acceptance-operator", "Acceptance Operator", False)
    superadmin = q.QueueActor("acceptance-superadmin", "Acceptance Super Admin", True)

    print("[1/6] Persist operator Supplier proposal...")
    with Session(engine) as s:
        proposal = q.propose_source(
            s,
            actor=operator,
            source_kind="SUPPLIER",
            name="M99 Revision 31 Acceptance Supplier",
            domain="rev31-phase2-acceptance.invalid",
            base_url="https://rev31-phase2-acceptance.invalid/",
        )
        proposal_uuid = proposal.proposal_uuid
    if not db_path.exists() or db_path.stat().st_size == 0:
        fail("SQLite persistence file was not created.")
    print("[PASS] Proposal committed to file database.")

    print("[2/6] Reopen DB and verify Super Admin queue...")
    with Session(engine) as s:
        pending = q.pending_source_proposals(s, actor=superadmin)
        matches = [x for x in pending if x.proposal_uuid == proposal_uuid]
        if len(matches) != 1:
            fail("Persisted proposal not visible in Super Admin pending queue.")
    print("[PASS] Queue sees persisted proposal after session reopen.")

    print("[3/6] Approve proposal as Super Admin...")
    with Session(engine) as s:
        source = q.approve_source(
            s,
            actor=superadmin,
            proposal_uuid=proposal_uuid,
            decision_note="Revision 31 Phase 2 acceptance approval",
        )
        source_uuid = source.source_uuid
    print("[PASS] Approval committed.")

    print("[4/6] Reopen DB and verify ACTIVE approved source...")
    with Session(engine) as s:
        source = s.scalar(
            select(p.ApprovedSourceRecord).where(p.ApprovedSourceRecord.source_uuid == source_uuid)
        )
        if source is None:
            fail("Approved source not found after reopen.")
        if source.activation_status != "ACTIVE":
            fail(f"Expected ACTIVE source, got {source.activation_status}.")
    print("[PASS] Approved source durable and ACTIVE.")

    print("[5/6] Verify approval audit...")
    with Session(engine) as s:
        audits = list(
            s.scalars(
                select(p.SourceAuditRecord).where(
                    p.SourceAuditRecord.entity_uuid == proposal_uuid,
                    p.SourceAuditRecord.action == "SOURCE_APPROVE",
                )
            )
        )
        if len(audits) != 1:
            fail(f"Expected exactly one SOURCE_APPROVE audit, got {len(audits)}.")
        if audits[0].actor_user_id != superadmin.user_id:
            fail("Approval audit actor mismatch.")
    print("[PASS] Approval audit durable.")

    print("[6/6] Verify operator cannot read Super Admin queue...")
    with Session(engine) as s:
        try:
            q.pending_source_proposals(s, actor=operator)
        except q.ApprovalPermissionError:
            pass
        else:
            fail("Operator unexpectedly gained Super Admin queue access.")
    print("[PASS] Queue authorization enforced.")

    try:
        engine.dispose()
    finally:
        try:
            db_path.unlink(missing_ok=True)
            temp_dir.rmdir()
        except OSError:
            pass

    print("")
    print("================================================================")
    print(" REVISION 31 PHASE 2 REAL PERSISTENCE ACCEPTANCE PASSED")
    print("================================================================")
    print("Operator proposal -> durable DB -> Super Admin queue -> approval -> audit: PASS")
    print("No website/product write performed.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
