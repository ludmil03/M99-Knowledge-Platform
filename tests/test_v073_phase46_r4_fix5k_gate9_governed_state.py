from pathlib import Path
import re

RUNTIME_RE = re.compile(r"var/phase46_draft_enrichment/job-\d+\.json")
MIGRATED_FIX5B = "tests/test_v073_phase46_r4_fix5b_runtime_draft_artifact_allowlist.py"

def is_runtime(path: str) -> bool:
    return bool(RUNTIME_RE.fullmatch(path.replace("\\", "/")))

def test_runtime_sidecar_is_separate_from_governed_source_set():
    observed = {
        MIGRATED_FIX5B,
        "tests/test_v073_phase46_r4_fix5k_gate9_governed_state.py",
        "var/phase46_draft_enrichment/job-17.json",
    }
    governed = {p for p in observed if not is_runtime(p)}
    runtime = {p for p in observed if is_runtime(p)}
    assert MIGRATED_FIX5B in governed
    assert "var/phase46_draft_enrichment/job-17.json" in runtime
    assert "var/phase46_draft_enrichment/job-17.json" not in governed

def test_runtime_filter_is_exact_not_broad_var_ignore():
    assert is_runtime("var/phase46_draft_enrichment/job-17.json")
    assert is_runtime(r"var\phase46_draft_enrichment\job-42.json")
    assert not is_runtime("var/random.json")
    assert not is_runtime("var/phase46_draft_enrichment/job-17.json.bak")
    assert not is_runtime("var/phase46_draft_enrichment/sub/job-17.json")
