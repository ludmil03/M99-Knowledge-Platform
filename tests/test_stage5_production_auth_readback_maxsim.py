import pytest
from app.services.stage5_production_authorization import *
def K():
 return dict(reference="M99 100019",target="m99.eu",gross_price="58.13",vat_rate="20",language_map={"en":"7","bg":"4","ru":"9"},content={"en":{"name":"UNO"},"bg":{"name":"УНО"},"ru":{"name":"УНО"}},variants=[{"size":"36"},{"size":"48"}],payload_xml="<prestashop/>",ready_targets=["m99.eu"])
def test_new_create_existing_update():
 assert build_authorization(identity_state="NEW",**K()).operation=="CREATE"
 assert build_authorization(identity_state="EXISTING",**K()).operation=="UPDATE"
def test_failclosed():
 for state in ("AMBIGUOUS","UNRESOLVED"):
  with pytest.raises(ValueError):build_authorization(identity_state=state,**K())
 k=K();k["ready_targets"]=[]
 with pytest.raises(ValueError):build_authorization(identity_state="NEW",**k)
def test_tamper_and_audit():
 p=build_authorization(identity_state="EXISTING",**K())
 assert validate_submission(p,submitted_token=p.scope_token,submitted_operation="UPDATE",submitted_reference=p.reference,submitted_target=p.target)
 for field,val in (("submitted_token","x"),("submitted_operation","CREATE"),("submitted_reference","M99 100020"),("submitted_target","mela99.com")):
  kw=dict(submitted_token=p.scope_token,submitted_operation=p.operation,submitted_reference=p.reference,submitted_target=p.target);kw[field]=val
  with pytest.raises(ValueError):validate_submission(p,**kw)
 a=audit_simulation(p,False);assert not a["write_performed"] and not a["retry_performed"] and not a["readback_ok"]
def test_scope_changes():
 a=build_authorization(identity_state="NEW",**K());k=K();k["gross_price"]="58.14";b=build_authorization(identity_state="NEW",**k);assert a.scope_token!=b.scope_token
