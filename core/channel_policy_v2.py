from __future__ import annotations
import json
from pathlib import Path


class ChannelPolicy:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))

    def eligible(self, channel: str, applications: set[str]) -> bool:
        cfg = self.config["channels"][channel]
        allowed = set(cfg["allow"])
        if cfg.get("strict_medical_only"):
            return "medical" in applications
        return bool(allowed.intersection(applications))

    def eligible_channels(self, applications: set[str]) -> list[str]:
        return [
            channel for channel in self.config["channels"]
            if self.eligible(channel, applications)
        ]

    def publication_requires_approval(self) -> bool:
        return bool(self.config["publication"]["new_productgroup_requires_operator_approval"])

    def url_is_protected(self) -> bool:
        return bool(self.config["publication"]["existing_url_is_protected"])
