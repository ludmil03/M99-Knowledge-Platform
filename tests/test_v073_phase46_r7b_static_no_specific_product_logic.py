from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=(ROOT/"admin-platform/app/services/v073_phase46/calenda_supplier_reconciler.py").read_text(encoding="utf-8").casefold()
def test_no_product_specific_logic():
    for forbidden in ("31940","36127","31869","fruit of the loom","promo stars","river","brook","65-014-0","22160","21185"):
        assert forbidden not in S
