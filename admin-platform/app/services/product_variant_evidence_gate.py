from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class VariantEvidence:
    dimension:str
    value:str
    supplier_variant_ref:str|None=None

@dataclass(frozen=True)
class ProductVariantEvidence:
    supplier_product_id:str
    supplier_product_sku:str|None
    variants:tuple[VariantEvidence,...]
    availability:str|None
    standard:str|None
    blockers:tuple[str,...]
    can_continue_to_content:bool
    write_performed:bool=False

def build_product_variant_evidence(product:Any, *, variant_values:tuple[str,...]=())->ProductVariantEvidence:
    pid=str(getattr(product,"supplier_product_id","") or "").strip()
    sku=str(getattr(product,"supplier_sku","") or "").strip() or None
    if not pid: raise ValueError("SUPPLIER_PRODUCT_ID_MISSING")
    blockers=[]
    if not sku: blockers.append("SUPPLIER_PRODUCT_SKU_MISSING")
    if sku and sku.endswith(tuple("."+str(x) for x in range(1,100))):
        blockers.append("PRODUCT_VARIANT_IDENTITY_FUSED")
    standard=str(getattr(product,"standard","") or "").strip() or None
    if not standard: blockers.append("TECHNICAL_STANDARD_MISSING")
    availability=str(getattr(product,"availability","") or "").strip() or None
    variants=tuple(VariantEvidence("size",str(v).strip()) for v in variant_values if str(v).strip())
    return ProductVariantEvidence(pid,sku,variants,availability,standard,tuple(blockers),not blockers,False)
