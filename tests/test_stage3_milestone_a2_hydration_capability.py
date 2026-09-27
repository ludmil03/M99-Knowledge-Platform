import pytest
from app.services.wizard_hydration_capability import *
def test_bultex_transitioned_to_ready_only_after_a3_acceptance():
    c=hydration_capability("org-bultex")
    assert c.supplier_key=="BULTEX99" and c.state==HydrationState.READY
    assert c.network_read_required is True and c.write_performed is False
def test_palltex_remains_blocked_and_does_not_call_runtime():
    called=[]
    with pytest.raises(ValueError,match="HYDRATION_NOT_READY"):
        hydrate_for_wizard("org-palltex",["X"],runtime_call=lambda x:called.append(x))
    assert called==[]
def test_calenda_remains_blocked():
    with pytest.raises(ValueError,match="HYDRATION_NOT_READY"): require_proven_hydration("org-calenda")
def test_unknown_org_remains_blocked():
    c=hydration_capability("org-feya")
    assert c.state==HydrationState.BLOCKED and c.reason=="SUPPLIER_HYDRATION_NOT_REGISTERED"
