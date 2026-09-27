from __future__ import annotations
from typing import Iterable
from app.services.channel_registry_governance import CHANNEL_POLICIES, ChannelPolicy

def available_governed_targets() -> list[ChannelPolicy]:
    return list(CHANNEL_POLICIES)

def resolve_governed_target_scope(requested: Iterable[str]) -> dict[str, list[str]]:
    requested_unique = list(dict.fromkeys(x.strip() for x in requested if x.strip()))
    by_key = {x.key: x for x in CHANNEL_POLICIES}
    authorized, ready, blocked = [], [], []
    for key in requested_unique:
        target = by_key.get(key)
        if target is None:
            blocked.append(key)
            continue
        if target.authorized:
            authorized.append(key)
        if target.authorized and target.ready:
            ready.append(key)
        else:
            blocked.append(key)
    return {
        "requested_targets": requested_unique,
        "authorized_targets": authorized,
        "ready_targets": ready,
        "blocked_targets": blocked,
    }
