import re

RUNTIME_DRAFT_RE = re.compile(r"var/phase46_draft_enrichment/job-\d+\.json")

def _is_allowed_runtime_artifact(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return bool(RUNTIME_DRAFT_RE.fullmatch(normalized))

def test_runtime_sidecar_allowlist_is_exact_and_narrow():
    accepted = [
        "var/phase46_draft_enrichment/job-17.json",
        r"var\phase46_draft_enrichment\job-999.json",
    ]
    rejected = [
        "var/phase46_draft_enrichment/job-x.json",
        "var/phase46_draft_enrichment/job-17.json.bak",
        "var/phase46_draft_enrichment/sub/job-17.json",
        "var/other/job-17.json",
        "var/phase46_draft_enrichment/",
        "var/phase46_draft_enrichment/job-17.JSON",
    ]
    assert all(_is_allowed_runtime_artifact(p) for p in accepted)
    assert not any(_is_allowed_runtime_artifact(p) for p in rejected)

def test_unexpected_nonruntime_paths_are_not_allowlisted():
    assert not _is_allowed_runtime_artifact("admin-platform/app/main.py")
    assert not _is_allowed_runtime_artifact("README.md")
    assert not _is_allowed_runtime_artifact("var/random.txt")

def test_contract_regex_is_fullmatch_not_prefix_match():
    assert _is_allowed_runtime_artifact("var/phase46_draft_enrichment/job-1.json")
    assert not _is_allowed_runtime_artifact("var/phase46_draft_enrichment/job-1.json/extra")
