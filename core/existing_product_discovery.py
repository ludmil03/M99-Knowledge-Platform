from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass
class DiscoveryEvidence:
    channel: str
    query_type: str
    query_value: str
    result: str
    matched_url: str | None = None
    matched_product_id: str | None = None
    notes: str | None = None


EXACT_RESULTS = {"EXACT_MATCH"}
NONPROOF_RESULTS = {
    "NO_PUBLIC_EXACT_MATCH_FOUND",
    "NOT_INDEXED_OR_NOT_FOUND",
}


def evaluate_channel_discovery(records: Iterable[DiscoveryEvidence]) -> dict:
    records = list(records)

    exact = [r for r in records if r.result in EXACT_RESULTS]
    if exact:
        best = exact[0]
        return {
            "status": "EXACT_MATCH_FOUND",
            "first_publish_allowed": False,
            "action": "LINK_EXISTING_PRODUCT",
            "preserve_existing_url": True,
            "preserve_existing_product_id": True,
            "matched_url": best.matched_url,
            "matched_product_id": best.matched_product_id,
            "operator_confirmation_required": True,
            "evidence": [asdict(r) for r in records],
        }

    # A public-search miss is deliberately NOT interpreted as proof
    # that a product is absent from the channel.
    return {
        "status": "NO_PUBLIC_EXACT_MATCH_FOUND_REVIEW_REQUIRED",
        "first_publish_allowed": False,
        "action": "OPERATOR_VERIFY_CHANNEL_BEFORE_CREATE",
        "preserve_existing_url": False,
        "preserve_existing_product_id": False,
        "matched_url": None,
        "matched_product_id": None,
        "operator_confirmation_required": True,
        "evidence": [asdict(r) for r in records],
    }


def evaluate_discovery(records: Iterable[DiscoveryEvidence]) -> dict:
    by_channel = {}
    for record in records:
        by_channel.setdefault(record.channel, []).append(record)

    channels = {
        channel: evaluate_channel_discovery(items)
        for channel, items in sorted(by_channel.items())
    }

    return {
        "status": "REVIEW_REQUIRED",
        "all_channels_verified": all(
            item["status"] == "EXACT_MATCH_FOUND"
            for item in channels.values()
        ),
        "channels": channels,
        "rule": (
            "A missing public search result does not prove that the product "
            "does not already exist in the channel."
        ),
    }
