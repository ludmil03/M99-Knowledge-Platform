from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from app.services.supplier_product_evidence import SupplierProductEvidence
from app.services.supplier_evidence_adapters import from_bultex99, from_calenda, from_palltex
Adapter=Callable[[Any],SupplierProductEvidence]
@dataclass(frozen=True)
class SupplierAdapterRegistration:
    key: str
    adapter: Adapter
    status: str = "PROVEN"
    note: str = ""
_REGISTRY={
 "BULTEX99":SupplierAdapterRegistration("BULTEX99",from_bultex99),
 "CALENDA":SupplierAdapterRegistration("CALENDA",from_calenda),
 "PALLTEX":SupplierAdapterRegistration("PALLTEX",from_palltex),
}
def normalize_supplier_key(value:str)->str:
    return str(value or "").strip().upper().replace("-","_").replace(" ","_")
def registered_suppliers()->tuple[str,...]:
    return tuple(_REGISTRY)
def get_registration(supplier_key:str)->SupplierAdapterRegistration:
    key=normalize_supplier_key(supplier_key)
    reg=_REGISTRY.get(key)
    if reg is None:
        raise ValueError(f"UNSUPPORTED_SUPPLIER;SUPPLIER_NOT_REGISTERED:{key or 'EMPTY'}")
    if reg.status!="PROVEN":
        raise ValueError(f"SUPPLIER_ADAPTER_NOT_PROVEN:{key}")
    return reg
def normalize_registered_supplier(supplier_key:str,hydrated:Any)->SupplierProductEvidence:
    reg=get_registration(supplier_key)
    evidence=reg.adapter(hydrated)
    errors=evidence.validate()
    if errors:
        raise ValueError("INVALID_SUPPLIER_EVIDENCE:"+",".join(errors))
    return evidence
