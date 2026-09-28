from app.services.unified_publish_service import *
def A(**k):
 d=dict(operator_confirmed=True,displayed_scope_token="s",submitted_scope_token="s",requested_targets=("m99.eu",),qa_ready=True,price_vat_ready=True,languages_ready=True,m99_id=None,identity_state="NEW");d.update(k);return PublishAuthorization(**d)
def test_create_update_separation():
 assert authorize_channel_plans(A())[0].operation==PublishOperation.CREATE
 assert authorize_channel_plans(A(identity_state="EXISTING",m99_id="M99 100019"))[0].operation==PublishOperation.UPDATE
def test_update_never_create_fallback():
 p=authorize_channel_plans(A(identity_state="EXISTING",m99_id="M99 100019"))[0];c=[]
 r=execute_authorized_plan(p,create=lambda p:c.append(1),update=None,readback=lambda p,r:True,audit=lambda *a:None)
 assert r.outcome==WriteOutcome.REJECTED and c==[]
def test_scope_and_gates_fail_closed():
 for k in ({"submitted_scope_token":"x"},{"operator_confirmed":False},{"qa_ready":False},{"price_vat_ready":False},{"languages_ready":False},{"identity_state":"AMBIGUOUS"},{"requested_targets":("alviro.ro",)}):
  assert not authorize_channel_plans(A(**k))[0].authorized
def test_ambiguous_no_retry():
 p=authorize_channel_plans(A())[0];n=[]
 def w(p):n.append(1);raise TimeoutError()
 r=execute_authorized_plan(p,create=w,readback=lambda p,r:True,audit=lambda *a:None)
 assert len(n)==1 and r.outcome==WriteOutcome.AMBIGUOUS and not r.retry_allowed
def test_mandatory_readback():
 p=authorize_channel_plans(A())[0]
 r=execute_authorized_plan(p,create=lambda p:{"confirmed":True,"remote_id":"42"},readback=lambda p,r:False,audit=lambda *a:None)
 assert r.blocker=="MANDATORY_READBACK_FAILED"
