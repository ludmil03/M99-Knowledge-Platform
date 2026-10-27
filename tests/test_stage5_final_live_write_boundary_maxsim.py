import pytest
from app.services.stage5_final_live_write_boundary import *
from app.services.stage5_production_authorization import build_authorization
def P(state="NEW"):
 return build_authorization(identity_state=state,reference="M99 100019",target="m99.eu",gross_price="58.13",vat_rate="20",language_map={"en":"7","bg":"4","ru":"9"},content={"en":{"name":"UNO"},"bg":{"name":"УНО"},"ru":{"name":"УНО"}},variants=[{"size":"36"}],payload_xml="<prestashop/>",ready_targets=["m99.eu"])
def run(p,t):
 return execute_authorized_simulation(plan=p,submitted_token=p.scope_token,submitted_operation=p.operation,submitted_reference=p.reference,submitted_target=p.target,transport=t)
def test_real_boundary_hard_locked():
 with pytest.raises(WriteLocked):LockedPS9WriteTransport(unlock=True)
 with pytest.raises(WriteLocked):LockedPS9WriteTransport().execute(WriteRequest("CREATE","/api/products","x","t"))
def test_create_post_update_put_and_readback():
 t=SimulatedOneShotPS9();r=run(P("NEW"),t);assert t.calls[0][0]=="POST" and t.calls[1][0]=="GET" and r.readback_ok and not r.retry_performed
 t=SimulatedOneShotPS9();r=run(P("EXISTING"),t);assert t.calls[0][0]=="PUT" and t.calls[1][0]=="GET"
@pytest.mark.parametrize("o",["timeout","disconnect","ambiguous"])
def test_ambiguous_stops_no_retry(o):
 t=SimulatedOneShotPS9(o)
 with pytest.raises(AmbiguousWrite):run(P(),t)
 assert len(t.calls)==1
def test_readback_failure_is_not_retry():
 t=SimulatedOneShotPS9("success",False);r=run(P(),t);assert not r.readback_ok and not r.retry_performed and len(t.calls)==2
