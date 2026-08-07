#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Product Matcher v0.2

Matches incomplete external/legacy product data
against the M99 Product Master and Product Variant.

Important:

MoneyWorks may contain only:

    code
    name
    size
    color

or:

    code
    name
    size

or:

    code
    name
    color

or even only:

    code
    name

Missing information is NOT automatically an error.

The matcher must distinguish between:

    CONFIRMED
    HIGH_CONFIDENCE
    REVIEW
    REJECTED

The matcher NEVER creates a new M99 product automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re


# ============================================================
# CONSTANTS
# ============================================================

MATCH_CONFIRMED = "CONFIRMED"
MATCH_HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
MATCH_REVIEW = "REVIEW"
MATCH_REJECTED = "REJECTED"

VALID_MATCH_STATUSES = {
    MATCH_CONFIRMED,
    MATCH_HIGH_CONFIDENCE,
    MATCH_REVIEW,
    MATCH_REJECTED,
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    value: Any
) -> str:
    """
    Normalize free text for comparison.

    Examples:

        PUMA VELOCITY 2.0 BLACK LOW

        puma velocity 2.0 black low

    become comparable.
    """

    if value is None:
        return ""

    value = str(value).strip().casefold()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


def normalize_identifier(
    value: Any
) -> str:
    """
    Normalize SKU / code / EAN-like identifiers.
    """

    if value is None:
        return ""

    value = str(value).strip().upper()

    value = re.sub(
        r"\s+",
        "",
        value
    )

    return value


# ============================================================
# EXTERNAL PRODUCT
# ============================================================

@dataclass
class ExternalProduct:
    """
    Product information coming from an external system.

    All fields except code and name are optional.

    This is intentional because MoneyWorks data
    may be incomplete.
    """

    source: str

    code: str

    name: str

    size: Optional[str] = None

    color: Optional[str] = None

    ean: Optional[str] = None

    brand: Optional[str] = None

    manufacturer_sku: Optional[str] = None

    supplier_sku: Optional[str] = None

    attributes: dict[str, Any] = field(
        default_factory=dict
    )

    def normalized_code(self) -> str:

        return normalize_identifier(
            self.code
        )

    def normalized_name(self) -> str:

        return normalize_text(
            self.name
        )

    def normalized_size(self) -> str:

        return normalize_text(
            self.size
        )

    def normalized_color(self) -> str:

        return normalize_text(
            self.color
        )

    def normalized_ean(self) -> str:

        return normalize_identifier(
            self.ean
        )


# ============================================================
# M99 VARIANT
# ============================================================

@dataclass
class M99Variant:
    """
    Minimal M99 Variant representation required
    by the matcher.
    """

    variant_id: str

    product_id: str

    name: str

    size: Optional[str] = None

    color: Optional[str] = None

    ean: Optional[str] = None

    manufacturer_sku: Optional[str] = None

    supplier_sku: Optional[str] = None

    attributes: dict[str, Any] = field(
        default_factory=dict
    )

    def normalized_name(self) -> str:

        return normalize_text(
            self.name
        )

    def normalized_size(self) -> str:

        return normalize_text(
            self.size
        )

    def normalized_color(self) -> str:

        return normalize_text(
            self.color
        )

    def normalized_ean(self) -> str:

        return normalize_identifier(
            self.ean
        )


# ============================================================
# M99 PRODUCT MASTER
# ============================================================

@dataclass
class M99Product:
    """
    Minimal Product Master representation.
    """

    product_id: str

    name: str

    brand: Optional[str] = None

    model: Optional[str] = None

    manufacturer_sku: Optional[str] = None

    supplier_sku: Optional[str] = None

    variants: list[M99Variant] = field(
        default_factory=list
    )


# ============================================================
# MATCH RESULT
# ============================================================

@dataclass
class MatchResult:

    status: str

    score: float

    product_id: Optional[str] = None

    variant_id: Optional[str] = None

    matched_fields: list[str] = field(
        default_factory=list
    )

    missing_fields: list[str] = field(
        default_factory=list
    )

    conflicts: list[str] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:

        return {
            "status": self.status,
            "score": self.score,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "matched_fields":
                self.matched_fields,
            "missing_fields":
                self.missing_fields,
            "conflicts":
                self.conflicts,
            "reasons":
                self.reasons,
        }


# ============================================================
# PRODUCT MATCHER
# ============================================================

class ProductMatcher:
    """
    Matches external/legacy data against M99.

    Scoring philosophy:

        Exact EAN
            very strong

        Manufacturer SKU
            very strong

        Supplier SKU
            strong

        Exact size
            strong

        Exact color
            strong

        Product name
            supporting evidence

    Missing data:
        neutral

    Conflicting data:
        negative

    The matcher does NOT require all fields.
    """

    # --------------------------------------------------------
    # SCORE WEIGHTS
    # --------------------------------------------------------

    WEIGHT_EAN = 100

    WEIGHT_MANUFACTURER_SKU = 90

    WEIGHT_SUPPLIER_SKU = 80

    WEIGHT_BRAND = 25

    WEIGHT_NAME = 30

    WEIGHT_SIZE = 25

    WEIGHT_COLOR = 25

    PENALTY_CONFLICT = 40

    # ========================================================
    # NORMALIZED NAME TOKENS
    # ========================================================

    @staticmethod
    def name_tokens(
        value: str
    ) -> set[str]:

        value = normalize_text(
            value
        )

        if not value:

            return set()

        return set(
            re.findall(
                r"[a-z0-9а-яё]+",
                value
            )
        )

    # ========================================================
    # NAME SIMILARITY
    # ========================================================

    @classmethod
    def name_similarity(
        cls,
        first: str,
        second: str
    ) -> float:

        first_tokens = cls.name_tokens(
            first
        )

        second_tokens = cls.name_tokens(
            second
        )

        if not first_tokens:
            return 0.0

        if not second_tokens:
            return 0.0

        intersection = (
            first_tokens
            &
            second_tokens
        )

        union = (
            first_tokens
            |
            second_tokens
        )

        if not union:
            return 0.0

        return (
            len(intersection)
            /
            len(union)
        )

    # ========================================================
    # SINGLE VARIANT MATCH
    # ========================================================

    def compare_variant(
        self,
        external: ExternalProduct,
        product: M99Product,
        variant: M99Variant,
    ) -> MatchResult:

        score = 0.0

        matched_fields: list[str] = []

        missing_fields: list[str] = []

        conflicts: list[str] = []

        reasons: list[str] = []

        # ----------------------------------------------------
        # EAN
        # ----------------------------------------------------

        if external.ean:

            if variant.ean:

                if (
                    external.normalized_ean()
                    ==
                    variant.normalized_ean()
                ):

                    score += self.WEIGHT_EAN

                    matched_fields.append(
                        "ean"
                    )

                else:

                    conflicts.append(
                        "ean"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

            else:

                missing_fields.append(
                    "variant.ean"
                )

        else:

            missing_fields.append(
                "external.ean"
            )

        # ----------------------------------------------------
        # MANUFACTURER SKU
        # ----------------------------------------------------

        if external.manufacturer_sku:

            if variant.manufacturer_sku:

                if (
                    normalize_identifier(
                        external.manufacturer_sku
                    )
                    ==
                    normalize_identifier(
                        variant.manufacturer_sku
                    )
                ):

                    score += (
                        self.WEIGHT_MANUFACTURER_SKU
                    )

                    matched_fields.append(
                        "manufacturer_sku"
                    )

                else:

                    conflicts.append(
                        "manufacturer_sku"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

            else:

                missing_fields.append(
                    "variant.manufacturer_sku"
                )

        # ----------------------------------------------------
        # SUPPLIER SKU
        # ----------------------------------------------------

        if external.supplier_sku:

            if variant.supplier_sku:

                if (
                    normalize_identifier(
                        external.supplier_sku
                    )
                    ==
                    normalize_identifier(
                        variant.supplier_sku
                    )
                ):

                    score += (
                        self.WEIGHT_SUPPLIER_SKU
                    )

                    matched_fields.append(
                        "supplier_sku"
                    )

                else:

                    conflicts.append(
                        "supplier_sku"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

            else:

                missing_fields.append(
                    "variant.supplier_sku"
                )

        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        if external.size:

            if variant.size:

                if (
                    external.normalized_size()
                    ==
                    variant.normalized_size()
                ):

                    score += (
                        self.WEIGHT_SIZE
                    )

                    matched_fields.append(
                        "size"
                    )

                else:

                    conflicts.append(
                        "size"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

            else:

                missing_fields.append(
                    "variant.size"
                )

        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------

        if external.color:

            if variant.color:

                if (
                    external.normalized_color()
                    ==
                    variant.normalized_color()
                ):

                    score += (
                        self.WEIGHT_COLOR
                    )

                    matched_fields.append(
                        "color"
                    )

                else:

                    conflicts.append(
                        "color"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

            else:

                missing_fields.append(
                    "variant.color"
                )

        # ----------------------------------------------------
        # PRODUCT NAME
        # ----------------------------------------------------

        if external.name:

            similarity = (
                self.name_similarity(
                    external.name,
                    variant.name
                )
            )

            if similarity >= 0.80:

                score += self.WEIGHT_NAME

                matched_fields.append(
                    "name"
                )

                reasons.append(
                    "Very high product-name similarity."
                )

            elif similarity >= 0.50:

                score += (
                    self.WEIGHT_NAME
                    * 0.60
                )

                matched_fields.append(
                    "name_partial"
                )

                reasons.append(
                    "Partial product-name similarity."
                )

            elif similarity >= 0.30:

                score += (
                    self.WEIGHT_NAME
                    * 0.25
                )

                reasons.append(
                    "Weak product-name similarity."
                )

            else:

                conflicts.append(
                    "name"
                )

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        if external.brand:

            if product.brand:

                if (
                    normalize_text(
                        external.brand
                    )
                    ==
                    normalize_text(
                        product.brand
                    )
                ):

                    score += (
                        self.WEIGHT_BRAND
                    )

                    matched_fields.append(
                        "brand"
                    )

                else:

                    conflicts.append(
                        "brand"
                    )

                    score -= (
                        self.PENALTY_CONFLICT
                    )

        # ====================================================
        # RESULT CLASSIFICATION
        # ====================================================

        if conflicts:

            status = MATCH_REVIEW

            reasons.append(
                "Conflicting information detected."
            )

        elif score >= 100:

            status = MATCH_CONFIRMED

            reasons.append(
                "Strong identity evidence."
            )

        elif score >= 60:

            status = MATCH_HIGH_CONFIDENCE

            reasons.append(
                "High-confidence partial match."
            )

        elif score >= 30:

            status = MATCH_REVIEW

            reasons.append(
                "Insufficient information for automatic confirmation."
            )

        else:

            status = MATCH_REJECTED

            reasons.append(
                "Insufficient matching evidence."
            )

        return MatchResult(
            status=status,
            score=max(
                0.0,
                min(
                    100.0,
                    score
                )
            ),
            product_id=product.product_id,
            variant_id=variant.variant_id,
            matched_fields=matched_fields,
            missing_fields=missing_fields,
            conflicts=conflicts,
            reasons=reasons,
        )

    # ========================================================
    # MATCH PRODUCT
    # ========================================================

    def match_product(
        self,
        external: ExternalProduct,
        product: M99Product,
    ) -> list[MatchResult]:

        results: list[
            MatchResult
        ] = []

        for variant in product.variants:

            result = self.compare_variant(
                external,
                product,
                variant
            )

            results.append(
                result
            )

        results.sort(
            key=lambda result:
                result.score,
            reverse=True
        )

        return results

    # ========================================================
    # MATCH MANY PRODUCTS
    # ========================================================

    def match(
        self,
        external: ExternalProduct,
        products: list[M99Product],
    ) -> list[MatchResult]:

        results: list[
            MatchResult
        ] = []

        for product in products:

            results.extend(
                self.match_product(
                    external,
                    product
                )
            )

        results.sort(
            key=lambda result:
                result.score,
            reverse=True
        )

        return results

    # ========================================================
    # BEST MATCH
    # ========================================================

    def best_match(
        self,
        external: ExternalProduct,
        products: list[M99Product],
    ) -> MatchResult:

        results = self.match(
            external,
            products
        )

        if not results:

            return MatchResult(
                status=MATCH_REJECTED,
                score=0.0,
                reasons=[
                    "No M99 variants available."
                ],
            )

        best = results[0]

        # ----------------------------------------------------
        # SAFETY RULE
        # ----------------------------------------------------
        #
        # Never automatically confirm a result when
        # there is a conflict.
        #

        if best.conflicts:

            best.status = MATCH_REVIEW

        return best


# ============================================================
# MONEYWORKS HELPER
# ============================================================

def moneyworks_product(
    code: str,
    name: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
) -> ExternalProduct:

    """
    Create an ExternalProduct from the limited
    information normally available in MoneyWorks.
    """

    return ExternalProduct(
        source="moneyworks",
        code=code,
        name=name,
        size=size,
        color=color,
    )


# ============================================================
# DEMO DATA
# ============================================================

def create_demo_products() -> list[M99Product]:

    return [

        M99Product(
            product_id="M99-PM-000001",
            name=(
                "PUMA Velocity 2.0 Black Low"
            ),
            brand="PUMA Safety",
            model="Velocity 2.0 Black Low",
            manufacturer_sku="643870",
            supplier_sku="06100288",

            variants=[

                M99Variant(
                    variant_id="M99-PV-000001",
                    product_id="M99-PM-000001",
                    name=(
                        "PUMA Velocity 2.0 Black Low "
                        "Size 40 Black"
                    ),
                    size="40",
                    color="Black",
                    manufacturer_sku="643870",
                    supplier_sku="06100288",
                ),

                M99Variant(
                    variant_id="M99-PV-000002",
                    product_id="M99-PM-000001",
                    name=(
                        "PUMA Velocity 2.0 Black Low "
                        "Size 41 Black"
                    ),
                    size="41",
                    color="Black",
                    manufacturer_sku="643870",
                    supplier_sku="06100288",
                ),

                M99Variant(
                    variant_id="M99-PV-000003",
                    product_id="M99-PM-000001",
                    name=(
                        "PUMA Velocity 2.0 Black Low "
                        "Size 42 Black"
                    ),
                    size="42",
                    color="Black",
                    manufacturer_sku="643870",
                    supplier_sku="06100288",
                ),
            ],
        )
    ]


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )
    print(
        "M99 Knowledge Platform"
    )
    print(
        "Product Matcher v0.2"
    )
    print(
        "========================================"
    )
    print()

    matcher = ProductMatcher()

    products = create_demo_products()

    # ========================================================
    # CASE 1
    # MoneyWorks has size + color
    # ========================================================

    print(
        "TEST 1"
    )

    external = moneyworks_product(
        code="MW-0001842",
        name=(
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),
        size="40",
        color="Black",
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # CASE 2
    # MoneyWorks has only size
    # ========================================================

    print(
        "TEST 2"
    )

    external = moneyworks_product(
        code="MW-0001843",
        name=(
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),
        size="41",
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # CASE 3
    # MoneyWorks has only color
    # ========================================================

    print(
        "TEST 3"
    )

    external = moneyworks_product(
        code="MW-0001844",
        name=(
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),
        color="Black",
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # CASE 4
    # MoneyWorks has only name
    # ========================================================

    print(
        "TEST 4"
    )

    external = moneyworks_product(
        code="MW-0001845",
        name=(
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # CASE 5
    # Wrong size
    # ========================================================

    print(
        "TEST 5"
    )

    external = moneyworks_product(
        code="MW-0001846",
        name=(
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),
        size="45",
        color="Black",
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # CASE 6
    # Wrong product
    # ========================================================

    print(
        "TEST 6"
    )

    external = moneyworks_product(
        code="MW-0001847",
        name="Safety Shoes Other Brand",
        size="40",
        color="Black",
    )

    result = matcher.best_match(
        external,
        products
    )

    print(
        result.to_dict()
    )

    print()

    print(
        "========================================"
    )
    print(
        "Product Matcher test completed."
    )
    print(
        "========================================"
    )
