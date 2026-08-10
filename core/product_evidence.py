from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class EvidenceRecord:
    source_type: str
    source_name: str
    source_url: str
    identity_strength: str
    facts: dict[str, Any]
    notes: str | None = None

def compare_supplier_candidate(manufacturer: EvidenceRecord, supplier: EvidenceRecord) -> dict:
    mf, sf = manufacturer.facts, supplier.facts
    exact_item = bool(
        mf.get("manufacturer_item")
        and sf.get("manufacturer_item")
        and str(mf.get("manufacturer_item")).strip() == str(sf.get("manufacturer_item")).strip()
    )
    same_name = (
        str(mf.get("model_name", "")).strip().lower()
        == str(sf.get("model_name", "")).strip().lower()
    )
    mf_class = str(mf.get("protection_class", "")).strip().upper()
    sf_class = str(sf.get("protection_class", "")).strip().upper()
    protection_conflict = bool(mf_class and sf_class and mf_class != sf_class)
    auto_merge = bool(exact_item and not protection_conflict)
    reasons = []
    if not exact_item:
        reasons.append("NO_EXACT_MANUFACTURER_ITEM_MATCH")
    if protection_conflict:
        reasons.append("PROTECTION_CLASS_CONFLICT")
    if same_name and not exact_item:
        reasons.append("SIMILAR_NAME_ONLY")
    return {
        "exact_manufacturer_item_match": exact_item,
        "same_normalized_model_name": same_name,
        "protection_class_conflict": protection_conflict,
        "auto_merge_allowed": auto_merge,
        "decision": "MATCH" if auto_merge else "REVIEW",
        "reasons": reasons,
    }

def evidence_bundle(manufacturer: EvidenceRecord, supplier_candidates: list[EvidenceRecord]) -> dict:
    comparisons = []
    for candidate in supplier_candidates:
        comparisons.append({
            "supplier": candidate.source_name,
            "comparison": compare_supplier_candidate(manufacturer, candidate),
            "evidence": asdict(candidate),
        })
    return {
        "manufacturer": asdict(manufacturer),
        "supplier_candidates": comparisons,
        "automatic_supplier_merge_allowed": (
            all(x["comparison"]["auto_merge_allowed"] for x in comparisons)
            if comparisons else False
        ),
    }
