from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
LEGACY = HERE / "test_v073_phase46_r4_fix5b_runtime_draft_artifact_allowlist.py"

def _load():
    spec=importlib.util.spec_from_file_location("fix5b_contract", LEGACY)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_fix5b_contract_is_repo_self_contained():
    s=LEGACY.read_text(encoding="utf-8")
    assert 'INSTALL_M99_V073_PHASE46_R4.py' not in s
    assert "fullmatch" in s

def test_fix5b_contract_matches_expected_behavior():
    m=_load()
    assert m._is_allowed_runtime_artifact("var/phase46_draft_enrichment/job-17.json")
    assert m._is_allowed_runtime_artifact(r"var\phase46_draft_enrichment\job-42.json")
    assert not m._is_allowed_runtime_artifact("var/phase46_draft_enrichment/job-17.json.bak")
    assert not m._is_allowed_runtime_artifact("var/anything.json")
