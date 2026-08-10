from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ReadOnlyAdapterConfig:
    channel: str
    base_url: str
    timeout_seconds: int = 20


class ReadOnlyCatalogAdapter(ABC):
    """
    Contract: catalog discovery adapters may only read.
    There are intentionally no create/update/delete methods in this interface.
    """

    def __init__(self, config: ReadOnlyAdapterConfig):
        self.config = config

    @abstractmethod
    def search(self, identity: dict[str, Any]) -> list[dict]:
        raise NotImplementedError
