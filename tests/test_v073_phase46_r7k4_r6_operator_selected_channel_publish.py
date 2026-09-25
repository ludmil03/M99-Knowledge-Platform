from pathlib import Path
import sys,random
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.operator_selected_channel_publish_r6 import *

def good(channel="m99.eu",mid="M99 100018",eid="2041"):
    return PublishRequest(mid,channel,eid,"UPDATE_ONLY",f"PUBLISH {mid} TO {channel}",
      True,True,True,True,True,True,True)

def upd(p): 
    assert p["operation"]=="UPDATE_ONLY" and p["active"] is False and p["available_for_order"] is False
    assert p["inventory_write_allowed"] is False and p["delete_allowed"] is False
    return {"ok":True}
def rb(eid): return {"external_product_id":eid,"m99_id":"M99 100018","active":False,"available_for_order":False}

def test_all_configured_channels_selectable():
    assert select_channels(ALLOWED_CHANNELS)==ALLOWED_CHANNELS
def test_no_implicit_all_and_unknown_blocked():
    try: select_channels([])
    except ValueError as e: assert "AT_LEAST_ONE" in str(e)
    else: assert False
    try: select_channels(["evil.example"])
    except ValueError as e: assert "CHANNEL_NOT_ALLOWED" in str(e)
    else: assert False
def test_exact_confirmation():
    r=good(); r=PublishRequest(**{**r.__dict__,"operator_confirmation":"yes"})
    assert "EXACT_OPERATOR_CONFIRMATION_REQUIRED" in validate_request(r)
def test_create_is_blocked():
    r=good(); r=PublishRequest(**{**r.__dict__,"operation":"CREATE"})
    assert "CREATE_BLOCKED_R6" in validate_request(r)
def test_every_gate_fail_closed():
    base=good().__dict__
    for k in ("evidence_verified","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"):
        r=PublishRequest(**{**base,k:False})
        assert validate_request(r)
def test_hidden_update_payload_never_inventory_or_delete():
    p=build_hidden_update_payload(good(),{"name":"Daytona"})
    assert p["active"] is False and p["available_for_order"] is False
    assert p["inventory_write_allowed"] is False and p["delete_allowed"] is False
def test_success_requires_readback():
    x=controlled_publish(good(),{"name":"Daytona"},upd,rb)
    assert x["status"]=="PUBLISHED_HIDDEN_VERIFIED" and x["readback_verified"]
def test_readback_identity_mismatch_fails():
    def bad(eid): return {"external_product_id":eid,"m99_id":"M99 999999","active":False,"available_for_order":False}
    x=controlled_publish(good(),{},upd,bad)
    assert x["status"]=="READBACK_FAILED"
def test_readback_active_fails():
    def bad(eid): return {"external_product_id":eid,"m99_id":"M99 100018","active":True,"available_for_order":False}
    assert controlled_publish(good(),{},upd,bad)["status"]=="READBACK_FAILED"
def test_adapter_write_rejection_fails():
    assert controlled_publish(good(),{},lambda p:{"ok":False},rb)["status"]=="WRITE_FAILED"
def test_blocked_request_never_calls_adapter():
    calls=[0]
    def u(p): calls[0]+=1; return {"ok":True}
    r=PublishRequest("M99 100018","m99.eu","2041")
    assert controlled_publish(r,{},u,rb)["status"]=="BLOCKED" and calls[0]==0
def test_1000000_mass_simulations():
    rng=random.Random(606)
    for i in range(1_000_000):
        c=rng.choice(ALLOWED_CHANNELS); valid=rng.randrange(5)!=0
        r=good(c, "M99 100018", str(1000+(i%9000)))
        if not valid:
            field=rng.choice(["evidence_verified","canonical_ready","pricing_ready","vat_ready","content_ready","images_ready","variants_ready"])
            r=PublishRequest(**{**r.__dict__,field:False})
        calls=[0]
        def u(p): calls[0]+=1; return {"ok":True}
        def rr(eid): return {"external_product_id":eid,"m99_id":"M99 100018","active":False,"available_for_order":False}
        x=controlled_publish(r,{"n":"x"},u,rr)
        if valid:
            assert x["status"]=="PUBLISHED_HIDDEN_VERIFIED" and calls[0]==1
        else:
            assert x["status"]=="BLOCKED" and calls[0]==0
