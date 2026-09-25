from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping

SCHEMA="R7K.4-R7.1-M99-KNOWLEDGE-OPERATOR-LIVE-PUBLISH"
SUPPORTED_CHANNELS=("m99.eu",)  # first real bound channel; others fail closed

@dataclass(frozen=True)
class OperatorPublishCommand:
    channel:str
    m99_id:str
    external_product_id:str
    operator_approved:bool
    evidence_verified:bool
    duplicate_exact_existing:bool
    canonical_ready:bool
    pricing_ready:bool
    vat_ready:bool
    content_ready:bool
    images_ready:bool
    variants_ready:bool

def gate(c:OperatorPublishCommand)->list[str]:
    b=[]
    if c.channel not in SUPPORTED_CHANNELS:b.append("LIVE_ADAPTER_NOT_BOUND_FOR_CHANNEL")
    if not c.operator_approved:b.append("OPERATOR_APPROVAL_REQUIRED")
    if not c.m99_id.startswith("M99 ") or len(c.m99_id)!=10 or not c.m99_id[4:].isdigit():b.append("M99_ID_INVALID")
    if not str(c.external_product_id).strip():b.append("EXTERNAL_PRODUCT_ID_REQUIRED")
    for ok,code in (
      (c.evidence_verified,"EVIDENCE_NOT_VERIFIED"),
      (c.duplicate_exact_existing,"EXACT_EXISTING_IDENTITY_NOT_VERIFIED"),
      (c.canonical_ready,"CANONICAL_NOT_READY"),
      (c.pricing_ready,"PRICING_NOT_READY"),
      (c.vat_ready,"VAT_NOT_READY"),
      (c.content_ready,"CONTENT_NOT_READY"),
      (c.images_ready,"IMAGES_NOT_READY"),
      (c.variants_ready,"VARIANTS_NOT_READY"),
    ):
        if not ok:b.append(code)
    return b

def operator_publish(c:OperatorPublishCommand, canonical:Mapping[str,Any],
                     preflight:Callable[[str],Mapping[str,Any]],
                     update_hidden:Callable[[dict[str,Any]],Mapping[str,Any]],
                     readback:Callable[[str],Mapping[str,Any]])->dict[str,Any]:
    out={"schema":SCHEMA,"status":"BLOCKED","channel":c.channel,"m99_id":c.m99_id,
         "external_product_id":str(c.external_product_id),"write_attempted":False,
         "readback_verified":False,"blockers":gate(c)}
    if out["blockers"]: return out
    try: p=dict(preflight(str(c.external_product_id)))
    except Exception as e:
        out["blockers"]=["PREFLIGHT_ERROR:"+type(e).__name__]; return out
    if str(p.get("external_product_id",""))!=str(c.external_product_id) or str(p.get("m99_id",""))!=c.m99_id:
        out["blockers"]=["PREFLIGHT_IDENTITY_MISMATCH"]; return out
    if p.get("active") is not False or p.get("available_for_order") is not False:
        out["blockers"]=["PREFLIGHT_NOT_HIDDEN_SAFE"]; return out
    payload={"operation":"UPDATE_ONLY","channel":c.channel,"m99_id":c.m99_id,
             "external_product_id":str(c.external_product_id),"active":False,
             "available_for_order":False,"visibility":"none","create_allowed":False,
             "delete_allowed":False,"inventory_write_allowed":False,"canonical":dict(canonical)}
    out["write_attempted"]=True
    try: w=dict(update_hidden(payload))
    except Exception as e:
        out["status"]="WRITE_FAILED";out["blockers"]=["WRITE_ERROR:"+type(e).__name__];return out
    if not w.get("ok"):
        out["status"]="WRITE_FAILED";out["blockers"]=["WRITE_REJECTED"];return out
    try:r=dict(readback(str(c.external_product_id)))
    except Exception as e:
        out["status"]="READBACK_FAILED";out["blockers"]=["READBACK_ERROR:"+type(e).__name__];return out
    checks={"product_id":str(r.get("external_product_id",""))==str(c.external_product_id),
            "m99_id":str(r.get("m99_id",""))==c.m99_id,
            "hidden":r.get("active") is False,
            "not_orderable":r.get("available_for_order") is False}
    out["readback_checks"]=checks
    if not all(checks.values()):
        out["status"]="READBACK_FAILED";out["blockers"]=["READBACK_MISMATCH"];return out
    out["status"]="LIVE_HIDDEN_UPDATE_VERIFIED";out["readback_verified"]=True;out["blockers"]=[]
    return out
