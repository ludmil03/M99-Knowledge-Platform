from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Mapping

@dataclass(frozen=True)
class EvidenceFact:
    value: Any
    source: str
    source_url: str | None = None
    confidence: str = "OBSERVED"

@dataclass(frozen=True)
class SupplierProductEvidence:
    supplier_key: str
    source_key: str
    source_url: str
    identity_facts: Mapping[str, EvidenceFact] = field(default_factory=dict)
    technical_facts: Mapping[str, EvidenceFact] = field(default_factory=dict)
    images: tuple[EvidenceFact, ...] = ()
    price: EvidenceFact | None = None
    availability: EvidenceFact | None = None
    variants: tuple[Mapping[str, Any], ...] = ()
    commercial_evidence: Mapping[str, EvidenceFact] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> tuple[str, ...]:
        errors=[]
        if not self.supplier_key.strip(): errors.append("SUPPLIER_KEY_MISSING")
        if not self.source_key.strip(): errors.append("SOURCE_KEY_MISSING")
        if not self.source_url.startswith("https://"): errors.append("SOURCE_URL_NOT_HTTPS")
        if not self.identity_facts: errors.append("IDENTITY_FACTS_MISSING")
        return tuple(errors)
