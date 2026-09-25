from decimal import Decimal
import pytest
from app.services.v073_phase46.product_2041_controlled_update import *
S={"id":"2041","reference":"M99 100018","active":"0","available_for_order":"0","visibility":"none"}
def P():return preflight(S,True,"palltex","r1","30.20",".20",5,2,1)
def test_id():assert P()["operation"]=="UPDATE" and P()["id"]=="2041"
def test_price():assert Decimal(".0100")<=P()["discount"]<=Decimal(".0170") and P()["gross"]<Decimal("30.20")
def test_vat():assert P()["tax"]=="5"
def test_source():assert not preflight(S,False,"p","r","30.20",".20",5,2,1)["ready"]
def test_confirm():
 with pytest.raises(ValueError):authorize(P(),"YES")
def test_hidden():assert not preflight({**S,"active":"1"},True,"p","r","30.20",".20",5,2,1)["ready"]
def test_identity():assert not preflight({**S,"id":"2042"},True,"p","r","30.20",".20",5,2,1)["ready"]
def test_readback():
 p=P();assert readback(p,{"id":"2041","reference":"M99 100018","active":"0","available_for_order":"0","visibility":"none","tax":"5","gross":p["gross"],"default_count":1,"variant_count":2,"image_count":1})[0]
def test_zero():
 p=P();assert not readback(p,{"id":"2041","reference":"M99 100018","active":"0","available_for_order":"0","visibility":"none","tax":"5","gross":"0","default_count":1,"variant_count":2,"image_count":1})[0]
