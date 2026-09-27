from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class StandardApplicability(str, Enum):
    REQUIRED = "REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"

class StandardEvidenceSource(str, Enum):
    SUPPLIER = "OBSERVED_SUPPLIER"
    MANUFACTURER = "OBSERVED_MANUFACTURER"
    AUTHORIZED = "OTHER_AUTHORIZED_EVIDENCE"

@dataclass(frozen=True)
class StandardEvidence:
    value: str
    source: StandardEvidenceSource
    source_ref: str | None = None

@dataclass(frozen=True)
class StandardDecision:
    applicability: StandardApplicability
    standard: str | None
    provenance: StandardEvidenceSource | None
    status: str
    blockers: tuple[str, ...]
    publish_gate_pass: bool
    write_performed: bool = False

def _norm(value: str) -> str:
    return " ".join(value.upper().replace(":", " ").split())

def resolve_standard(
    applicability: StandardApplicability,
    evidence: Iterable[StandardEvidence],
) -> StandardDecision:
    items=tuple(e for e in evidence if e.value and e.value.strip())
    norms={_norm(e.value) for e in items}
    if len(norms)>1:
        return StandardDecision(applicability,None,None,"CONFLICT",
                                ("TECHNICAL_STANDARD_CONFLICT",),False,False)

    chosen=None
    for src in (StandardEvidenceSource.SUPPLIER,
                StandardEvidenceSource.MANUFACTURER,
                StandardEvidenceSource.AUTHORIZED):
        chosen=next((e for e in items if e.source is src),None)
        if chosen: break

    if applicability is StandardApplicability.NOT_APPLICABLE:
        if chosen:
            return StandardDecision(applicability,chosen.value,chosen.source,
                                    "EVIDENCE_PRESENT_NOT_REQUIRED",(),True,False)
        return StandardDecision(applicability,None,None,"NOT_APPLICABLE",(),True,False)

    if chosen:
        return StandardDecision(applicability,chosen.value,chosen.source,
                                "PROVEN",(),True,False)

    if applicability is StandardApplicability.REQUIRED:
        return StandardDecision(applicability,None,None,"REQUIRED_NOT_PROVEN",
                                ("TECHNICAL_STANDARD_REQUIRED_NOT_PROVEN",),False,False)

    return StandardDecision(applicability,None,None,"NOT_STATED",
                            ("TECHNICAL_STANDARD_APPLICABILITY_REVIEW",),False,False)
