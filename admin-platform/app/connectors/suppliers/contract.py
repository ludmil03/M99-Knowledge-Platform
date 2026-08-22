from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SupplierCapability(StrEnum):
    IDENTITY = "IDENTITY"
    TECHNICAL_FACTS = "TECHNICAL_FACTS"
    MPN = "MPN"
    EAN_GTIN = "EAN_GTIN"
    IMAGES = "IMAGES"
    DOCUMENTS = "DOCUMENTS"
    CATALOGUES = "CATALOGUES"
    PRICE = "PRICE"
    PURCHASE_PRICE = "PURCHASE_PRICE"
    AVAILABILITY = "AVAILABILITY"
    LEAD_TIME = "LEAD_TIME"
    VARIANTS = "VARIANTS"
    STOCK = "STOCK"
    ORDER_TERMS = "ORDER_TERMS"


@dataclass(frozen=True)
class CategoryRecord:
    key: str
    name: str
    url: str
    product_count: int | None = None
    parent_key: str | None = None


@dataclass(frozen=True)
class ProductSummary:
    source_key: str
    name: str
    url: str
    price_text: str | None = None
    availability_text: str | None = None
    image_url: str | None = None


@dataclass(frozen=True)
class ProductDetail:
    source_key: str
    name: str
    url: str
    reference: str | None = None
    mpn: str | None = None
    ean: str | None = None
    price_text: str | None = None
    availability_text: str | None = None
    description_text: str | None = None
    images: tuple[str, ...] = ()
    variants: tuple[dict[str, Any], ...] = ()
    facts: dict[str, Any] = field(default_factory=dict)


class SupplierConnector(ABC):
    """Read-only live supplier connector contract.

    A connector may perform GET/read operations only. It MUST NOT create orders,
    modify supplier data or write to M99 sales channels.
    """

    key: str
    read_only: bool = True

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_categories(self) -> list[CategoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def list_products(
        self,
        category_key: str,
        *,
        page: int = 1,
        limit: int = 100,
    ) -> list[ProductSummary]:
        raise NotImplementedError

    @abstractmethod
    def get_product(self, source_key: str) -> ProductDetail:
        raise NotImplementedError

    def get_variants(self, source_key: str) -> list[dict[str, Any]]:
        return list(self.get_product(source_key).variants)

    def get_images(self, source_key: str) -> list[str]:
        return list(self.get_product(source_key).images)

    def get_commercial_data(self, source_key: str) -> dict[str, Any]:
        product = self.get_product(source_key)
        return {
            "price_text": product.price_text,
            "availability_text": product.availability_text,
        }
