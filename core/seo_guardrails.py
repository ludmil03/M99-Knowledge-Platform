from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class OptimizationDecision(str,Enum):
    KEEP="KEEP"
    ENRICH="ENRICH"
    REPLACE="REPLACE"

PROTECTED_FIELDS={"canonical_url","external_product_id","legacy_reference"}

@dataclass
class BaselineAudit:
    channel_id:str
    market_id:str
    current_url:str
    metrics:dict[str,Any]=field(default_factory=dict)
    observed_content:dict[str,Any]=field(default_factory=dict)

@dataclass
class CandidateEvaluation:
    decision:OptimizationDecision
    evidence:list[str]
    changed_fields:list[str]
    protected_fields_touched:list[str]=field(default_factory=list)

def evaluate_candidate(baseline,proposed_changes,evidence,improvement_fields):
    protected=[f for f in proposed_changes if f in PROTECTED_FIELDS]
    if protected or not evidence or not improvement_fields:
        return CandidateEvaluation(OptimizationDecision.KEEP,evidence,list(proposed_changes),protected)
    major={"title","meta_description","h1","description","structured_data","images"}
    decision=OptimizationDecision.REPLACE if len(major.intersection(improvement_fields))>=3 else OptimizationDecision.ENRICH
    return CandidateEvaluation(decision,evidence,list(proposed_changes),[])
