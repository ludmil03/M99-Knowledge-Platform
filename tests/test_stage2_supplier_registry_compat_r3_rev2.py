import pytest
from app.services.supplier_adapter_registry import get_registration,registered_suppliers
from app.services.supplier_evidence_runtime import normalize_supplier_evidence
def test_r2_error_contract_preserved():
    with pytest.raises(ValueError,match=r"UNSUPPORTED_SUPPLIER"):
        normalize_supplier_evidence("FOURTH",object())
def test_future_supplier_is_unregistered_not_permanently_forbidden():
    with pytest.raises(ValueError) as exc:
        get_registration("feya")
    msg=str(exc.value)
    assert "UNSUPPORTED_SUPPLIER" in msg
    assert "SUPPLIER_NOT_REGISTERED:FEYA" in msg
def test_registry_current_proven_three():
    assert registered_suppliers()==("BULTEX99","CALENDA","PALLTEX")
def test_empty_supplier_fails_closed():
    with pytest.raises(ValueError) as exc:
        normalize_supplier_evidence("",object())
    assert "UNSUPPORTED_SUPPLIER" in str(exc.value)
    assert "SUPPLIER_NOT_REGISTERED:EMPTY" in str(exc.value)
