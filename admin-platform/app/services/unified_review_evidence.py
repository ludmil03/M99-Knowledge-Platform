from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.services.product_variant_evidence_gate import build_product_variant_evidence
from app.services.standard_evidence_policy import (
 StandardApplicability, StandardEvidence, StandardEvidenceSource, resolve_standard
)

@dataclass(frozen=True)
class UnifiedReviewEvidence:
 supplier_product_id:str
 supplier_product_sku:str|None
 variants:tuple[str,...]
 availability:str|None
 standard:str|None
 standard_status:str
 standard_provenance:str|None
 blockers:tuple[str,...]
 review_ready:bool
 publish_enabled:bool=False
 write_performed:bool=False

def build_unified_review_evidence(
 product:Any, *, variant_values:tuple[str,...]=(),
 standard_applicability:StandardApplicability=StandardApplicability.UNKNOWN,
 manufacturer_standard:str|None=None,
 authorized_standard:str|None=None,
)->UnifiedReviewEvidence:
 pv=build_product_variant_evidence(product,variant_values=variant_values)
 ev=[]
 if getattr(product,"standard",None):
  ev.append(StandardEvidence(str(product.standard),StandardEvidenceSource.SUPPLIER))
 if manufacturer_standard:
  ev.append(StandardEvidence(manufacturer_standard,StandardEvidenceSource.MANUFACTURER))
 if authorized_standard:
  ev.append(StandardEvidence(authorized_standard,StandardEvidenceSource.AUTHORIZED))
 sd=resolve_standard(standard_applicability,ev)
 # A9 supersedes A6's unconditional missing-standard blocker.
 blockers=tuple(b for b in pv.blockers if b!="TECHNICAL_STANDARD_MISSING")+sd.blockers
 return UnifiedReviewEvidence(
  pv.supplier_product_id,pv.supplier_product_sku,
  tuple(v.value for v in pv.variants),pv.availability,
  sd.standard,sd.status,sd.provenance.value if sd.provenance else None,
  blockers,not blockers,False,False)
