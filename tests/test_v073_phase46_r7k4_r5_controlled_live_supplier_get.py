from pathlib import Path
import sys, random
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.controlled_live_supplier_get_r5 import *
from app.services.v073_phase46.real_supplier_evidence_bridge_r4 import from_public_page_observation,evidence_gate

class Resp:
    def __init__(self,status=200,url="https://palltex.bg/bg/p/daytona/17374",ctype="text/html",text="OK",headers=None):
        self.status_code=status; self.url=url; self.text=text; self.content=text.encode()
        self.headers=headers if headers is not None else {"content-type":ctype}

def req(**kw):
    d=dict(supplier="Palltex",exact_product_url="https://palltex.bg/bg/p/daytona/17374",
           expected_host="palltex.bg",supplier_reference="042502",operator_approved=True)
    d.update(kw); return LiveFetchRequest(**d)

def transport(method,url,**kwargs):
    assert method=="GET"; assert kwargs["allow_redirects"] is False
    return Resp(url=url)

def parser(body,r):
    return {"supplier_reference":"042502","product_name":"Daytona","observed_at":"2026-09-17T20:00:00+03:00",
            "price_gross":"30.70","currency":"BGN",
            "variants":[{"supplier_variant_code":"042502.S","size":"S","availability":"наличен","currency":"BGN","price_gross":"30.70"}],
            "image_urls":["https://palltex.bg/media/daytona.jpg"]}

def test_happy_path_get_to_r4():
    x=acquire_to_r4(req(),transport,parser,from_public_page_observation,evidence_gate)
    assert x["status"]=="VERIFIED" and x["ready_for_r3"]
    assert x["method"]=="GET" and not x["writes_performed"]

def test_operator_approval_required_before_transport():
    called=[0]
    def t(*a,**k): called[0]+=1; return Resp()
    x=controlled_get(req(operator_approved=False),t)
    assert x.status=="BLOCKED" and called[0]==0

def test_host_https_and_exact_url_fail_closed():
    bad=("http://palltex.bg/bg/p/daytona/17374","https://evil.bg/bg/p/daytona/17374",
         "https://palltex.bg/category/17374","https://palltex.bg/")
    for u in bad:
        assert controlled_get(req(exact_product_url=u),transport).status=="BLOCKED"

def test_redirect_is_blocked_not_followed():
    def t(*a,**k): return Resp(302,headers={"location":"https://palltex.bg/other","content-type":"text/html"})
    x=controlled_get(req(),t); assert x.status=="VERIFICATION_FAILED" and x.failure_reason=="REDIRECT_BLOCKED"

def test_non_200_fail_closed():
    for s in (401,403,404,429,500,503):
        def t(*a,_s=s,**k): return Resp(_s)
        x=controlled_get(req(),t)
        assert x.status=="VERIFICATION_FAILED" and x.failure_reason=="HTTP_STATUS_NOT_200"

def test_content_type_gate():
    def t(*a,**k): return Resp(200,ctype="application/octet-stream")
    assert controlled_get(req(),t).failure_reason=="CONTENT_TYPE_BLOCKED"

def test_network_error_never_becomes_zero_stock():
    def t(*a,**k): raise TimeoutError("x")
    x=acquire_to_r4(req(),t,parser,from_public_page_observation,evidence_gate)
    assert x["status"]=="VERIFICATION_FAILED" and not x["source_failure_means_zero_stock"]

def test_parser_error_fail_closed():
    def p(*a): raise ValueError("bad html")
    x=acquire_to_r4(req(),transport,p,from_public_page_observation,evidence_gate)
    assert x["status"]=="VERIFICATION_FAILED" and x["blockers"][0].startswith("PARSER_ERROR")

def test_reference_mismatch_blocks_before_r4():
    def p(body,r):
        x=parser(body,r); x["supplier_reference"]="WRONG"; return x
    x=acquire_to_r4(req(),transport,p,from_public_page_observation,evidence_gate)
    assert x["blockers"]==["SUPPLIER_REFERENCE_MISMATCH"]

def test_incomplete_evidence_stays_verification_failed():
    def p(body,r):
        return {"supplier_reference":"042502","product_name":"Daytona","observed_at":"2026-09-17T20:00:00+03:00",
                "price_gross":None,"currency":None,"variants":[],"image_urls":[]}
    x=acquire_to_r4(req(),transport,p,from_public_page_observation,evidence_gate)
    assert x["status"]=="VERIFICATION_FAILED"
    assert "SUPPLIER_PRICE_NOT_VERIFIED" in x["blockers"]

def test_static_contract_rejects_write_verbs():
    assert static_transport_contract("requests.post(url)") != []
    assert static_transport_contract("requests.get(url)") == []

def test_1500000_mass_simulations():
    rng=random.Random(99405)
    statuses=[200,200,200,401,403,404,429,500,503]
    for i in range(1_500_000):
        s=rng.choice(statuses)
        approved=rng.choice([True,True,True,False])
        def t(method,url,_s=s,**kwargs):
            assert method=="GET"
            return Resp(_s,url=url)
        x=controlled_get(req(operator_approved=approved),t)
        assert x.method=="GET" and not x.writes_performed
        if not approved: assert x.status=="BLOCKED"
        elif s==200: assert x.status=="FETCHED"
        else: assert x.status=="VERIFICATION_FAILED"
        if i%15000==0:
            y=acquire_to_r4(req(),transport,parser,from_public_page_observation,evidence_gate)
            assert y["status"]=="VERIFIED" and not y["supplier_stock_is_m99_physical_stock"]
