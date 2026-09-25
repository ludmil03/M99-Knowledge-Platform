"""R7.1 route installer helper.
The installer patches app.main only when a recognized FastAPI app object exists.
Actual adapter discovery is dynamic and fail-closed; no guessed HTTP implementation.
"""
from __future__ import annotations
import importlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.v073_phase46.m99_knowledge_operator_live_publish_r71 import OperatorPublishCommand, operator_publish, gate

router=APIRouter(prefix="/api/v073/r7k4/operator-publish",tags=["R7K4 Operator Publish"])

class Req(BaseModel):
    channel:str
    m99_id:str
    external_product_id:str
    operator_approved:bool=False
    canonical:dict={}
    gates:dict={}

def _adapter():
    candidates=(
      "integrations.m99eu_prestashop9.r7_live_adapter",
      "integrations.m99eu_prestashop9.publisher",
      "integrations.m99eu_prestashop9.client",
    )
    for name in candidates:
        try:
            m=importlib.import_module(name)
        except Exception:
            continue
        if all(hasattr(m,n) for n in ("preflight_existing","update_hidden","readback_existing")):
            return m
    return None

@router.post("")
def publish(req:Req):
    g=req.gates
    c=OperatorPublishCommand(req.channel,req.m99_id,req.external_product_id,req.operator_approved,
      bool(g.get("evidence_verified")),bool(g.get("duplicate_exact_existing")),bool(g.get("canonical_ready")),
      bool(g.get("pricing_ready")),bool(g.get("vat_ready")),bool(g.get("content_ready")),
      bool(g.get("images_ready")),bool(g.get("variants_ready")))
    b=gate(c)
    if b:return {"status":"BLOCKED","blockers":b,"write_attempted":False}
    a=_adapter()
    if a is None:return {"status":"BLOCKED","blockers":["VERIFIED_LIVE_ADAPTER_BINDING_NOT_FOUND"],"write_attempted":False}
    return operator_publish(c,req.canonical,a.preflight_existing,a.update_hidden,a.readback_existing)

@router.get("/capabilities")
def capabilities():
    a=_adapter()
    return {"schema":"R7K.4-R7.1","m99_knowledge_operator_publish":True,
            "channels":{"m99.eu":{"live_adapter_bound":a is not None,"mode":"UPDATE_ONLY_HIDDEN_FIRST"}},
            "operator_approval_required":True}
