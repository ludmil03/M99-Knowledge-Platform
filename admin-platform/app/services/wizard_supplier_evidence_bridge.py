from __future__ import annotations
from dataclasses import asdict
from typing import Any
from app.services.supplier_evidence_runtime import normalize_supplier_evidence

def build_wizard_evidence_preview(supplier_key: str, hydrated_products: list[Any]) -> dict[str, object]:
    items=[]
    warnings=[]
    for product in hydrated_products:
        evidence=normalize_supplier_evidence(supplier_key, product)
        identity={k:v.value for k,v in evidence.identity_facts.items()}
        items.append({
            "supplier_key": evidence.supplier_key,
            "source_key": evidence.source_key,
            "source_url": evidence.source_url,
            "identity": identity,
            "technical_fact_count": len(evidence.technical_facts),
            "image_count": len(evidence.images),
            "variant_count": len(evidence.variants),
            "has_price": evidence.price is not None,
            "has_availability": evidence.availability is not None,
            "warnings": list(evidence.warnings),
        })
        warnings.extend(evidence.warnings)
    return {
        "supplier_key": str(supplier_key or "").strip().upper(),
        "items": items,
        "count": len(items),
        "warnings": list(dict.fromkeys(warnings)),
        "write_performed": False,
    }
