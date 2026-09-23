from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable, Mapping
from urllib.parse import urlparse
import json

SCHEMA="R7K.4-R5-CONTROLLED-LIVE-SUPPLIER-GET"
MODE="OPERATOR_GET_ONLY"
ALLOWED_METHOD="GET"
MAX_BYTES=4_000_000

@dataclass(frozen=True)
class LiveFetchRequest:
    supplier: str
    exact_product_url: str
    expected_host: str
    supplier_reference: str
    operator_approved: bool=False

@dataclass(frozen=True)
class LiveFetchResult:
    status: str
    http_status: int|None
    final_url: str|None
    content_type: str|None
    body: str|None
    failure_reason: str|None
    method: str="GET"
    writes_performed: bool=False

def _host(url:str)->str:
    try: return (urlparse(url).hostname or "").lower().removeprefix("www.")
    except Exception: return ""

def validate_request(r:LiveFetchRequest)->list[str]:
    b=[]
    if not r.operator_approved: b.append("OPERATOR_APPROVAL_REQUIRED")
    if not r.supplier.strip(): b.append("SUPPLIER_MISSING")
    if not r.supplier_reference.strip(): b.append("SUPPLIER_REFERENCE_MISSING")
    p=urlparse(r.exact_product_url)
    if p.scheme!="https": b.append("HTTPS_REQUIRED")
    if not p.hostname or _host(r.exact_product_url)!=r.expected_host.lower().removeprefix("www."):
        b.append("HOST_MISMATCH")
    if not p.path or p.path=="/" or any(x in p.path.lower() for x in ("/category","/search","/cart","/login")):
        b.append("EXACT_PRODUCT_URL_REQUIRED")
    return sorted(set(b))

def controlled_get(r:LiveFetchRequest, transport:Callable[...,Any])->LiveFetchResult:
    blockers=validate_request(r)
    if blockers:
        return LiveFetchResult("BLOCKED",None,None,None,None,",".join(blockers))
    try:
        resp=transport("GET",r.exact_product_url,allow_redirects=False,timeout=20)
    except Exception as e:
        return LiveFetchResult("VERIFICATION_FAILED",None,None,None,None,"NETWORK_ERROR:"+type(e).__name__)
    status=int(getattr(resp,"status_code",0) or 0)
    headers={str(k).lower():str(v) for k,v in dict(getattr(resp,"headers",{}) or {}).items()}
    loc=headers.get("location")
    if 300<=status<400:
        return LiveFetchResult("VERIFICATION_FAILED",status,loc,headers.get("content-type"),None,"REDIRECT_BLOCKED")
    final=str(getattr(resp,"url",r.exact_product_url) or r.exact_product_url)
    if _host(final)!=r.expected_host.lower().removeprefix("www."):
        return LiveFetchResult("VERIFICATION_FAILED",status,final,headers.get("content-type"),None,"FINAL_HOST_MISMATCH")
    if status!=200:
        return LiveFetchResult("VERIFICATION_FAILED",status,final,headers.get("content-type"),None,"HTTP_STATUS_NOT_200")
    ctype=headers.get("content-type","").lower()
    if not any(x in ctype for x in ("text/html","application/xhtml+xml","application/json")):
        return LiveFetchResult("VERIFICATION_FAILED",status,final,ctype,None,"CONTENT_TYPE_BLOCKED")
    raw=getattr(resp,"content",None)
    if raw is None:
        txt=str(getattr(resp,"text",""))
        raw=txt.encode("utf-8",errors="replace")
    if len(raw)>MAX_BYTES:
        return LiveFetchResult("VERIFICATION_FAILED",status,final,ctype,None,"RESPONSE_TOO_LARGE")
    text=getattr(resp,"text",None)
    if text is None: text=raw.decode("utf-8",errors="replace")
    return LiveFetchResult("FETCHED",status,final,ctype,str(text),None)

def acquire_to_r4(
    r:LiveFetchRequest,
    transport:Callable[...,Any],
    parser:Callable[[str,LiveFetchRequest],Mapping[str,Any]],
    r4_builder:Callable[...,Any],
    r4_gate:Callable[[Any],dict[str,Any]],
)->dict[str,Any]:
    f=controlled_get(r,transport)
    base={"schema":SCHEMA,"mode":MODE,"fetch":asdict(f),"writes_performed":False,
          "method":"GET","supplier_stock_is_m99_physical_stock":False,
          "source_failure_means_zero_stock":False,"ready_for_r3":False}
    if f.status!="FETCHED":
        base["status"]="VERIFICATION_FAILED" if f.status!="BLOCKED" else "BLOCKED"
        base["blockers"]=[f.failure_reason or "FETCH_FAILED"]
        return base
    try:
        obs=dict(parser(f.body or "",r))
    except Exception as e:
        base["status"]="VERIFICATION_FAILED"; base["blockers"]=["PARSER_ERROR:"+type(e).__name__]; return base
    # identity is locked to operator request; parser may enrich but may not silently switch product.
    parsed_ref=str(obs.get("supplier_reference") or "").strip()
    if parsed_ref!=r.supplier_reference:
        base["status"]="VERIFICATION_FAILED"; base["blockers"]=["SUPPLIER_REFERENCE_MISMATCH"]; return base
    obs["supplier"]=r.supplier
    obs["supplier_reference"]=r.supplier_reference
    obs["source_url"]=r.exact_product_url
    try:
        ev=r4_builder(obs,r.expected_host)
        gate=r4_gate(ev)
    except Exception as e:
        base["status"]="VERIFICATION_FAILED"; base["blockers"]=["R4_GATE_ERROR:"+type(e).__name__]; return base
    base["r4_gate"]=gate
    base["status"]="VERIFIED" if gate.get("ready_for_r3_canonical_bridge") else "VERIFICATION_FAILED"
    base["blockers"]=list(gate.get("blockers") or [])
    base["ready_for_r3"]=base["status"]=="VERIFIED"
    return base

def static_transport_contract(transport_source:str)->list[str]:
    low=transport_source.lower()
    forbidden=("post(","put(","patch(","delete(","requests.post","requests.put","requests.patch","requests.delete")
    return [x for x in forbidden if x in low]
