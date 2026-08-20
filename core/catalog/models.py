from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping

from .enums import ProductLifecycle, PublicationStatus, ChannelKind


def _required(value: str, field_name: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field_name} is required")
    return value


def _positive_decimal(value: Decimal | str | int | float, field_name: str) -> Decimal:
    d = Decimal(str(value))
    if d < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return d


@dataclass(frozen=True)
class ExternalIdentity:
    system: str
    external_id: str
    entity_type: str

    def __post_init__(self):
        object.__setattr__(self, "system", _required(self.system, "system"))
        object.__setattr__(self, "external_id", _required(self.external_id, "external_id"))
        object.__setattr__(self, "entity_type", _required(self.entity_type, "entity_type"))


@dataclass
class ProductGroup:
    m99_id: str
    name: str
    lifecycle: ProductLifecycle = ProductLifecycle.DRAFT
    external_ids: list[ExternalIdentity] = field(default_factory=list)

    def __post_init__(self):
        self.m99_id = _required(self.m99_id, "m99_id")
        self.name = _required(self.name, "name")


@dataclass
class Product:
    m99_id: str
    product_group_id: str
    name: str
    lifecycle: ProductLifecycle = ProductLifecycle.DRAFT
    external_ids: list[ExternalIdentity] = field(default_factory=list)

    def __post_init__(self):
        self.m99_id = _required(self.m99_id, "m99_id")
        self.product_group_id = _required(self.product_group_id, "product_group_id")
        self.name = _required(self.name, "name")


@dataclass
class ProductVariant:
    m99_id: str
    product_id: str
    variant_key: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    lifecycle: ProductLifecycle = ProductLifecycle.DRAFT
    external_ids: list[ExternalIdentity] = field(default_factory=list)

    def __post_init__(self):
        self.m99_id = _required(self.m99_id, "m99_id")
        self.product_id = _required(self.product_id, "product_id")
        self.variant_key = _required(self.variant_key, "variant_key")


@dataclass
class SupplierOffer:
    m99_id: str
    supplier_id: str
    variant_id: str
    supplier_sku: str
    purchase_price_ex_vat: Decimal
    currency: str = "EUR"
    available: bool = False

    def __post_init__(self):
        self.m99_id = _required(self.m99_id, "m99_id")
        self.supplier_id = _required(self.supplier_id, "supplier_id")
        self.variant_id = _required(self.variant_id, "variant_id")
        self.supplier_sku = _required(self.supplier_sku, "supplier_sku")
        self.currency = _required(self.currency, "currency").upper()
        self.purchase_price_ex_vat = _positive_decimal(
            self.purchase_price_ex_vat, "purchase_price_ex_vat"
        )


@dataclass(frozen=True)
class Market:
    code: str
    name: str
    country_code: str
    default_currency: str
    default_language: str

    def __post_init__(self):
        object.__setattr__(self, "code", _required(self.code, "code").lower())
        object.__setattr__(self, "name", _required(self.name, "name"))
        object.__setattr__(self, "country_code", _required(self.country_code, "country_code").upper())
        object.__setattr__(self, "default_currency", _required(self.default_currency, "default_currency").upper())
        object.__setattr__(self, "default_language", _required(self.default_language, "default_language").lower())


@dataclass(frozen=True)
class Channel:
    code: str
    name: str
    market_code: str
    kind: ChannelKind
    base_url: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "code", _required(self.code, "code").lower())
        object.__setattr__(self, "name", _required(self.name, "name"))
        object.__setattr__(self, "market_code", _required(self.market_code, "market_code").lower())


@dataclass(frozen=True)
class ChannelProductGroup:
    channel_code: str
    product_group_id: str
    enabled: bool = True

    def __post_init__(self):
        object.__setattr__(self, "channel_code", _required(self.channel_code, "channel_code").lower())
        object.__setattr__(self, "product_group_id", _required(self.product_group_id, "product_group_id"))


@dataclass
class ChannelPresence:
    channel_code: str
    variant_id: str
    publication_status: PublicationStatus = PublicationStatus.NOT_PUBLISHED
    external_product_id: str | None = None

    def __post_init__(self):
        self.channel_code = _required(self.channel_code, "channel_code").lower()
        self.variant_id = _required(self.variant_id, "variant_id")


@dataclass(frozen=True)
class InventoryMapping:
    variant_id: str
    system: str
    warehouse_id: str
    external_product_id: str

    def __post_init__(self):
        object.__setattr__(self, "variant_id", _required(self.variant_id, "variant_id"))
        object.__setattr__(self, "system", _required(self.system, "system"))
        object.__setattr__(self, "warehouse_id", _required(self.warehouse_id, "warehouse_id"))
        object.__setattr__(self, "external_product_id", _required(self.external_product_id, "external_product_id"))
