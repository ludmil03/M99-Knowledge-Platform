from pathlib import Path
import sys,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.real_selected_channel_hidden_publish_r7 import *
def good(c="m99.eu",mid="M99 100018",eid="2041"):
 r=LivePublishRequest(c,mid,eid,"",True,True,True,True,True,True,True,True)
 return LivePublishRequest(**{**r.__dict__,"exact_confirmation":confirmation(r)})
def pre(e):return {"external_product_id":e,"m99_id":"M99 100018","active":False,"available_for_order":False}
def upd(p):
 assert p["active"] is False and p["available_for_order"] is False and p["create_allowed"] is False
 return {"ok":True}
def rb(e):return pre(e)
def test_all_channels_supported(): assert set(CHANNELS)=={"mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com","laviro.ro","alviro.ro","toplinka.com"}
def test_exact_confirmation_required():
 r=good();r=LivePublishRequest(**{**r.__dict__,"exact_confirmation":"yes"});assert "EXACT_OPERATOR_CONFIRMATION_REQUIRED" in blockers(r)
def test_all_gates_fail_closed():
 d=good().__dict__
 for k in ("evidence_verified","duplicate_exact_existing","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"):
  r=LivePublishRequest(**{**d,k:False});assert blockers(r)
def test_contract_update_hidden_no_inventory_delete_create():
 p=hidden_contract(good(),{});assert p["operation"]=="UPDATE_ONLY" and p["active"] is False and not p["inventory_write_allowed"] and not p["delete_allowed"] and not p["create_allowed"]
def test_preflight_identity_mismatch_blocks_before_write():
 calls=[0]
 def u(p):calls[0]+=1;return {"ok":True}
 x=execute_live_hidden_update(good(),{},lambda e:{**pre(e),"m99_id":"M99 999999"},u,rb)
 assert x["status"]=="BLOCKED" and calls[0]==0
def test_visible_preflight_blocks_before_write():
 calls=[0]
 def u(p):calls[0]+=1;return {"ok":True}
 x=execute_live_hidden_update(good(),{},lambda e:{**pre(e),"active":True},u,rb)
 assert x["status"]=="BLOCKED" and calls[0]==0
def test_success_is_hidden_and_readback_verified():
 x=execute_live_hidden_update(good(),{"name":"x"},pre,upd,rb);assert x["status"]=="LIVE_HIDDEN_UPDATE_VERIFIED" and x["readback_verified"]
def test_write_failure_not_success():
 assert execute_live_hidden_update(good(),{},pre,lambda p:{"ok":False},rb)["status"]=="WRITE_FAILED"
def test_readback_visible_is_failure():
 def bad(e):return {**pre(e),"active":True}
 assert execute_live_hidden_update(good(),{},pre,upd,bad)["status"]=="READBACK_FAILED"
def test_blocked_never_calls_any_adapter():
 calls=[0]
 def f(*a):calls[0]+=1;return {}
 r=LivePublishRequest("m99.eu","M99 100018","2041","",False,False,False,False,False,False,False,False)
 assert execute_live_hidden_update(r,{},f,f,f)["status"]=="BLOCKED" and calls[0]==0
def test_1000000_maxsim():
 rng=random.Random(707)
 for i in range(1_000_000):
  c=rng.choice(CHANNELS);valid=rng.randrange(6)!=0;r=good(c)
  if not valid:
   d=r.__dict__.copy();d[rng.choice(["evidence_verified","duplicate_exact_existing","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"])]=False;r=LivePublishRequest(**d)
  calls=[0]
  def pp(e):calls[0]+=1;return pre(e)
  def uu(p):calls[0]+=1;return {"ok":True}
  def rr(e):calls[0]+=1;return rb(e)
  x=execute_live_hidden_update(r,{},pp,uu,rr)
  if valid:assert x["status"]=="LIVE_HIDDEN_UPDATE_VERIFIED" and calls[0]==3
  else:assert x["status"]=="BLOCKED" and calls[0]==0
