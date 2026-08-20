from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="ascii")


def test_preflight_launcher_uses_python_module_execution():
    text = _read("RUN_M99EU_PRESTASHOP_PREFLIGHT.bat")
    assert "-m scripts.m99eu_prestashop.preflight" in text
    assert '"scripts\\m99eu_prestashop\\preflight.py"' not in text


def test_dry_run_launcher_uses_python_module_execution():
    text = _read("RUN_M99EU_PRESTASHOP_DRY_RUN.bat")
    assert "-m scripts.m99eu_prestashop.dry_run" in text
    assert '"scripts\\m99eu_prestashop\\dry_run.py"' not in text


def test_create_launcher_uses_python_module_execution():
    text = _read("RUN_M99EU_PRESTASHOP_CREATE_DRAFT.bat")
    assert "-m scripts.m99eu_prestashop.create_inactive" in text
    assert '"scripts\\m99eu_prestashop\\create_inactive.py"' not in text


def test_module_imports_resolve_from_repository_root():
    import integrations.m99eu_prestashop
    import scripts.m99eu_prestashop.preflight
    import scripts.m99eu_prestashop.dry_run
    import scripts.m99eu_prestashop.create_inactive

    assert integrations.m99eu_prestashop is not None
