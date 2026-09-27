from __future__ import annotations
from dataclasses import asdict
from typing import Any
from app.services.standard_evidence_policy import StandardApplicability
from app.services.unified_review_evidence import build_unified_review_evidence
def build_wizard_review_context(product:Any, *, variant_values:tuple[str,...]=(), standard_applicability:StandardApplicability=StandardApplicability.UNKNOWN, manufacturer_standard:str|None=None, authorized_standard:str|None=None)->dict:
 r=build_unified_review_evidence(product,variant_values=variant_values,standard_applicability=standard_applicability,manufacturer_standard=manufacturer_standard,authorized_standard=authorized_standard)
 return {"product_evidence":asdict(r),"publish_enabled":False,"write_performed":False}
