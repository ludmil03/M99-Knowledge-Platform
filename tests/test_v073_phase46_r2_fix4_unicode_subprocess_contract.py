from pathlib import Path

def test_fix4_contract_documented_in_architecture():
    root = Path(__file__).resolve().parents[1]
    arch = (root / "ARCHITECTURE_v0.7.3_PHASE46_R2_EVIDENCE_CHAIN_REPAIR.md").read_text(encoding="utf-8")
    assert "Unicode-safe subprocess capture" in arch
    assert "text=False" in arch
