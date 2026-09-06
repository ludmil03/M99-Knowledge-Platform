from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T=ROOT/"admin-platform/app/services/v073_phase45/r37_identity_persistence_reconcile.py"
def test_no_common_base_assumption():
    x=T.read_text(encoding="utf-8"); assert "Base.metadata" not in x; assert "app.core.db import Base" not in x
def test_private_metadata_discovery():
    x=T.read_text(encoding="utf-8"); assert "_discover_identity_tables" in x; assert 'getattr(obj, "__table__", None)' in x; assert "pkgutil.walk_packages" in x
def test_fail_closed():
    assert "No Identity persistence Table objects discovered" in T.read_text(encoding="utf-8")
def test_backup_before_create():
    x=T.read_text(encoding="utf-8"); assert "backup = _backup(db)" in x; assert "table.create(" in x; assert "shutil.copy2(backup" in x
