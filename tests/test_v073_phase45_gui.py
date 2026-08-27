from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_real_test_center_files_exist():
    assert (ROOT/"admin-platform/app/routers/real_test_center.py").exists()
    assert (ROOT/"admin-platform/app/services/v073_phase45/real_test_center.py").exists()
    assert (ROOT/"admin-platform/app/templates/real_tests/index.html").exists()

def test_gui_happy_path_keeps_product():
    t=(ROOT/"admin-platform/app/templates/real_tests/index.html").read_text(encoding="utf-8")
    assert "APPROVE — продуктът остава" in t
    assert "Daily Sync" in t
    assert "Няма автоматично DELETE" in t

def test_gui_has_real_test_actions():
    t=(ROOT/"admin-platform/app/templates/real_tests/index.html").read_text(encoding="utf-8")
    for path in (
        "/operator/real-tests/persistence",
        "/operator/real-tests/stenso",
        "/operator/real-tests/m99eu",
        "/operator/real-tests/dolibarr",
        "/operator/real-tests/operator-decision",
    ):
        assert path in t
