#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Product Matcher v0.3

Architecture:

    External / Legacy Article
                |
                v
          PRODUCT MATCH
                |
                v
          VARIANT MATCH
                |
                v
       Final Match Decision

Designed for incomplete MoneyWorks data.

MoneyWorks may contain:

    code
    name
    size
    color

Any of size/color may be missing.

Important rules:

    Missing information != conflict

    Conflicting information = conflict

    Product identity is evaluated separately
    from variant identity.

    The matcher NEVER creates an M99 Product
    or M99 Variant automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re


# ============================================================
# STATUS CONSTANTS
# ============================================================

CONFIRMED = "CONFIRMED"
HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
REVIEW = "REVIEW"
REJECTED = "REJECTED"

VARIANT_NOT_DETERMINED = "NOT_DETERMINED"
VARIANT_AMBIGUOUS = "AMBIGUOUS"


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:

    if value is None:
        return ""

    value = str(value).strip().casefold()

    value = re.sub(r"\s+", " ", value)

    return value


def normalize_identifier(value: Any) -> str:

    if value is None:
        return ""

    value = str(value).strip().upper()

    value = re.sub(r"\s+", "", value)

    return value


def normalize_size(value: Any) -> str:

    if value is None:
        return ""

    value = normalize_text(value)

    # Examples:
    #
    # "Size: 40" -> "40"
    # "Shoes Size: 40" -> "40"

    value = re.sub(
        r"^(size|shoes size)\s*[:\-]?\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    return value.strip()


def normalize_color(value: Any) -> str:

    if value is None:
        return ""

    return normalize_text(value)


# ============================================================
# NAME TOKENIZATION
# ============================================================

def name_tokens(value: str) -> set[str]:

    value = normalize_text(value)

    if not value:
        return set()

    return set(
        re.findall(
            r"[a-z0-9а-яё]+",
            value,
        )
    )


def name_similarity(
    first: str,
    second: str,
) -> float:

    first_tokens = name_tokens(first)
    second_tokens = name_tokens(second)

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = (
        first_tokens & second_tokens
    )

    union = (
        first_tokens | second_tokens
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


# ============================================================
# EXTERNAL ARTICLE
# ============================================================

@dataclass
class ExternalProduct:

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

    def normalized_name(self):

        return normalize_text(self.name)

    def normalized_size(self):

        return normalize_size(self.size)

    def normalized_color(self):

        return normalize_color(self.color)

    def normalized_ean(self):

        return normalize_identifier(self.ean)


# ============================================================
# M99 VARIANT
# ============================================================

@dataclass
class M99Variant:

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

    def normalized_size(self):

        return normalize_size(self.size)

    def normalized_color(self):

        return normalize_color(self.color)

    def normalized_ean(self):

        return normalize_identifier(self.ean)


# ============================================================
# M99 PRODUCT MASTER
# ============================================================

@dataclass
class M99Product:

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
# PRODUCT MATCH RESULT
# ============================================================

@dataclass
class ProductMatchResult:

    status: str

    score: float

    product_id: Optional[str] = None

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

    def to_dict(self):

        return {
            "status": self.status,
            "score": round(self.score, 2),
            "product_id": self.product_id,
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
# VARIANT MATCH RESULT
# ============================================================

@dataclass
class VariantMatchResult:

    status: str

    score: float

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

    candidates: list[dict[str, Any]] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "status": self.status,
            "score": round(self.score, 2),
            "variant_id": self.variant_id,
            "matched_fields":
                self.matched_fields,
            "missing_fields":
                self.missing_fields,
            "conflicts":
                self.conflicts,
            "reasons":
                self.reasons,
            "candidates":
                self.candidates,
        }


# ============================================================
# FINAL MATCH RESULT
# ============================================================

@dataclass
class MatchResult:

    status: str

    product: Optional[ProductMatchResult] = None

    variant: Optional[VariantMatchResult] = None

    product_id: Optional[str] = None

    variant_id: Optional[str] = None

    reasons: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "status": self.status,

            "product_id":
                self.product_id,

            "variant_id":
                self.variant_id,

            "product":
                self.product.to_dict()
                if self.product
                else None,

            "variant":
                self.variant.to_dict()
                if self.variant
                else None,

            "reasons":
                self.reasons,
        }


# ============================================================
# PRODUCT MATCHER
# ============================================================

class ProductMatcher:

    # --------------------------------------------------------
    # PRODUCT WEIGHTS
    # --------------------------------------------------------

    EAN_WEIGHT = 100

    MANUFACTURER_SKU_WEIGHT = 90

    SUPPLIER_SKU_WEIGHT = 80

    BRAND_WEIGHT = 25

    NAME_WEIGHT = 60

    # --------------------------------------------------------
    # VARIANT WEIGHTS
    # --------------------------------------------------------

    VARIANT_EAN_WEIGHT = 100

    VARIANT_SIZE_WEIGHT = 50

    VARIANT_COLOR_WEIGHT = 50

    VARIANT_MANUFACTURER_WEIGHT = 90

    VARIANT_SUPPLIER_WEIGHT = 80

    CONFLICT_PENALTY = 100

    # ========================================================
    # PRODUCT MATCH
    # ========================================================

    def match_product_identity(
        self,
        external: ExternalProduct,
        product: M99Product,
    ) -> ProductMatchResult:

        score = 0.0

        matched = []

        missing = []

        conflicts = []

        reasons = []

        # ----------------------------------------------------
        # EAN
        # ----------------------------------------------------

        if external.ean:

            if external.ean and product.manufacturer_sku:
                pass

            # Product-level EAN is not currently stored
            # in the demo Product Master.
            #
            # Therefore EAN is ignored at product level
            # unless supplied through attributes.

        else:

            missing.append(
                "external.ean"
            )

        # ----------------------------------------------------
        # MANUFACTURER SKU
        # ----------------------------------------------------

        if external.manufacturer_sku:

            if product.manufacturer_sku:

                if (
                    normalize_identifier(
                        external.manufacturer_sku
                    )
                    ==
                    normalize_identifier(
                        product.manufacturer_sku
                    )
                ):

                    score += (
                        self.MANUFACTURER_SKU_WEIGHT
                    )

                    matched.append(
                        "manufacturer_sku"
                    )

                else:

                    conflicts.append(
                        "manufacturer_sku"
                    )

        # ----------------------------------------------------
        # SUPPLIER SKU
        # ----------------------------------------------------

        if external.supplier_sku:

            if product.supplier_sku:

                if (
                    normalize_identifier(
                        external.supplier_sku
                    )
                    ==
                    normalize_identifier(
                        product.supplier_sku
                    )
                ):

                    score += (
                        self.SUPPLIER_SKU_WEIGHT
                    )

                    matched.append(
                        "supplier_sku"
                    )

                else:

                    conflicts.append(
                        "supplier_sku"
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
                        self.BRAND_WEIGHT
                    )

                    matched.append(
                        "brand"
                    )

                else:

                    conflicts.append(
                        "brand"
                    )

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        similarity = name_similarity(
            external.name,
            product.name,
        )

        if similarity >= 0.80:

            score += self.NAME_WEIGHT

            matched.append(
                "name_exact_or_near_exact"
            )

            reasons.append(
                "Strong product-name similarity."
            )

        elif similarity >= 0.55:

            score += (
                self.NAME_WEIGHT * 0.75
            )

            matched.append(
                "name_partial"
            )

            reasons.append(
                "Good product-name similarity."
            )

        elif similarity >= 0.30:

            score += (
                self.NAME_WEIGHT * 0.40
            )

            matched.append(
                "name_weak"
            )

            reasons.append(
                "Weak product-name similarity."
            )

        else:

            conflicts.append(
                "name"
            )

        # ----------------------------------------------------
        # FINAL PRODUCT STATUS
        # ----------------------------------------------------

        if conflicts:

            status = REJECTED

            reasons.append(
                "Product identity conflict detected."
            )

        elif score >= 90:

            status = CONFIRMED

            reasons.append(
                "Product identity confirmed."
            )

        elif score >= 60:

            status = HIGH_CONFIDENCE

            reasons.append(
                "Product identity has high confidence."
            )

        elif score >= 30:

            status = REVIEW

            reasons.append(
                "Product identity requires review."
            )

        else:

            status = REJECTED

            reasons.append(
                "Insufficient product identity evidence."
            )

        return ProductMatchResult(
            status=status,
            score=min(100.0, score),
            product_id=product.product_id,
            matched_fields=matched,
            missing_fields=missing,
            conflicts=conflicts,
            reasons=reasons,
        )

    # ========================================================
    # VARIANT MATCH
    # ========================================================

    def match_variant(
        self,
        external: ExternalProduct,
        product: M99Product,
    ) -> VariantMatchResult:

        candidates = []

        # ----------------------------------------------------
        # TEST EACH VARIANT
        # ----------------------------------------------------

        for variant in product.variants:

            score = 0.0

            matched = []

            missing = []

            conflicts = []

            # ------------------------------------------------
            # EAN
            # ------------------------------------------------

            if external.ean:

                if variant.ean:

                    if (
                        external.normalized_ean()
                        ==
                        variant.normalized_ean()
                    ):

                        score += (
                            self.VARIANT_EAN_WEIGHT
                        )

                        matched.append(
                            "ean"
                        )

                    else:

                        conflicts.append(
                            "ean"
                        )

            # ------------------------------------------------
            # SIZE
            # ------------------------------------------------

            if external.size:

                if variant.size:

                    if (
                        external.normalized_size()
                        ==
                        variant.normalized_size()
                    ):

                        score += (
                            self.VARIANT_SIZE_WEIGHT
                        )

                        matched.append(
                            "size"
                        )

                    else:

                        conflicts.append(
                            "size"
                        )

                else:

                    missing.append(
                        "variant.size"
                    )

            else:

                missing.append(
                    "external.size"
                )

            # ------------------------------------------------
            # COLOR
            # ------------------------------------------------

            if external.color:

                if variant.color:

                    if (
                        external.normalized_color()
                        ==
                        variant.normalized_color()
                    ):

                        score += (
                            self.VARIANT_COLOR_WEIGHT
                        )

                        matched.append(
                            "color"
                        )

                    else:

                        conflicts.append(
                            "color"
                        )

                else:

                    missing.append(
                        "variant.color"
                    )

            else:

                missing.append(
                    "external.color"
                )

            # ------------------------------------------------
            # MANUFACTURER SKU
            # ------------------------------------------------

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
                            self.VARIANT_MANUFACTURER_WEIGHT
                        )

                        matched.append(
                            "manufacturer_sku"
                        )

                    else:

                        conflicts.append(
                            "manufacturer_sku"
                        )

            # ------------------------------------------------
            # SUPPLIER SKU
            # ------------------------------------------------

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
                            self.VARIANT_SUPPLIER_WEIGHT
                        )

                        matched.append(
                            "supplier_sku"
                        )

                    else:

                        conflicts.append(
                            "supplier_sku"
                        )

            # ------------------------------------------------
            # CONFLICT
            # ------------------------------------------------

            if conflicts:

                continue

            candidates.append(
                {
                    "variant_id":
                        variant.variant_id,

                    "score":
                        min(
                            100.0,
                            score
                        ),

                    "matched_fields":
                        matched,

                    "missing_fields":
                        missing,
                }
            )

        # ====================================================
        # NO CANDIDATES
        # ====================================================

        if not candidates:

            return VariantMatchResult(
                status=REJECTED,
                score=0.0,
                reasons=[
                    "No compatible variant found."
                ],
            )

        # ====================================================
        # SORT
        # ====================================================

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        best = candidates[0]

        best_score = best["score"]

        # ----------------------------------------------------
        # SAME SCORE = AMBIGUITY
        # ----------------------------------------------------

        same_score = [
            candidate
            for candidate in candidates
            if candidate["score"] == best_score
        ]

        if len(same_score) > 1:

            return VariantMatchResult(
                status=VARIANT_AMBIGUOUS,
                score=best_score,
                variant_id=None,
                matched_fields=best[
                    "matched_fields"
                ],
                missing_fields=best[
                    "missing_fields"
                ],
                reasons=[
                    "Multiple variants have identical matching evidence."
                ],
                candidates=candidates,
            )

        # ====================================================
        # VARIANT STATUS
        # ====================================================

        matched_fields = best[
            "matched_fields"
        ]

        missing_fields = best[
            "missing_fields"
        ]

        # ----------------------------------------------------
        # SIZE + COLOR
        # ----------------------------------------------------

        has_size = (
            "size"
            in matched_fields
        )

        has_color = (
            "color"
            in matched_fields
        )

        # ----------------------------------------------------
        # BOTH SIZE AND COLOR
        # ----------------------------------------------------

        if has_size and has_color:

            status = CONFIRMED

            reason = (
                "Exact size and color variant match."
            )

        # ----------------------------------------------------
        # UNIQUE SIZE
        # ----------------------------------------------------

        elif has_size and not has_color:

            same_size = [
                candidate
                for candidate in candidates
                if "size"
                in candidate["matched_fields"]
            ]

            if len(same_size) == 1:

                status = HIGH_CONFIDENCE

                reason = (
                    "Unique size identifies one variant."
                )

            else:

                status = VARIANT_AMBIGUOUS

                reason = (
                    "Size matches multiple variants."
                )

        # ----------------------------------------------------
        # UNIQUE COLOR
        # ----------------------------------------------------

        elif has_color and not has_size:

            same_color = [
                candidate
                for candidate in candidates
                if "color"
                in candidate["matched_fields"]
            ]

            if len(same_color) == 1:

                status = HIGH_CONFIDENCE

                reason = (
                    "Unique color identifies one variant."
                )

            else:

                status = VARIANT_AMBIGUOUS

                reason = (
                    "Color matches multiple variants."
                )

        # ----------------------------------------------------
        # NO VARIANT ATTRIBUTE
        # ----------------------------------------------------

        else:

            status = VARIANT_NOT_DETERMINED

            reason = (
                "No sufficient variant attributes were supplied."
            )

        return VariantMatchResult(
            status=status,
            score=best_score,
            variant_id=(
                best["variant_id"]
                if status not in {
                    VARIANT_AMBIGUOUS,
                    VARIANT_NOT_DETERMINED,
                }
                else None
            ),
            matched_fields=matched_fields,
            missing_fields=missing_fields,
            reasons=[reason],
            candidates=candidates,
        )

    # ========================================================
    # COMPLETE MATCH
    # ========================================================

    def match(
        self,
        external: ExternalProduct,
        product: M99Product,
    ) -> MatchResult:

        product_result = (
            self.match_product_identity(
                external,
                product,
            )
        )

        # ----------------------------------------------------
        # PRODUCT REJECTED
        # ----------------------------------------------------

        if product_result.status == REJECTED:

            return MatchResult(
                status=REJECTED,
                product=product_result,
                product_id=None,
                reasons=[
                    "Product identity could not be confirmed."
                ],
            )

        # ----------------------------------------------------
        # PRODUCT OK
        # ----------------------------------------------------

        variant_result = self.match_variant(
            external,
            product,
        )

        # ----------------------------------------------------
        # VARIANT CONFIRMED
        # ----------------------------------------------------

        if (
            variant_result.status
            == CONFIRMED
        ):

            final_status = CONFIRMED

            final_variant_id = (
                variant_result.variant_id
            )

        elif (
            variant_result.status
            == HIGH_CONFIDENCE
        ):

            final_status = HIGH_CONFIDENCE

            final_variant_id = (
                variant_result.variant_id
            )

        elif (
            variant_result.status
            == VARIANT_AMBIGUOUS
        ):

            final_status = REVIEW

            final_variant_id = None

        else:

            final_status = REVIEW

            final_variant_id = None

        return MatchResult(
            status=final_status,
            product=product_result,
            variant=variant_result,
            product_id=product.product_id,
            variant_id=final_variant_id,
            reasons=[
                "Product and variant evaluated separately."
            ],
        )


# ============================================================
# MONEYWORKS HELPER
# ============================================================

def moneyworks_product(
    code: str,
    name: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
) -> ExternalProduct:

    return ExternalProduct(
        source="moneyworks",
        code=code,
        name=name,
        size=size,
        color=color,
    )


# ============================================================
# DEMO PRODUCTS
# ============================================================

def create_demo_products():

    return [

        M99Product(
            product_id="M99-PM-000001",

            name=(
                "PUMA Velocity 2.0 Black Low"
            ),

            brand="PUMA Safety",

            model=(
                "Velocity 2.0 Black Low"
            ),

            manufacturer_sku="643870",

            supplier_sku="06100288",

            variants=[

                M99Variant(
                    variant_id="M99-PV-000001",

                    product_id="M99-PM-000001",

                    name=(
                        "PUMA Velocity 2.0 "
                        "Black Low Size 40 Black"
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
                        "PUMA Velocity 2.0 "
                        "Black Low Size 41 Black"
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
                        "PUMA Velocity 2.0 "
                        "Black Low Size 42 Black"
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
# TEST
# ============================================================

def run_test(
    matcher,
    products,
    title,
    external,
):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    result = matcher.match(
        external,
        products[0],
    )

    print()

    print(
        result.to_dict()
    )

    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "M99 Knowledge Platform"
    )

    print(
        "Product Matcher v0.3"
    )

    print(
        "========================================"
    )

    print()

    matcher = ProductMatcher()

    products = create_demo_products()

    # ========================================================
    # TEST 1
    # Name + Size + Color
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 1 - Name + Size + Color",

        moneyworks_product(
            code="MW-0001842",

            name=(
                "Работни обувки PUMA "
                "VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),

            size="40",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 2
    # Name + Size
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 2 - Name + Size",

        moneyworks_product(
            code="MW-0001843",

            name=(
                "Работни обувки PUMA "
                "VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),

            size="41",
        ),
    )

    # ========================================================
    # TEST 3
    # Name + Color
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 3 - Name + Color",

        moneyworks_product(
            code="MW-0001844",

            name=(
                "Работни обувки PUMA "
                "VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),

            color="Black",
        ),
    )

    # ========================================================
    # TEST 4
    # Name only
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 4 - Name Only",

        moneyworks_product(
            code="MW-0001845",

            name=(
                "Работни обувки PUMA "
                "VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),
        ),
    )

    # ========================================================
    # TEST 5
    # Wrong size
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 5 - Wrong Size",

        moneyworks_product(
            code="MW-0001846",

            name=(
                "Работни обувки PUMA "
                "VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),

            size="45",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 6
    # Completely different product
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 6 - Different Product",

        moneyworks_product(
            code="MW-0001847",

            name="Safety Shoes Other Brand",

            size="40",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 7
    # Size only, but UNIQUE size
    # ========================================================

    run_test(
        matcher,
        products,
        "TEST 7 - Size Only",

        moneyworks_product(
            code="MW-0001848",

            name=(
                "PUMA Velocity 2.0 Black Low"
            ),

            size="42",
        ),
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "========================================"
    )

    print(
        "Product Matcher v0.3 test completed."
    )

    print(
        "========================================"
    )
