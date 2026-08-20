"""Canonical catalog model for M99 Knowledge Platform v0.7.2."""

from .enums import (
    KnowledgeStatus,
    ProductLifecycle,
    PublicationStatus,
    ChannelKind,
)
from .models import (
    ProductGroup,
    Product,
    ProductVariant,
    SupplierOffer,
    Market,
    Channel,
    ChannelProductGroup,
    ChannelPresence,
    InventoryMapping,
    ExternalIdentity,
)
from .transitions import (
    transition_product_lifecycle,
    require_hard_delete_confirmation,
)

__all__ = [
    "KnowledgeStatus",
    "ProductLifecycle",
    "PublicationStatus",
    "ChannelKind",
    "ProductGroup",
    "Product",
    "ProductVariant",
    "SupplierOffer",
    "Market",
    "Channel",
    "ChannelProductGroup",
    "ChannelPresence",
    "InventoryMapping",
    "ExternalIdentity",
    "transition_product_lifecycle",
    "require_hard_delete_confirmation",
]
