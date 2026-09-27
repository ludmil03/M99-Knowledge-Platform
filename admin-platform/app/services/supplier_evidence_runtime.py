from __future__ import annotations
from typing import Any
from app.services.supplier_product_evidence import SupplierProductEvidence
from app.services.supplier_adapter_registry import normalize_registered_supplier,registered_suppliers
def supported_suppliers()->tuple[str,...]:
    return registered_suppliers()
def normalize_supplier_evidence(supplier_key:str,hydrated:Any)->SupplierProductEvidence:
    return normalize_registered_supplier(supplier_key,hydrated)
