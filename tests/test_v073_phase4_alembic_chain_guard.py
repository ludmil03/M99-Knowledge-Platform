from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "admin-platform" / "migrations" / "versions" / "0001_v072_canonical_foundation.py"
PHASE4 = ROOT / "admin-platform" / "migrations" / "versions" / "v073_phase4_identity_and_governance.py"

def _assignment(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {path}")

def test_phase4_down_revision_matches_actual_baseline_revision_id():
    assert BASE.exists()
    assert PHASE4.exists()
    baseline_revision = _assignment(BASE, "revision")
    phase4_down_revision = _assignment(PHASE4, "down_revision")
    assert baseline_revision == "0001_v072_canonical"
    assert phase4_down_revision == baseline_revision
    assert phase4_down_revision != BASE.stem
