from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping
import re

SCHEMA="R7K.4-R7-REAL-SELECTED-CHANNEL-HIDDEN-PUBLISH"
CHANNELS=("mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com","laviro.ro","alviro.ro","toplinka.com")
M99_RE=re.compile(r"^M99 \d{6}$")

@dataclass(frozen=True)
class LivePublishRequest:
    channel:str
    m99_id:str
    external_product_id:str
    exact_confirmation:str
    evidence_verified:bool
    duplicate_exact_existing:bool
    canonical_ready:bool
    pricing_ready:bool
    vat_ready:bool
    content_ready:bool
    images_ready:bool
    variants_ready:bool

def confirmation(r:LivePublishRequest)->str:
    return f"LIVE HIDDEN UPDATE {r.m99_id} PRODUCT {r.external_product_id} ON {r.channel}"

def blockers(r:LivePublishRequest)->list[str]:
    b=[]
    if r.channel not in CHANNELS:b.append("CHANNEL_NOT_ALLOWED")
    if not M99_RE.fullmatch(r.m99_id):b.append("M99_ID_INVALID")
    if not str(r.external_product_id).strip():b.append("EXTERNAL_PRODUCT_ID_REQUIRED")
    if r.exact_confirmation!=confirmation(r):b.append("EXACT_OPERATOR_CONFIRMATION_REQUIRED")
    for ok,code in (
      (r.evidence_verified,"EVIDENCE_NOT_VERIFIED"),
      (r.duplicate_exact_existing,"EXACT_EXISTING_IDENTITY_NOT_VERIFIED"),
      (r.canonical_ready,"CANONICAL_NOT_READY"),
      (r.pricing_ready,"PRICING_NOT_READY"),
      (r.vat_ready,"VAT_NOT_READY"),
      (r.content_ready,"CONTENT_NOT_READY"),
      (r.images_ready,"IMAGES_NOT_READY"),
      (r.variants_ready,"VARIANTS_NOT_READY"),
    ):
        if not ok:b.append(code)
    return b

def hidden_contract(r:LivePublishRequest, canonical:Mapping[str,Any])->dict[str,Any]:
    return {"schema":SCHEMA,"operation":"UPDATE_ONLY","channel":r.channel,
      "m99_id":r.m99_id,"external_product_id":str(r.external_product_id),
      "active":False,"available_for_order":False,"visibility":"none",
      "inventory_write_allowed":False,"delete_allowed":False,"create_allowed":False,
      "canonical":dict(canonical)}

def execute_live_hidden_update(
 r:LivePublishRequest, canonical:Mapping[str,Any],
 adapter_preflight:Callable[[str],Mapping[str,Any]],
 adapter_update:Callable[[dict[str,Any]],Mapping[str,Any]],
 adapter_readback:Callable[[str],Mapping[str,Any]],
)->dict[str,Any]:
    out={"schema":SCHEMA,"channel":r.channel,"m99_id":r.m99_id,
         "external_product_id":str(r.external_product_id),"status":"BLOCKED",
         "write_attempted":False,"readback_verified":False,"blockers":blockers(r)}
    if out["blockers"]:return out
    try: pre=dict(adapter_preflight(str(r.external_product_id)))
    except Exception as e:
        out["blockers"]=["PREFLIGHT_ERROR:"+type(e).__name__];return out
    if str(pre.get("external_product_id",""))!=str(r.external_product_id):
        out["blockers"]=["PREFLIGHT_PRODUCT_ID_MISMATCH"];return out
    if str(pre.get("m99_id",""))!=r.m99_id:
        out["blockers"]=["PREFLIGHT_M99_ID_MISMATCH"];return out
    # R7 never updates an already-visible/orderable product in the pilot.
    if pre.get("active") is not False or pre.get("available_for_order") is not False:
        out["blockers"]=["PREFLIGHT_NOT_HIDDEN_SAFE"];return out
    payload=hidden_contract(r,canonical)
    out["write_attempted"]=True
    try: wr=dict(adapter_update(payload))
    except Exception as e:
        out["status"]="WRITE_FAILED";out["blockers"]=["WRITE_ERROR:"+type(e).__name__];return out
    if not wr.get("ok"):
        out["status"]="WRITE_FAILED";out["blockers"]=["WRITE_REJECTED"];return out
    try: rb=dict(adapter_readback(str(r.external_product_id)))
    except Exception as e:
        out["status"]="READBACK_FAILED";out["blockers"]=["READBACK_ERROR:"+type(e).__name__];return out
    checks={
      "product_id":str(rb.get("external_product_id",""))==str(r.external_product_id),
      "m99_id":str(rb.get("m99_id",""))==r.m99_id,
      "active":rb.get("active") is False,
      "orderable":rb.get("available_for_order") is False,
    }
    out["readback_checks"]=checks
    if not all(checks.values()):
        out["status"]="READBACK_FAILED";out["blockers"]=["READBACK_MISMATCH"];return out
    out["status"]="LIVE_HIDDEN_UPDATE_VERIFIED";out["readback_verified"]=True;out["blockers"]=[]
    return out
