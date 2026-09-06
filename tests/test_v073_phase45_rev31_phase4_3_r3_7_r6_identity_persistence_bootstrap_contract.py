from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOT = ROOT / "admin-platform/app/services/v073_phase45/r37_identity_persistence_bootstrap.py"

def test_identity_table_contract_named_exactly():
    text = BOOT.read_text(encoding="utf-8")
    assert '"m99_v073_identity_external_mappings"' in text

def test_backup_before_bootstrap_contract():
    text = BOOT.read_text(encoding="utf-8")
    assert "backup = backup_admin_db(db)" in text
    assert "CREATE TABLE IF NOT EXISTS m99_v073_identity_external_mappings" in text

def test_bootstrap_is_narrow_and_idempotent():
    text = BOOT.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS" in text
    assert "CREATE INDEX IF NOT EXISTS" in text

    # Scope the safety check to executable write statements, not explanatory
    # docstrings/comments. R3.7R6 intentionally documents that it does NOT
    # create DRAFT/channel/stock writes.
    executable_markers = (
        "INSERT INTO ",
        "UPDATE ",
        "DELETE FROM ",
    )
    upper = text.upper()
    assert not any(marker in upper for marker in executable_markers)
    assert "prestashop" not in upper
    assert "dolibarr" not in upper

def test_failed_bootstrap_restores_backup():
    text = BOOT.read_text(encoding="utf-8")
    assert "shutil.copy2(backup, Path(plan.database_path))" in text

def test_verified_query_index_supported():
    text = BOOT.read_text(encoding="utf-8")
    assert "(mapping_type, external_value, verified)" in text
