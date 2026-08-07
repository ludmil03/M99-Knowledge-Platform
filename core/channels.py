#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Channel Engine v0.2

Responsible for:
- Sales channels
- Product publication
- Inventory synchronization
- Channel-level controls
- Product-level overrides
- Variant-level overrides
- Inventory policies

Important:

Publishing and inventory synchronization are
two completely independent controls.

Publishing OFF
does NOT mean
Inventory Sync OFF.

Inventory Sync OFF
does NOT mean
Stock = 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# CONSTANTS
# ============================================================

VALID_STATUSES = {
    "active",
    "inactive",
    "draft",
}

VALID_PUBLICATION_STATUSES = {
    "not_published",
    "ready",
    "published",
    "hidden",
    "blocked",
}

VALID_SYNC_DIRECTIONS = {
    "DISABLED",
    "M99_TO_CHANNEL",
    "CHANNEL_TO_M99",
    "BIDIRECTIONAL",
}

VALID_INVENTORY_SOURCES = {
    "M99_AVAILABLE",
    "M99_PHYSICAL",
    "SUPPLIER_STOCK",
    "COMBINED",
    "MANUAL",
}

VALID_STOCK_ZERO_ACTIONS = {
    "hide",
    "show",
    "backorder",
    "supplier_order",
}


# ============================================================
# INVENTORY POLICY
# ============================================================

@dataclass
class InventoryPolicy:
    """
    Defines how inventory is presented/synchronized
    to a sales channel.
    """

    sync_enabled: bool = False

    direction: str = "DISABLED"

    source: str = "M99_AVAILABLE"

    publish_when_zero: bool = False

    zero_stock_action: str = "hide"

    allow_supplier_stock: bool = False

    minimum_publish_quantity: int = 0

    def validate(self) -> list[str]:

        errors: list[str] = []

        if self.direction not in VALID_SYNC_DIRECTIONS:

            errors.append(
                f"Invalid inventory sync direction: "
                f"{self.direction}"
            )

        if self.source not in VALID_INVENTORY_SOURCES:

            errors.append(
                f"Invalid inventory source: "
                f"{self.source}"
            )

        if (
            self.zero_stock_action
            not in VALID_STOCK_ZERO_ACTIONS
        ):

            errors.append(
                f"Invalid zero stock action: "
                f"{self.zero_stock_action}"
            )

        if self.minimum_publish_quantity < 0:

            errors.append(
                "minimum_publish_quantity "
                "cannot be negative."
            )

        if (
            not self.sync_enabled
            and self.direction != "DISABLED"
        ):

            errors.append(
                "Inventory sync is disabled "
                "but direction is not DISABLED."
            )

        if (
            self.sync_enabled
            and self.direction == "DISABLED"
        ):

            errors.append(
                "Inventory sync is enabled "
                "but direction is DISABLED."
            )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "sync_enabled": self.sync_enabled,
            "direction": self.direction,
            "source": self.source,
            "publish_when_zero": self.publish_when_zero,
            "zero_stock_action": self.zero_stock_action,
            "allow_supplier_stock": self.allow_supplier_stock,
            "minimum_publish_quantity":
                self.minimum_publish_quantity,
        }


# ============================================================
# CHANNEL
# ============================================================

@dataclass
class SalesChannel:
    """
    Represents one M99 sales/publishing channel.
    """

    channel_id: str

    name: str

    status: str = "active"

    publishing_enabled: bool = False

    publication_status: str = "not_published"

    inventory: InventoryPolicy = field(
        default_factory=InventoryPolicy
    )

    description: Optional[str] = None

    def validate(self) -> list[str]:

        errors: list[str] = []

        if not self.channel_id:

            errors.append(
                "Channel ID is missing."
            )

        if not self.name:

            errors.append(
                "Channel name is missing."
            )

        if self.status not in VALID_STATUSES:

            errors.append(
                f"Invalid channel status: "
                f"{self.status}"
            )

        if (
            self.publication_status
            not in VALID_PUBLICATION_STATUSES
        ):

            errors.append(
                "Invalid publication status: "
                f"{self.publication_status}"
            )

        errors.extend(
            self.inventory.validate()
        )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "status": self.status,
            "publishing_enabled":
                self.publishing_enabled,
            "publication_status":
                self.publication_status,
            "inventory":
                self.inventory.to_dict(),
            "description":
                self.description,
        }


# ============================================================
# PRODUCT CHANNEL OVERRIDE
# ============================================================

@dataclass
class ProductChannelOverride:
    """
    Product-specific channel settings.

    None means:
        inherit channel setting.

    True / False means:
        explicitly override channel setting.
    """

    channel_id: str

    publishing_enabled: Optional[bool] = None

    inventory_sync_enabled: Optional[bool] = None

    publication_status: Optional[str] = None

    def validate(self) -> list[str]:

        errors: list[str] = []

        if not self.channel_id:

            errors.append(
                "Channel ID is missing."
            )

        if (
            self.publication_status is not None
            and self.publication_status
            not in VALID_PUBLICATION_STATUSES
        ):

            errors.append(
                "Invalid publication status: "
                f"{self.publication_status}"
            )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "channel_id": self.channel_id,
            "publishing_enabled":
                self.publishing_enabled,
            "inventory_sync_enabled":
                self.inventory_sync_enabled,
            "publication_status":
                self.publication_status,
        }


# ============================================================
# VARIANT CHANNEL OVERRIDE
# ============================================================

@dataclass
class VariantChannelOverride:
    """
    Variant-specific channel settings.

    This allows one size/color variant to behave
    differently from the Product Master.
    """

    variant_id: str

    channel_id: str

    publishing_enabled: Optional[bool] = None

    inventory_sync_enabled: Optional[bool] = None

    def validate(self) -> list[str]:

        errors: list[str] = []

        if not self.variant_id:

            errors.append(
                "Variant ID is missing."
            )

        if not self.channel_id:

            errors.append(
                "Channel ID is missing."
            )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "variant_id": self.variant_id,
            "channel_id": self.channel_id,
            "publishing_enabled":
                self.publishing_enabled,
            "inventory_sync_enabled":
                self.inventory_sync_enabled,
        }


# ============================================================
# GLOBAL ENGINE CONTROL
# ============================================================

@dataclass
class InventoryEngineControl:
    """
    Master switch for inventory synchronization.

    If enabled=False:
        no channel may receive automatic
        inventory updates from M99 Engine.
    """

    enabled: bool = False

    def validate(self) -> list[str]:

        return []

    def to_dict(self) -> dict[str, Any]:

        return {
            "enabled": self.enabled
        }


# ============================================================
# CHANNEL ENGINE
# ============================================================

class ChannelEngine:
    """
    Central channel management engine.

    Determines:

        Is product published?

        Is inventory synchronized?

        What is the effective setting?

    Priority:

        Variant Override
              ↓
        Product Override
              ↓
        Channel Setting
              ↓
        Global Engine Control
    """

    def __init__(
        self,
        channels: Optional[
            list[SalesChannel]
        ] = None,
        global_inventory: Optional[
            InventoryEngineControl
        ] = None,
    ) -> None:

        self.channels = channels or []

        self.global_inventory = (
            global_inventory
            or InventoryEngineControl()
        )

        self.product_overrides: list[
            ProductChannelOverride
        ] = []

        self.variant_overrides: list[
            VariantChannelOverride
        ] = []

    # ========================================================
    # CHANNEL MANAGEMENT
    # ========================================================

    def add_channel(
        self,
        channel: SalesChannel
    ) -> None:

        if self.get_channel(
            channel.channel_id
        ):

            raise ValueError(
                "Duplicate channel ID: "
                f"{channel.channel_id}"
            )

        self.channels.append(
            channel
        )

    def get_channel(
        self,
        channel_id: str
    ) -> Optional[SalesChannel]:

        for channel in self.channels:

            if channel.channel_id == channel_id:

                return channel

        return None

    # ========================================================
    # PRODUCT OVERRIDES
    # ========================================================

    def add_product_override(
        self,
        override: ProductChannelOverride
    ) -> None:

        self.product_overrides.append(
            override
        )

    def get_product_override(
        self,
        channel_id: str
    ) -> Optional[ProductChannelOverride]:

        for override in self.product_overrides:

            if override.channel_id == channel_id:

                return override

        return None

    # ========================================================
    # VARIANT OVERRIDES
    # ========================================================

    def add_variant_override(
        self,
        override: VariantChannelOverride
    ) -> None:

        self.variant_overrides.append(
            override
        )

    def get_variant_override(
        self,
        variant_id: str,
        channel_id: str
    ) -> Optional[VariantChannelOverride]:

        for override in self.variant_overrides:

            if (
                override.variant_id == variant_id
                and
                override.channel_id == channel_id
            ):

                return override

        return None

    # ========================================================
    # EFFECTIVE PUBLISHING
    # ========================================================

    def is_publishing_enabled(
        self,
        channel_id: str,
        variant_id: Optional[str] = None
    ) -> bool:

        channel = self.get_channel(
            channel_id
        )

        if not channel:

            return False

        result = channel.publishing_enabled

        product_override = (
            self.get_product_override(
                channel_id
            )
        )

        if (
            product_override
            and
            product_override.publishing_enabled
            is not None
        ):

            result = (
                product_override.publishing_enabled
            )

        if variant_id:

            variant_override = (
                self.get_variant_override(
                    variant_id,
                    channel_id
                )
            )

            if (
                variant_override
                and
                variant_override.publishing_enabled
                is not None
            ):

                result = (
                    variant_override.publishing_enabled
                )

        return result

    # ========================================================
    # EFFECTIVE INVENTORY SYNC
    # ========================================================

    def is_inventory_sync_enabled(
        self,
        channel_id: str,
        variant_id: Optional[str] = None
    ) -> bool:

        # ----------------------------------------------------
        # GLOBAL MASTER SWITCH
        # ----------------------------------------------------

        if not self.global_inventory.enabled:

            return False

        channel = self.get_channel(
            channel_id
        )

        if not channel:

            return False

        result = (
            channel.inventory.sync_enabled
        )

        # ----------------------------------------------------
        # PRODUCT OVERRIDE
        # ----------------------------------------------------

        product_override = (
            self.get_product_override(
                channel_id
            )
        )

        if (
            product_override
            and
            product_override.inventory_sync_enabled
            is not None
        ):

            result = (
                product_override.inventory_sync_enabled
            )

        # ----------------------------------------------------
        # VARIANT OVERRIDE
        # ----------------------------------------------------

        if variant_id:

            variant_override = (
                self.get_variant_override(
                    variant_id,
                    channel_id
                )
            )

            if (
                variant_override
                and
                variant_override.inventory_sync_enabled
                is not None
            ):

                result = (
                    variant_override.inventory_sync_enabled
                )

        # ----------------------------------------------------
        # FINAL SAFETY CHECK
        # ----------------------------------------------------

        if (
            result
            and
            channel.inventory.direction
            == "DISABLED"
        ):

            return False

        return result

    # ========================================================
    # INVENTORY DIRECTION
    # ========================================================

    def get_inventory_direction(
        self,
        channel_id: str
    ) -> str:

        channel = self.get_channel(
            channel_id
        )

        if not channel:

            return "DISABLED"

        if not self.global_inventory.enabled:

            return "DISABLED"

        if not channel.inventory.sync_enabled:

            return "DISABLED"

        return channel.inventory.direction

    # ========================================================
    # INVENTORY SOURCE
    # ========================================================

    def get_inventory_source(
        self,
        channel_id: str
    ) -> Optional[str]:

        channel = self.get_channel(
            channel_id
        )

        if not channel:

            return None

        return channel.inventory.source

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> list[str]:

        errors: list[str] = []

        channel_ids: set[str] = set()

        for channel in self.channels:

            errors.extend(
                channel.validate()
            )

            if channel.channel_id in channel_ids:

                errors.append(
                    "Duplicate channel ID: "
                    f"{channel.channel_id}"
                )

            channel_ids.add(
                channel.channel_id
            )

        for override in self.product_overrides:

            errors.extend(
                override.validate()
            )

            if (
                override.channel_id
                not in channel_ids
            ):

                errors.append(
                    "Product override references "
                    "unknown channel: "
                    f"{override.channel_id}"
                )

        for override in self.variant_overrides:

            errors.extend(
                override.validate()
            )

            if (
                override.channel_id
                not in channel_ids
            ):

                errors.append(
                    "Variant override references "
                    "unknown channel: "
                    f"{override.channel_id}"
                )

        return errors


# ============================================================
# DEFAULT M99 CHANNELS
# ============================================================

def create_default_channels() -> ChannelEngine:
    """
    Create the initial M99 channel configuration.

    All publishing and inventory synchronization
    are intentionally disabled by default.
    """

    engine = ChannelEngine(
        global_inventory=InventoryEngineControl(
            enabled=False
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="mela99",
            name="Mela99",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="m99-eu",
            name="M99.eu",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="rabotni-drehi",
            name="Rabotni-Drehi",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="laviro",
            name="Laviro",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="b2b",
            name="B2B",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    engine.add_channel(
        SalesChannel(
            channel_id="direct",
            name="Direct Sales",
            publishing_enabled=False,
            publication_status="not_published",
            inventory=InventoryPolicy(
                sync_enabled=False,
                direction="DISABLED",
                source="M99_AVAILABLE",
            ),
        )
    )

    return engine


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )
    print(
        "M99 Knowledge Platform"
    )
    print(
        "Channel Engine v0.2"
    )
    print(
        "========================================"
    )
    print()

    engine = create_default_channels()

    errors = engine.validate()

    if errors:

        print("VALIDATION ERRORS:")

        for error in errors:

            print(
                f"ERROR: {error}"
            )

    else:

        print(
            "Channel configuration: VALID"
        )

    print()

    # --------------------------------------------------------
    # Enable global inventory synchronization
    # --------------------------------------------------------

    engine.global_inventory.enabled = True

    # --------------------------------------------------------
    # Enable Mela99 publishing
    # --------------------------------------------------------

    mela99 = engine.get_channel(
        "mela99"
    )

    if mela99:

        mela99.publishing_enabled = True

        mela99.publication_status = (
            "ready"
        )

        mela99.inventory.sync_enabled = True

        mela99.inventory.direction = (
            "M99_TO_CHANNEL"
        )

    print(
        "Mela99 publishing:"
    )

    print(
        engine.is_publishing_enabled(
            "mela99"
        )
    )

    print()

    print(
        "Mela99 inventory sync:"
    )

    print(
        engine.is_inventory_sync_enabled(
            "mela99"
        )
    )

    print()

    print(
        "M99.eu inventory sync:"
    )

    print(
        engine.is_inventory_sync_enabled(
            "m99-eu"
        )
    )

    print()

    # --------------------------------------------------------
    # Product override
    # --------------------------------------------------------

    engine.add_product_override(
        ProductChannelOverride(
            channel_id="mela99",
            inventory_sync_enabled=False,
        )
    )

    print(
        "Mela99 inventory sync "
        "after product override:"
    )

    print(
        engine.is_inventory_sync_enabled(
            "mela99"
        )
    )

    print()

    # --------------------------------------------------------
    # Variant override
    # --------------------------------------------------------

    engine.add_variant_override(
        VariantChannelOverride(
            variant_id="M99-PV-000001",
            channel_id="mela99",
            inventory_sync_enabled=True,
        )
    )

    print(
        "Variant inventory sync "
        "after variant override:"
    )

    print(
        engine.is_inventory_sync_enabled(
            "mela99",
            "M99-PV-000001"
        )
    )

    print()

    print(
        "========================================"
    )
    print(
        "Channel Engine test completed."
    )
    print(
        "========================================"
    )
