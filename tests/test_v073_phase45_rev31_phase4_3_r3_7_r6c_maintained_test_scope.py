from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "r37r6_maintained_test_scope.contract"

def test_maintained_scope_contract_exists():
    assert CONTRACT.exists()

def test_full_regression_scope_is_tests_only():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "FULL_REGRESSION_COMMAND=pytest -q tests" in text
    assert "EXCLUDE_OUTPUT_BACKUPS=true" in text
    assert "EXCLUDE_LIVE_SCRIPTS=true" in text
