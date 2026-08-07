#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Variant Engine v0.2

Responsible for:
- Product Variants
- Size
- Color
- Variant attributes
- Allowed variant combinations
- Variant validation
- Serial numbers
- Batch / Lot numbers

Important:
Size and color are PRODUCT ATTRIBUTES.
Serial and batch numbers are INVENTORY IDENTIFIERS.

M99 Product Master:
    M99-PM-000001

M99 Product Variant:
    M99-PV-000001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# CONSTANTS
# ============================================================

VALID_VARIANT_STATUSES = {
    "draft",
    "active",
    "discontinued",
    "archived",
}

VALID_MAPPING_STATUSES = {
    "auto_match",
    "high_confidence",
    "manual_review",
    "validated",
    "rejected",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(value: Any) -> Optional[str]:
    """
    Normalize an attribute value.

    Example:

        "  Black  " -> "Black"
        "40"        -> "40"
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def normalize_attributes(
    attributes: Optional[dict[str, Any]]
) -> dict[str, str]:
    """
    Normalize variant attributes.

    Empty attributes are removed.
    """

    if not attributes:
        return {}

    result: dict[str, str] = {}

    for key, value in attributes.items():

        normalized_key = str(key).strip().lower()

        normalized_value = normalize_value(value)

        if normalized_key and normalized_value:

            result[normalized_key] = normalized_value

    return result


# ============================================================
# VARIANT
# ============================================================

@dataclass
class ProductVariant:
    """
    Represents one sellable variant of a Product Master.
    """

    variant_id: str

    sku: str

    product_id: str

    attributes: dict[str, str] = field(
        default_factory=dict
    )

    ean: Optional[str] = None

    status: str = "active"

    mapping_status: str = "manual_review"

    confidence: Optional[float] = None

    def __post_init__(self) -> None:

        self.attributes = normalize_attributes(
            self.attributes
        )

        if self.ean:

            self.ean = str(
                self.ean
            ).strip()

    # --------------------------------------------------------
    # ATTRIBUTE HELPERS
    # --------------------------------------------------------

    @property
    def size(self) -> Optional[str]:

        return self.attributes.get(
            "size"
        )

    @property
    def color(self) -> Optional[str]:

        return self.attributes.get(
            "color"
        )

    def get_attribute(
        self,
        name: str
    ) -> Optional[str]:

        if not name:
            return None

        return self.attributes.get(
            name.strip().lower()
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    def validate(self) -> list[str]:

        errors: list[str] = []

        if not self.variant_id:

            errors.append(
                "Variant ID is missing."
            )

        if not self.sku:

            errors.append(
                "Variant SKU is missing."
            )

        if not self.product_id:

            errors.append(
                "Parent Product ID is missing."
            )

        if self.status not in VALID_VARIANT_STATUSES:

            errors.append(
                f"Invalid variant status: "
                f"{self.status}"
            )

        if (
            self.mapping_status
            not in VALID_MAPPING_STATUSES
        ):

            errors.append(
                "Invalid mapping status: "
                f"{self.mapping_status}"
            )

        if self.confidence is not None:

            if not (
                0 <= self.confidence <= 100
            ):

                errors.append(
                    "Confidence must be "
                    "between 0 and 100."
                )

        return errors

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "variant_id": self.variant_id,
            "sku": self.sku,
            "product_id": self.product_id,
            "attributes": self.attributes,
            "ean": self.ean,
            "status": self.status,
            "mapping_status": self.mapping_status,
            "confidence": self.confidence,
        }


# ============================================================
# ALLOWED VARIANT COMBINATION
# ============================================================

@dataclass(frozen=True)
class AllowedVariant:
    """
    Represents one valid combination of attributes.

    Example:

        size = 40
        color = Black
    """

    attributes: tuple[
        tuple[str, str], ...
    ]

    @classmethod
    def from_dict(
        cls,
        attributes: dict[str, Any]
    ) -> "AllowedVariant":

        normalized = normalize_attributes(
            attributes
        )

        return cls(
            attributes=tuple(
                sorted(
                    normalized.items()
                )
            )
        )

    def matches(
        self,
        attributes: dict[str, Any]
    ) -> bool:

        normalized = normalize_attributes(
            attributes
        )

        return self.attributes == tuple(
            sorted(
                normalized.items()
            )
        )

    def to_dict(self) -> dict[str, str]:

        return dict(
            self.attributes
        )


# ============================================================
# VARIANT RULES
# ============================================================

@dataclass
class VariantRules:
    """
    Defines which combinations of attributes
    are actually possible for a Product Master.

    Example:

        Black / 40
        Black / 41
        Black / 42
        Black / 43

    If Black / 47 is not listed,
    it is NOT a valid variant.
    """

    product_id: str

    allowed_variants: list[
        AllowedVariant
    ] = field(
        default_factory=list
    )

    strict: bool = True

    def add_allowed_variant(
        self,
        attributes: dict[str, Any]
    ) -> None:

        variant = AllowedVariant.from_dict(
            attributes
        )

        if variant not in self.allowed_variants:

            self.allowed_variants.append(
                variant
            )

    def is_allowed(
        self,
        attributes: dict[str, Any]
    ) -> bool:

        if not self.strict:

            return True

        normalized = normalize_attributes(
            attributes
        )

        for allowed in self.allowed_variants:

            if allowed.matches(
                normalized
            ):

                return True

        return False

    def validate_variant(
        self,
        variant: ProductVariant
    ) -> list[str]:

        errors: list[str] = []

        if variant.product_id != self.product_id:

            errors.append(
                "Variant belongs to another "
                "Product Master."
            )

            return errors

        if not self.is_allowed(
            variant.attributes
        ):

            errors.append(
                "Variant attributes are not "
                "allowed for this Product Master: "
                f"{variant.attributes}"
            )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "product_id": self.product_id,
            "strict": self.strict,
            "allowed_variants": [
                variant.to_dict()
                for variant in self.allowed_variants
            ],
        }


# ============================================================
# INVENTORY IDENTIFIERS
# ============================================================

@dataclass
class InventoryIdentifier:
    """
    Inventory-level identification.

    This is NOT the Product Variant identity.

    Examples:

        Serial Number
        Batch / Lot Number
    """

    identifier_type: str

    value: str

    variant_id: str

    status: str = "active"

    def validate(self) -> list[str]:

        errors: list[str] = []

        allowed_types = {
            "serial",
            "batch",
            "lot",
        }

        if self.identifier_type not in allowed_types:

            errors.append(
                "Invalid inventory identifier "
                f"type: {self.identifier_type}"
            )

        if not self.value:

            errors.append(
                "Inventory identifier value "
                "is missing."
            )

        if not self.variant_id:

            errors.append(
                "Variant ID is missing."
            )

        return errors

    def to_dict(self) -> dict[str, str]:

        return {
            "type": self.identifier_type,
            "value": self.value,
            "variant_id": self.variant_id,
            "status": self.status,
        }


# ============================================================
# VARIANT COLLECTION
# ============================================================

class VariantCollection:
    """
    Collection of Product Variants for one Product Master.

    Provides:
    - duplicate detection
    - SKU lookup
    - EAN lookup
    - size lookup
    - color lookup
    - validation
    """

    def __init__(
        self,
        product_id: str,
        variants: Optional[
            list[ProductVariant]
        ] = None,
    ) -> None:

        self.product_id = product_id

        self.variants = variants or []

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    def add(
        self,
        variant: ProductVariant
    ) -> None:

        if variant.product_id != self.product_id:

            raise ValueError(
                "Variant belongs to another "
                "Product Master."
            )

        self.variants.append(
            variant
        )

    # --------------------------------------------------------
    # LOOKUPS
    # --------------------------------------------------------

    def find_by_variant_id(
        self,
        variant_id: str
    ) -> Optional[ProductVariant]:

        for variant in self.variants:

            if variant.variant_id == variant_id:

                return variant

        return None

    def find_by_sku(
        self,
        sku: str
    ) -> Optional[ProductVariant]:

        for variant in self.variants:

            if variant.sku == sku:

                return variant

        return None

    def find_by_ean(
        self,
        ean: str
    ) -> Optional[ProductVariant]:

        if not ean:
            return None

        for variant in self.variants:

            if variant.ean == ean:

                return variant

        return None

    def find_by_attributes(
        self,
        attributes: dict[str, Any]
    ) -> list[ProductVariant]:

        normalized = normalize_attributes(
            attributes
        )

        result = []

        for variant in self.variants:

            if variant.attributes == normalized:

                result.append(
                    variant
                )

        return result

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    def validate(self) -> list[str]:

        errors: list[str] = []

        variant_ids: set[str] = set()
        skus: set[str] = set()
        eans: set[str] = set()

        for variant in self.variants:

            errors.extend(
                variant.validate()
            )

            if variant.variant_id in variant_ids:

                errors.append(
                    "Duplicate Variant ID: "
                    f"{variant.variant_id}"
                )

            variant_ids.add(
                variant.variant_id
            )

            if variant.sku in skus:

                errors.append(
                    "Duplicate Variant SKU: "
                    f"{variant.sku}"
                )

            skus.add(
                variant.sku
            )

            if variant.ean:

                if variant.ean in eans:

                    errors.append(
                        "Duplicate EAN: "
                        f"{variant.ean}"
                    )

                eans.add(
                    variant.ean
                )

        return errors


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_variant(
    product_id: str,
    variant_id: str,
    sku: str,
    attributes: dict[str, Any],
    ean: Optional[str] = None,
) -> ProductVariant:
    """
    Convenience function for creating a ProductVariant.
    """

    return ProductVariant(
        variant_id=variant_id,
        sku=sku,
        product_id=product_id,
        attributes=attributes,
        ean=ean,
    )


def create_variant_rules(
    product_id: str,
    allowed_variants: list[
        dict[str, Any]
    ],
    strict: bool = True,
) -> VariantRules:
    """
    Convenience function for creating VariantRules.
    """

    rules = VariantRules(
        product_id=product_id,
        strict=strict,
    )

    for attributes in allowed_variants:

        rules.add_allowed_variant(
            attributes
        )

    return rules


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )
    print(
        "M99 Knowledge Platform"
    )
    print(
        "Variant Engine v0.2"
    )
    print(
        "========================================"
    )
    print()

    product_id = "M99-PM-000001"

    rules = create_variant_rules(
        product_id=product_id,
        allowed_variants=[
            {
                "size": "40",
                "color": "Black",
            },
            {
                "size": "41",
                "color": "Black",
            },
            {
                "size": "42",
                "color": "Black",
            },
            {
                "size": "43",
                "color": "Black",
            },
            {
                "size": "44",
                "color": "Black",
            },
        ],
    )

    variant = create_variant(
        product_id=product_id,
        variant_id="M99-PV-000001",
        sku="M99-000001-40",
        attributes={
            "size": "40",
            "color": "Black",
        },
    )

    print(
        "Variant:"
    )

    print(
        variant.to_dict()
    )

    print()

    print(
        "Validation:"
    )

    errors = variant.validate()

    if errors:

        for error in errors:

            print(
                f"ERROR: {error}"
            )

    else:

        print(
            "Variant structure: VALID"
        )

    print()

    print(
        "Variant Rules:"
    )

    print(
        rules.to_dict()
    )

    print()

    print(
        "Allowed:"
    )

    print(
        rules.is_allowed(
            {
                "size": "40",
                "color": "Black",
            }
        )
    )

    print()

    print(
        "Not allowed:"
    )

    print(
        rules.is_allowed(
            {
                "size": "47",
                "color": "Black",
            }
        )
    )

    print()

    print(
        "========================================"
    )
    print(
        "Variant Engine test completed."
    )
    print(
        "========================================"
    )
