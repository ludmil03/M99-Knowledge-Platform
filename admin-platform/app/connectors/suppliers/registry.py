from __future__ import annotations

from typing import Callable

from .contract import SupplierConnector


class SupplierConnectorRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., SupplierConnector]] = {}

    def register(self, key: str, factory: Callable[..., SupplierConnector]) -> None:
        normalized = key.strip().lower()
        if not normalized:
            raise ValueError("Connector key is required.")
        self._factories[normalized] = factory

    def create(self, key: str, **kwargs) -> SupplierConnector:
        normalized = key.strip().lower()
        factory = self._factories.get(normalized)
        if factory is None:
            raise KeyError(f"Supplier connector is not registered: {key}")
        connector = factory(**kwargs)
        if not connector.read_only:
            raise ValueError("Supplier Browser connectors must be read-only.")
        return connector

    def keys(self) -> list[str]:
        return sorted(self._factories)
