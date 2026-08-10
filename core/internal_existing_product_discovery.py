from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import re
from typing import Iterable


class InternalDiscoveryDecision(str, Enum):
    EXISTING = "EXISTING"
    NEW = "NEW"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    CONFLICT = "CONFLICT"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    ERROR = "ERROR"


@dataclass
class CanonicalIdentity:
    brand: str
    model_name: str
    manufacturer_item: str | None = None
    ean: str | None = None
    legacy_identifiers: list[str] | None = None
    protection_class: str | None = None


@dataclass
class CatalogCandidate:
    channel: str
    product_id: str
    url: str | None = None
    name: str | None = None
    brand: str | None = None
    reference: str | None = None
    ean: str | None = None
    legacy_identifiers: list[str] | None = None
    protection_class: str | None = None
    active: bool | None = None
    raw_source: str | None = None


def _norm(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().casefold()
    text = re.sub(r"[\s._/\-]+", "", text)
    return text


def _norm_name(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().casefold()
    text = re.sub(r"[^0-9a-zа-яăâîșț\s]+", " ", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _legacy_overlap(identity: CanonicalIdentity, candidate: CatalogCandidate) -> bool:
    wanted = {_norm(x) for x in (identity.legacy_identifiers or []) if _norm(x)}
    found = {_norm(x) for x in (candidate.legacy_identifiers or []) if _norm(x)}
    return bool(wanted & found)


def compare_candidate(identity: CanonicalIdentity, candidate: CatalogCandidate) -> dict:
    reasons = []
    exact_keys = []

    manufacturer_ref_match = bool(
        identity.manufacturer_item
        and candidate.reference
        and _norm(identity.manufacturer_item) == _norm(candidate.reference)
    )
    if manufacturer_ref_match:
        exact_keys.append("manufacturer_item")

    ean_match = bool(
        identity.ean
        and candidate.ean
        and _norm(identity.ean) == _norm(candidate.ean)
    )
    if ean_match:
        exact_keys.append("ean")

    legacy_match = _legacy_overlap(identity, candidate)
    legacy_reference_match = bool(
        candidate.reference
        and any(
            _norm(candidate.reference) == _norm(x)
            for x in (identity.legacy_identifiers or [])
            if _norm(x)
        )
    )
    if legacy_match or legacy_reference_match:
        exact_keys.append("legacy_identifier")

    model_match = bool(
        identity.model_name
        and candidate.name
        and _norm_name(identity.model_name) == _norm_name(candidate.name)
    )
    brand_match = bool(
        identity.brand
        and candidate.brand
        and _norm_name(identity.brand) == _norm_name(candidate.brand)
    )

    protection_conflict = bool(
        identity.protection_class
        and candidate.protection_class
        and _norm(identity.protection_class) != _norm(candidate.protection_class)
    )

    # An exact technical identifier with contradictory protection data is not
    # silently accepted. It is an operator conflict.
    if exact_keys and protection_conflict:
        decision = InternalDiscoveryDecision.CONFLICT
        reasons.extend(exact_keys)
        reasons.append("PROTECTION_CLASS_CONFLICT")
        score = 100
    elif exact_keys:
        decision = InternalDiscoveryDecision.EXISTING
        reasons.extend(exact_keys)
        score = 100
    elif model_match and brand_match:
        decision = InternalDiscoveryDecision.POSSIBLE_DUPLICATE
        reasons.extend(["exact_normalized_model_name", "brand_match"])
        if protection_conflict:
            reasons.append("PROTECTION_CLASS_CONFLICT")
        score = 75
    elif model_match:
        decision = InternalDiscoveryDecision.POSSIBLE_DUPLICATE
        reasons.append("exact_normalized_model_name")
        if protection_conflict:
            reasons.append("PROTECTION_CLASS_CONFLICT")
        score = 60
    else:
        decision = InternalDiscoveryDecision.NEW
        score = 0

    return {
        "candidate": asdict(candidate),
        "decision": decision.value,
        "score": score,
        "matched_identity_keys": exact_keys,
        "model_match": model_match,
        "brand_match": brand_match,
        "protection_class_conflict": protection_conflict,
        "reasons": reasons,
    }


def decide_channel(identity: CanonicalIdentity, candidates: Iterable[CatalogCandidate]) -> dict:
    comparisons = [compare_candidate(identity, c) for c in candidates]

    conflicts = [x for x in comparisons if x["decision"] == InternalDiscoveryDecision.CONFLICT.value]
    existing = [x for x in comparisons if x["decision"] == InternalDiscoveryDecision.EXISTING.value]
    possible = [x for x in comparisons if x["decision"] == InternalDiscoveryDecision.POSSIBLE_DUPLICATE.value]

    if conflicts:
        decision = InternalDiscoveryDecision.CONFLICT
        selected = conflicts[0]
        action = "OPERATOR_REVIEW"
    elif len(existing) == 1:
        decision = InternalDiscoveryDecision.EXISTING
        selected = existing[0]
        action = "UPDATE_EXISTING_PRESERVE_ID_AND_URL"
    elif len(existing) > 1:
        decision = InternalDiscoveryDecision.CONFLICT
        selected = None
        action = "OPERATOR_REVIEW_MULTIPLE_EXACT_MATCHES"
    elif possible:
        decision = InternalDiscoveryDecision.POSSIBLE_DUPLICATE
        selected = possible[0]
        action = "OPERATOR_REVIEW_BEFORE_CREATE"
    else:
        decision = InternalDiscoveryDecision.NEW
        selected = None
        action = "CREATE_CANDIDATE"

    selected_candidate = selected["candidate"] if selected else None

    return {
        "decision": decision.value,
        "action": action,
        "publish_allowed": False,
        "operator_confirmation_required": True,
        "preserve_existing_product_id": decision == InternalDiscoveryDecision.EXISTING,
        "preserve_existing_url": decision == InternalDiscoveryDecision.EXISTING,
        "selected_product_id": selected_candidate.get("product_id") if selected_candidate else None,
        "selected_url": selected_candidate.get("url") if selected_candidate else None,
        "comparisons": comparisons,
    }


def discover_existing_product(channel: str, canonical_product: dict, candidates: list[dict]) -> dict:
    """
    Generic, platform-independent decision function.
    Platform adapters only READ and normalize their catalog records into candidates.
    """
    identity = CanonicalIdentity(
        brand=str(canonical_product.get("brand", "")).strip(),
        model_name=str(canonical_product.get("model_name", "")).strip(),
        manufacturer_item=canonical_product.get("manufacturer_item"),
        ean=canonical_product.get("ean"),
        legacy_identifiers=list(canonical_product.get("legacy_identifiers") or []),
        protection_class=canonical_product.get("protection_class"),
    )
    normalized = [
        CatalogCandidate(channel=channel, **item)
        for item in candidates
    ]
    result = decide_channel(identity, normalized)
    result["channel"] = channel
    result["canonical_identity"] = asdict(identity)
    return result
