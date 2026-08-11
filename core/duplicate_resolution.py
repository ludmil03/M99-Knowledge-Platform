from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum


class DuplicateResolutionDecision(str, Enum):
    MASTER_SELECTED = "MASTER_SELECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NO_CANDIDATES = "NO_CANDIDATES"


@dataclass
class MasterCandidate:
    product_id: str
    name: str | None
    url: str | None
    reference: str | None
    active: bool | None
    score: int
    model_match: bool
    exact_identifier: bool
    protection_conflict: bool
    has_clean_url: bool
    name_quality_penalty: int = 0


def _name_penalty(name: str | None) -> int:
    if not name:
        return 30
    text = " ".join(str(name).split())
    penalty = 0
    if text.endswith("2.") or text.endswith(" 2") or text.endswith("-2"):
        penalty += 25
    if len(text) > 110:
        penalty += 5
    return penalty


def _clean_url(url: str | None) -> bool:
    if not url:
        return False
    bad = ("/--", "s3s2", "undefined", "null")
    low = url.casefold()
    return not any(x in low for x in bad)


def rank_candidate(comparison: dict) -> dict:
    c = comparison["candidate"]
    exact_identifier = bool(comparison.get("matched_identity_keys"))
    score = 0

    if exact_identifier:
        score += 100
    if comparison.get("model_match"):
        score += 50
    if comparison.get("brand_match"):
        score += 15
    if c.get("reference"):
        score += 10
    if c.get("active") is True:
        score += 5

    clean = _clean_url(c.get("url"))
    if clean:
        score += 20

    penalty = _name_penalty(c.get("name"))
    score -= penalty

    if comparison.get("protection_class_conflict"):
        score -= 100

    ranked = MasterCandidate(
        product_id=str(c["product_id"]),
        name=c.get("name"),
        url=c.get("url"),
        reference=c.get("reference"),
        active=c.get("active"),
        score=score,
        model_match=bool(comparison.get("model_match")),
        exact_identifier=exact_identifier,
        protection_conflict=bool(comparison.get("protection_class_conflict")),
        has_clean_url=clean,
        name_quality_penalty=penalty,
    )
    return asdict(ranked)


def rank_candidates(comparisons: list[dict]) -> list[dict]:
    ranked = [rank_candidate(x) for x in comparisons]
    return sorted(
        ranked,
        key=lambda x: (
            x["protection_conflict"],
            -x["score"],
            x["product_id"],
        ),
    )


def resolve_duplicates(
    comparisons: list[dict],
    operator_master_product_id: str | None = None,
    operator_confirmation: str | None = None,
) -> dict:
    if not comparisons:
        return {
            "decision": DuplicateResolutionDecision.NO_CANDIDATES.value,
            "master": None,
            "duplicates": [],
            "write_allowed": False,
        }

    ranked = rank_candidates(comparisons)

    if not operator_master_product_id:
        return {
            "decision": DuplicateResolutionDecision.REVIEW_REQUIRED.value,
            "recommended_master": ranked[0],
            "ranked_candidates": ranked,
            "master": None,
            "duplicates": [],
            "write_allowed": False,
            "required_confirmation_pattern":
                "CONFIRM MASTER <PRODUCT_ID> M99 100017 MELA99",
        }

    matches = [
        x for x in ranked
        if str(x["product_id"]) == str(operator_master_product_id)
    ]
    if len(matches) != 1:
        raise ValueError("Selected master product ID is not one of the candidates")

    master = matches[0]
    if master["protection_conflict"]:
        raise ValueError("A candidate with protection-class conflict cannot be master")

    required = (
        f"CONFIRM MASTER {master['product_id']} "
        "M99 100017 MELA99"
    )
    if operator_confirmation != required:
        raise ValueError(
            "Exact operator confirmation required: " + required
        )

    duplicates = [
        dict(x, lifecycle_action="DUPLICATE_REVIEW")
        for x in ranked
        if x["product_id"] != master["product_id"]
    ]

    return {
        "decision": DuplicateResolutionDecision.MASTER_SELECTED.value,
        "master": dict(
            master,
            identity_status="EXISTING_CONFIRMED",
            product_id_action="KEEP",
            product_name_action="KEEP_BY_DEFAULT",
            slug_action="KEEP",
            url_action="KEEP",
            reference_action="KEEP_AS_LEGACY_UNLESS_OPERATOR_MIGRATES",
        ),
        "duplicates": duplicates,
        "write_allowed": True,
        "delete_allowed": False,
        "delete_policy": "NEVER_AUTOMATIC",
        "required_confirmation": required,
    }
