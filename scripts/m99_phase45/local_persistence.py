from __future__ import annotations
import tempfile
from pathlib import Path
from sqlalchemy import select
from .common import Report

def run(report: Report, repo: Path):
    try:
        import sys
        admin = repo / "admin-platform"
        if str(admin) not in sys.path:
            sys.path.insert(0, str(admin))

        from app.persistence.v073_phase4.database import create_test_schema, make_session_factory
        from app.persistence.v073_phase4.models import IdentityResolution, new_id

        with tempfile.TemporaryDirectory(prefix="m99_phase45_") as td:
            db = Path(td) / "persistence.sqlite3"
            url = f"sqlite:///{db.as_posix()}"
            create_test_schema(url)

            f1 = make_session_factory(url)
            rid = new_id("p45")
            with f1.begin() as s:
                s.add(IdentityResolution(
                    id=rid,
                    source_type="PHASE45_REAL_LOCAL",
                    source_id="phase45",
                    source_record_key="restart-persistence",
                    resolution_state="NEW",
                    confidence=100,
                    match_reasons_json="[]",
                    conflict_reasons_json="[]",
                    requires_human_review=False,
                ))
            del f1

            # Real close/reopen against disk, simulating process restart persistence.
            f2 = make_session_factory(url)
            with f2() as s:
                row = s.scalar(select(IdentityResolution).where(IdentityResolution.id == rid))
                if row is None or row.source_record_key != "restart-persistence":
                    report.add("Admin persistence restart/readback", "FAIL", "Record missing after engine/session recreation")
                    return
            report.add("Admin persistence restart/readback", "PASS", f"disk-backed SQLite record survived reopen: {rid}")
    except Exception as exc:
        report.add("Admin persistence restart/readback", "FAIL", repr(exc))
