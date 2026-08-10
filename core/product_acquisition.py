from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ProductGroupLifecycle(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


@dataclass(frozen=True)
class LegacyIdentifier:
    system: str
    value: str


@dataclass
class ProductVariant:
    variant_id: str
    parent_m99_id: str | None = None
    size: str | None = None
    color: str | None = None
    supplier_codes: dict[str, str] = field(default_factory=dict)
    ean: str | None = None


@dataclass
class SupplierOffer:
    supplier: str
    supplier_product_id: str | None = None
    purchase_price_ex_vat: float | None = None
    recommended_price_ex_vat: float | None = None
    public_price_inc_vat: float | None = None
    stock_qty: float | None = None
    source: str | None = None


@dataclass
class ChannelAssignment:
    channel: str
    enabled: bool = False
    operator_approved: bool = False
    existing_product_id: str | None = None
    legacy_identifier: str | None = None
    protected_url: str | None = None
    seo_change_allowed: bool = False


@dataclass
class ProductGroup:
    m99_id: str
    name: str
    brand: str
    applications: set[str]
    lifecycle: ProductGroupLifecycle = ProductGroupLifecycle.DRAFT
    variants: list[ProductVariant] = field(default_factory=list)
    legacy_identifiers: list[LegacyIdentifier] = field(default_factory=list)
    supplier_offers: list[SupplierOffer] = field(default_factory=list)
    channels: list[ChannelAssignment] = field(default_factory=list)

    def can_delete(self, operator_typed_confirmation: str | None) -> bool:
        return operator_typed_confirmation == "DELETE"

    def transition(self, target: ProductGroupLifecycle) -> None:
        allowed = {
            ProductGroupLifecycle.DRAFT: {ProductGroupLifecycle.ACTIVE},
            ProductGroupLifecycle.ACTIVE: {
                ProductGroupLifecycle.PAUSED,
                ProductGroupLifecycle.RETIRED,
            },
            ProductGroupLifecycle.PAUSED: {
                ProductGroupLifecycle.ACTIVE,
                ProductGroupLifecycle.RETIRED,
            },
            ProductGroupLifecycle.RETIRED: set(),
        }
        if target not in allowed[self.lifecycle]:
            raise ValueError(
                f"Invalid lifecycle transition: {self.lifecycle} -> {target}"
            )
        self.lifecycle = target
