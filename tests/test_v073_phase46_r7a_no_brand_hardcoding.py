from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=(ROOT/"admin-platform/app/services/v073_phase46/calenda_evidence_governance.py").read_text(encoding="utf-8").casefold()

def test_governance_service_has_no_product_or_manufacturer_specific_fixture():
    for forbidden in ("river","brook","fruit of the loom","promo stars","promostars","93100","93300","31940","65-014-0"):
        assert forbidden not in S
