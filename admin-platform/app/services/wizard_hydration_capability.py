from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Any

class HydrationState(StrEnum):
    READY="READY"
    BLOCKED="BLOCKED"

@dataclass(frozen=True)
class HydrationCapability:
    source_organization_id:str
    supplier_key:str
    state:HydrationState
    runtime:str|None
    reason:str
    network_read_required:bool=False
    write_performed:bool=False

_CAPABILITIES={
    "org-bultex":HydrationCapability("org-bultex","BULTEX99",HydrationState.READY,
        "app.services.bultex99_readonly_hydration.hydrate_bultex99_product",
        "BULTEX99 read-only hydration contract accepted in A3.",True,False),
    "org-palltex":HydrationCapability("org-palltex","PALLTEX",HydrationState.BLOCKED,None,
        "PALLTEX evidence adapter proven; live wizard hydration runtime not proven."),
    "org-calenda":HydrationCapability("org-calenda","CALENDA",HydrationState.BLOCKED,None,
        "CALENDA evidence adapter proven; approved wizard organization/live hydration not proven."),
}
def hydration_capability(source_organization_id:str|None)->HydrationCapability:
    key=str(source_organization_id or "").strip()
    return _CAPABILITIES.get(key,HydrationCapability(key,"",HydrationState.BLOCKED,None,"SUPPLIER_HYDRATION_NOT_REGISTERED"))
def require_proven_hydration(source_organization_id:str|None)->HydrationCapability:
    c=hydration_capability(source_organization_id)
    if c.state is not HydrationState.READY: raise ValueError("HYDRATION_NOT_READY:"+c.reason)
    return c
def hydrate_for_wizard(source_organization_id:str|None,product_refs:list[str],*,runtime_call:Callable[...,Any]|None=None)->list[Any]:
    c=require_proven_hydration(source_organization_id)
    if runtime_call is None: raise ValueError("HYDRATION_RUNTIME_MISSING")
    if c.supplier_key!="BULTEX99": raise ValueError("HYDRATION_RUNTIME_BINDING_NOT_IMPLEMENTED")
    out=[]
    for ref in product_refs:
        result=runtime_call(ref)
        product=getattr(result,"product",None)
        if product is None: raise ValueError("HYDRATION_RESULT_INVALID")
        if bool(getattr(result,"write_performed",True)): raise ValueError("HYDRATION_WRITE_INVARIANT_FAILED")
        out.append(product)
    return out
