from pathlib import Path
DOC=Path(__file__).resolve().parents[1]/"docs/ADR_RELEASE_GIT_CHECKPOINT_002.md"

def test_git_checkpoint_rule_exists():
    s=DOC.read_text(encoding="utf-8")
    assert "Windows/runtime acceptance" in s
    assert "governed-change audit" in s
    assert "git diff --cached --check" in s
    assert "verify HEAD == origin/main" in s
    assert "Do not click" in s
