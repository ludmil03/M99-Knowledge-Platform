from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable, Mapping, Sequence
import re

SCHEMA="R7K.4-R6-OPERATOR-SELECTED-CHANNEL-PUBLISH"
ALLOWED_CHANNELS=(
 "mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com",
 "laviro.ro","alviro.ro","toplinka.com",
)
WRITE_MODES=("UPDATE_ONLY",)  # CREATE remains blocked in R6.
M99_RE=re.compile(r"^M99 \d{6}$")

@dataclass(frozen=True)
class PublishRequest:
    m99_id:str
    channel:str
    external_product_id:str
    operation:str="UPDATE_ONLY"
    operator_confirmation:str=""
    evidence_verified:bool=False
    canonical_ready:bool=False
    pricing_ready:bool=False
    vat_ready:bool=False
    content_ready:bool=False
    images_ready:bool=False
    variants_ready:bool=False

def expected_confirmation(r:PublishRequest)->str:
    return f"PUBLISH {r.m99_id} TO {r.channel}"

def validate_request(r:PublishRequest)->list[str]:
    b=[]
    if not M99_RE.fullmatch(r.m99_id): b.append("M99_ID_INVALID")
    if r.channel not in ALLOWED_CHANNELS: b.append("CHANNEL_NOT_ALLOWED")
    if not str(r.external_product_id).strip(): b.append("EXTERNAL_PRODUCT_ID_REQUIRED")
    if r.operation not in WRITE_MODES: b.append("CREATE_BLOCKED_R6")
    if r.operator_confirmation != expected_confirmation(r): b.append("EXACT_OPERATOR_CONFIRMATION_REQUIRED")
    for ok,code in (
      (r.evidence_verified,"EVIDENCE_NOT_VERIFIED"),
      (r.canonical_ready,"CANONICAL_NOT_READY"),
      (r.pricing_ready,"PRICING_NOT_READY"),
      (r.vat_ready,"VAT_NOT_READY"),
      (r.content_ready,"CONTENT_NOT_READY"),
      (r.images_ready,"IMAGES_NOT_READY"),
      (r.variants_ready,"VARIANTS_NOT_READY"),
    ):
        if not ok:b.append(code)
    return b

def build_hidden_update_payload(r:PublishRequest, canonical:Mapping[str,Any])->dict[str,Any]:
    """Channel-neutral contract. Adapter translates it to PS/WP fields."""
    return {
      "schema":SCHEMA,"m99_id":r.m99_id,"channel":r.channel,
      "external_product_id":str(r.external_product_id),"operation":"UPDATE_ONLY",
      "publication_state":"HIDDEN_FIRST","active":False,"available_for_order":False,
      "canonical":dict(canonical),
      "inventory_write_allowed":False,
      "delete_allowed":False,
    }

def controlled_publish(
    r:PublishRequest,
    canonical:Mapping[str,Any],
    adapter_update:Callable[[dict[str,Any]],Mapping[str,Any]],
    adapter_readback:Callable[[str],Mapping[str,Any]],
)->dict[str,Any]:
    blockers=validate_request(r)
    base={"schema":SCHEMA,"channel":r.channel,"m99_id":r.m99_id,
          "operation":r.operation,"write_attempted":False,"write_accepted":False,
          "readback_verified":False,"status":"BLOCKED","blockers":blockers}
    if blockers:return base
    payload=build_hidden_update_payload(r,canonical)
    base["write_attempted"]=True
    try:
        wr=dict(adapter_update(payload))
    except Exception as e:
        base["status"]="WRITE_FAILED"; base["blockers"]=["ADAPTER_WRITE_ERROR:"+type(e).__name__]; return base
    if not wr.get("ok"):
        base["status"]="WRITE_FAILED"; base["blockers"]=["ADAPTER_WRITE_REJECTED"]; return base
    base["write_accepted"]=True
    try:
        rb=dict(adapter_readback(str(r.external_product_id)))
    except Exception as e:
        base["status"]="READBACK_FAILED"; base["blockers"]=["READBACK_ERROR:"+type(e).__name__]; return base
    checks={
      "external_product_id":str(rb.get("external_product_id",""))==str(r.external_product_id),
      "m99_id":str(rb.get("m99_id",""))==r.m99_id,
      "hidden":rb.get("active") is False,
      "not_orderable":rb.get("available_for_order") is False,
    }
    base["readback_checks"]=checks
    if not all(checks.values()):
        base["status"]="READBACK_FAILED"; base["blockers"]=[f"READBACK_{k.upper()}_MISMATCH" for k,v in checks.items() if not v]; return base
    base["readback_verified"]=True; base["status"]="PUBLISHED_HIDDEN_VERIFIED"; base["blockers"]=[]
    return base

def select_channels(requested:Sequence[str])->tuple[str,...]:
    """Preserve operator order, dedupe, reject unknown. No implicit ALL."""
    out=[]
    for c in requested:
        if c not in ALLOWED_CHANNELS: raise ValueError("CHANNEL_NOT_ALLOWED:"+str(c))
        if c not in out: out.append(c)
    if not out: raise ValueError("AT_LEAST_ONE_CHANNEL_REQUIRED")
    return tuple(out)
