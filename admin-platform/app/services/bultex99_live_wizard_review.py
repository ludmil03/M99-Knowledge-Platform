from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from app.services.bultex99_readonly_hydration import hydrate_bultex99_product
from app.services.standard_evidence_policy import StandardApplicability
from app.services.wizard_unified_review_context import build_wizard_review_context
@dataclass(frozen=True)
class LiveWizardReviewResult:
 source_url:str
 context:dict
 get_count:int
 write_performed:bool=False
def build_bultex99_live_wizard_review(source_url:str,*,get:Callable[[str],tuple[int,str,str]],variant_values:tuple[str,...]=(),standard_applicability:StandardApplicability=StandardApplicability.UNKNOWN)->LiveWizardReviewResult:
 calls=0
 def counted_get(url:str)->tuple[int,str,str]:
  nonlocal calls
  calls+=1
  if calls>1: raise RuntimeError("LIVE_READ_BUDGET_EXCEEDED")
  result=get(url)
  if not isinstance(result,tuple) or len(result)!=3:
   raise TypeError("BULTEX_GET_CONTRACT_EXPECTED_STATUS_FINAL_URL_HTML")
  return result
 hydrated=hydrate_bultex99_product(source_url,get=counted_get)
 if hydrated.write_performed: raise RuntimeError("UNEXPECTED_WRITE_STATE")
 context=build_wizard_review_context(hydrated.product,variant_values=variant_values,standard_applicability=standard_applicability)
 context["live_read"]={"source_url":source_url,"get_count":calls}
 context["publish_enabled"]=False;context["write_performed"]=False
 return LiveWizardReviewResult(source_url,context,calls,False)
