import pytest
from app.services.supplier_adapter_registry import get_registration
from app.services.supplier_evidence_runtime import normalize_supplier_evidence
def test_exact_historical_r2_regex_still_matches():
    with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
        normalize_supplier_evidence("FOURTH",object())
def test_exact_historical_r3_regex_still_matches():
    with pytest.raises(ValueError,match="SUPPLIER_NOT_REGISTERED:FEYA"):
        get_registration("feya")
@pytest.mark.parametrize("name",["BULT","EUROMASTER","VIKING","NEW_SUPPLIER"])
def test_future_supplier_dual_semantics(name):
    with pytest.raises(ValueError) as exc:
        get_registration(name)
    msg=str(exc.value)
    assert "UNSUPPORTED_SUPPLIER" in msg
    assert f"SUPPLIER_NOT_REGISTERED:{name}" in msg
