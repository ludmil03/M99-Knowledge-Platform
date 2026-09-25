from pathlib import Path
import sys,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.m99_knowledge_operator_live_publish_r71 import *
def good():
 return OperatorPublishCommand("m99.eu","M99 100018","2041",True,True,True,True,True,True,True,True,True)
def pre(e):return {"external_product_id":e,"m99_id":"M99 100018","active":False,"available_for_order":False}
def upd(p):
 assert p["operation"]=="UPDATE_ONLY" and p["active"] is False and not p["create_allowed"] and not p["delete_allowed"] and not p["inventory_write_allowed"]
 return {"ok":True}
def rb(e):return pre(e)
def test_operator_required():
 d=good().__dict__.copy();d["operator_approved"]=False;assert "OPERATOR_APPROVAL_REQUIRED" in gate(OperatorPublishCommand(**d))
def test_unbound_channel_blocked():
 d=good().__dict__.copy();d["channel"]="mela99.com";assert "LIVE_ADAPTER_NOT_BOUND_FOR_CHANNEL" in gate(OperatorPublishCommand(**d))
def test_all_business_gates_required():
 d=good().__dict__
 for k in ("evidence_verified","duplicate_exact_existing","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"):
  x=d.copy();x[k]=False;assert gate(OperatorPublishCommand(**x))
def test_identity_preflight_before_write():
 calls=[0]
 def u(p):calls[0]+=1;return {"ok":True}
 x=operator_publish(good(),{},lambda e:{**pre(e),"m99_id":"M99 999999"},u,rb)
 assert x["status"]=="BLOCKED" and calls[0]==0
def test_real_contract_hidden_update_readback():
 x=operator_publish(good(),{"name":"Daytona"},pre,upd,rb);assert x["status"]=="LIVE_HIDDEN_UPDATE_VERIFIED" and x["readback_verified"]
def test_write_reject_fails():
 assert operator_publish(good(),{},pre,lambda p:{"ok":False},rb)["status"]=="WRITE_FAILED"
def test_readback_mismatch_fails():
 assert operator_publish(good(),{},pre,upd,lambda e:{**rb(e),"active":True})["status"]=="READBACK_FAILED"
def test_1000000_operator_maxsim():
 rng=random.Random(711)
 for i in range(1_000_000):
  c=good();valid=rng.randrange(7)!=0
  if not valid:
   d=c.__dict__.copy();d[rng.choice(["operator_approved","evidence_verified","duplicate_exact_existing","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"])]=False;c=OperatorPublishCommand(**d)
  calls=[0]
  def p(e):calls[0]+=1;return pre(e)
  def u(x):calls[0]+=1;return {"ok":True}
  def r(e):calls[0]+=1;return rb(e)
  x=operator_publish(c,{},p,u,r)
  if valid:assert x["status"]=="LIVE_HIDDEN_UPDATE_VERIFIED" and calls[0]==3
  else:assert x["status"]=="BLOCKED" and calls[0]==0
