from pathlib import Path

def test_stale_r6b_filename_is_not_a_current_test_module():
    here = Path(__file__).resolve().parent
    assert not (here / "test_v073_phase45_rev31_phase4_3_r3_7_r6b_maintained_test_scope.py").exists()

def test_r6c_replacement_contract_is_present():
    here = Path(__file__).resolve().parent
    assert (here / "test_v073_phase45_rev31_phase4_3_r3_7_r6c_maintained_test_scope.py").exists()
    assert (here / "r37r6_maintained_test_scope.contract").exists()
