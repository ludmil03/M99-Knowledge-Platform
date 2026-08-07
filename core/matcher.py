#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Product Matcher v0.4

Purpose
-------
Matches external / legacy articles against the M99 Identity Architecture.

Architecture
------------

External Article
       |
       v
PRODUCT MATCH
       |
       v
VARIANT MATCH
       |
       v
FINAL DECISION

Important rules
---------------

1. Product identity and Variant identity are evaluated separately.

2. Missing information is NOT a conflict.

3. Conflicting information IS a conflict.

4. A Variant can never be CONFIRMED if Product is only REVIEW.

5. Name alone may identify a Product candidate,
   but never identifies a Variant.

6. Size alone may identify a Variant only when
   the size is unique inside the Product Master.

7. Color alone may identify a Variant only when
   the color is unique inside the Product Master.

8. Size + Color identifies a Variant when both
   attributes match the same Variant.

9. Zero-information variants are NOT candidates.

10. Matcher NEVER creates or modifies M99 products,
    variants or mappings.

11. The final decision can never be more confident
    than the Product identity.

Version: 0.4
"""


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re


# ============================================================
# STATUS
# ============================================================

CONFIRMED = "CONFIRMED"
HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
REVIEW = "REVIEW"
REJECTED = "REJECTED"

AMBIGUOUS = "AMBIGUOUS"
NOT_DETERMINED = "NOT_DETERMINED"


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

    value = re.sub(
        r"^(size|shoes size)"
        r"\s*[:\-]?\s*",
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
# NAME PROCESSING
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
# PRODUCT RESULT
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
# VARIANT RESULT
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
# FINAL RESULT
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
            "product_id": self.product_id,
            "variant_id": self.variant_id,
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
# MATCHER
# ============================================================

class ProductMatcher:

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    NAME_STRONG = 0.80
    NAME_GOOD = 0.55
    NAME_WEAK = 0.30

    # --------------------------------------------------------
    # VARIANT
    # --------------------------------------------------------

    SIZE_WEIGHT = 50
    COLOR_WEIGHT = 50

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

            product_ean = product.__dict__.get(
                "ean"
            )

            if product_ean:

                if (
                    external.normalized_ean()
                    ==
                    normalize_identifier(
                        product_ean
                    )
                ):

                    score += 100

                    matched.append(
                        "ean"
                    )

                else:

                    conflicts.append(
                        "ean"
                    )

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

                    score += 90

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

                    score += 80

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

                    score += 20

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

        if similarity >= self.NAME_STRONG:

            score += 60

            matched.append(
                "name_strong"
            )

            reasons.append(
                "Strong product-name similarity."
            )

        elif similarity >= self.NAME_GOOD:

            score += 45

            matched.append(
                "name_partial"
            )

            reasons.append(
                "Good product-name similarity."
            )

        elif similarity >= self.NAME_WEAK:

            score += 20

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
        # PRODUCT DECISION
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

        else:

            status = REVIEW

            reasons.append(
                "Product identity requires review."
            )

        return ProductMatchResult(
            status=status,
            score=min(score, 100),
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

        external_size = (
            external.normalized_size()
        )

        external_color = (
            external.normalized_color()
        )

        # ----------------------------------------------------
        # NO VARIANT INFORMATION
        # ----------------------------------------------------

        if not external_size and not external_color:

            return VariantMatchResult(
                status=NOT_DETERMINED,
                score=0,
                variant_id=None,
                missing_fields=[
                    "external.size",
                    "external.color",
                ],
                reasons=[
                    "No size or color was supplied."
                ],
                candidates=[],
            )

        # ----------------------------------------------------
        # CHECK VARIANTS
        # ----------------------------------------------------

        for variant in product.variants:

            variant_size = (
                variant.normalized_size()
            )

            variant_color = (
                variant.normalized_color()
            )

            matched = []

            missing = []

            conflicts = []

            score = 0.0

            # ------------------------------------------------
            # SIZE
            # ------------------------------------------------

            if external_size:

                if not variant_size:

                    missing.append(
                        "variant.size"
                    )

                elif (
                    external_size
                    ==
                    variant_size
                ):

                    score += self.SIZE_WEIGHT

                    matched.append(
                        "size"
                    )

                else:

                    conflicts.append(
                        "size"
                    )

            else:

                missing.append(
                    "external.size"
                )

            # ------------------------------------------------
            # COLOR
            # ------------------------------------------------

            if external_color:

                if not variant_color:

                    missing.append(
                        "variant.color"
                    )

                elif (
                    external_color
                    ==
                    variant_color
                ):

                    score += self.COLOR_WEIGHT

                    matched.append(
                        "color"
                    )

                else:

                    conflicts.append(
                        "color"
                    )

            else:

                missing.append(
                    "external.color"
                )

            # ------------------------------------------------
            # CONFLICT = NOT A CANDIDATE
            # ------------------------------------------------

            if conflicts:

                continue

            # ------------------------------------------------
            # ZERO MATCH = NOT A CANDIDATE
            # ------------------------------------------------

            if not matched:

                continue

            candidates.append(
                {
                    "variant_id":
                        variant.variant_id,

                    "score":
                        score,

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
                score=0,
                variant_id=None,
                reasons=[
                    "No compatible variant found."
                ],
                candidates=[],
            )

        # ====================================================
        # SORT
        # ====================================================

        candidates.sort(
            key=lambda item:
                item["score"],
            reverse=True,
        )

        best = candidates[0]

        best_score = best["score"]

        # ====================================================
        # AMBIGUOUS
        # ====================================================

        equal_candidates = [
            candidate
            for candidate in candidates
            if candidate["score"]
            == best_score
        ]

        if len(equal_candidates) > 1:

            return VariantMatchResult(
                status=AMBIGUOUS,
                score=best_score,
                variant_id=None,
                matched_fields=
                    best["matched_fields"],
                missing_fields=
                    best["missing_fields"],
                reasons=[
                    "Multiple variants match with equal evidence."
                ],
                candidates=candidates,
            )

        # ====================================================
        # SIZE + COLOR
        # ====================================================

        if (
            "size"
            in best["matched_fields"]
            and
            "color"
            in best["matched_fields"]
        ):

            return VariantMatchResult(
                status=CONFIRMED,
                score=100,
                variant_id=
                    best["variant_id"],
                matched_fields=
                    best["matched_fields"],
                missing_fields=
                    best["missing_fields"],
                reasons=[
                    "Exact size and color variant match."
                ],
                candidates=candidates,
            )

        # ====================================================
        # SIZE ONLY
        # ====================================================

        if (
            "size"
            in best["matched_fields"]
        ):

            return VariantMatchResult(
                status=HIGH_CONFIDENCE,
                score=50,
                variant_id=
                    best["variant_id"],
                matched_fields=
                    best["matched_fields"],
                missing_fields=
                    best["missing_fields"],
                reasons=[
                    "Unique size identifies one variant."
                ],
                candidates=candidates,
            )

        # ====================================================
        # COLOR ONLY
        # ====================================================

        if (
            "color"
            in best["matched_fields"]
        ):

            return VariantMatchResult(
                status=HIGH_CONFIDENCE,
                score=50,
                variant_id=
                    best["variant_id"],
                matched_fields=
                    best["matched_fields"],
                missing_fields=
                    best["missing_fields"],
                reasons=[
                    "Unique color identifies one variant."
                ],
                candidates=candidates,
            )

        # ====================================================
        # FALLBACK
        # ====================================================

        return VariantMatchResult(
            status=REVIEW,
            score=best_score,
            variant_id=None,
            matched_fields=
                best["matched_fields"],
            missing_fields=
                best["missing_fields"],
            reasons=[
                "Variant requires review."
            ],
            candidates=candidates,
        )

    # ========================================================
    # FINAL DECISION
    # ========================================================

    def final_status(
        self,
        product_status: str,
        variant_status: str,
    ) -> str:

        # ----------------------------------------------------
        # PRODUCT REJECTED
        # ----------------------------------------------------

        if product_status == REJECTED:

            return REJECTED

        # ----------------------------------------------------
        # PRODUCT REVIEW ALWAYS CAPS RESULT
        # ----------------------------------------------------

        if product_status == REVIEW:

            return REVIEW

        # ----------------------------------------------------
        # PRODUCT HIGH CONFIDENCE
        # ----------------------------------------------------

        if (
            product_status
            == HIGH_CONFIDENCE
        ):

            if variant_status == CONFIRMED:

                return HIGH_CONFIDENCE

            if variant_status == HIGH_CONFIDENCE:

                return HIGH_CONFIDENCE

            return REVIEW

        # ----------------------------------------------------
        # PRODUCT CONFIRMED
        # ----------------------------------------------------

        if (
            product_status
            == CONFIRMED
        ):

            if variant_status == CONFIRMED:

                return CONFIRMED

            if variant_status == HIGH_CONFIDENCE:

                return HIGH_CONFIDENCE

            if variant_status == NOT_DETERMINED:

                return REVIEW

            if variant_status == AMBIGUOUS:

                return REVIEW

            if variant_status == REJECTED:

                return REVIEW

        return REVIEW

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

        if (
            product_result.status
            == REJECTED
        ):

            return MatchResult(
                status=REJECTED,
                product=product_result,
                variant=None,
                product_id=None,
                variant_id=None,
                reasons=[
                    "Product identity rejected."
                ],
            )

        # ----------------------------------------------------
        # VARIANT
        # ----------------------------------------------------

        variant_result = (
            self.match_variant(
                external,
                product,
            )
        )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        final = self.final_status(
            product_result.status,
            variant_result.status,
        )

        # ----------------------------------------------------
        # PRODUCT ID
        # ----------------------------------------------------

        product_id = (
            product.product_id
        )

        # ----------------------------------------------------
        # VARIANT ID
        # ----------------------------------------------------

        variant_id = None

        if final in {
            CONFIRMED,
            HIGH_CONFIDENCE,
        }:

            variant_id = (
                variant_result.variant_id
            )

        return MatchResult(
            status=final,
            product=product_result,
            variant=variant_result,
            product_id=product_id,
            variant_id=variant_id,
            reasons=[
                "Product and variant evaluated separately.",
                f"Final status limited by product status: "
                f"{product_result.status}.",
            ],
        )


# ============================================================
# MONEYWORKS FACTORY
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
# DEMO PRODUCT MASTER
# ============================================================

def create_demo_product():

    return M99Product(

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
                    "Black Low 40 Black"
                ),
                size="40",
                color="Black",
            ),

            M99Variant(
                variant_id="M99-PV-000002",
                product_id="M99-PM-000001",
                name=(
                    "PUMA Velocity 2.0 "
                    "Black Low 41 Black"
                ),
                size="41",
                color="Black",
            ),

            M99Variant(
                variant_id="M99-PV-000003",
                product_id="M99-PM-000001",
                name=(
                    "PUMA Velocity 2.0 "
                    "Black Low 42 Black"
                ),
                size="42",
                color="Black",
            ),
        ],
    )


# ============================================================
# TEST RUNNER
# ============================================================

def run_test(
    matcher: ProductMatcher,
    product: M99Product,
    title: str,
    external: ExternalProduct,
):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()

    result = matcher.match(
        external,
        product,
    )

    print(
        result.to_dict()
    )


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
        "Product Matcher v0.4"
    )

    print(
        "========================================"
    )

    product = create_demo_product()

    matcher = ProductMatcher()

    # ========================================================
    # TEST 1
    # Name + Size + Color
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 1 - Name + Size + Color",

        moneyworks_product(
            "MW-0001842",

            "Работни обувки PUMA "
            "VELOCITY 2.0 BLACK LOW "
            "S3 ESD",

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
        product,
        "TEST 2 - Name + Size",

        moneyworks_product(
            "MW-0001843",

            "Работни обувки PUMA "
            "VELOCITY 2.0 BLACK LOW "
            "S3 ESD",

            size="41",
        ),
    )

    # ========================================================
    # TEST 3
    # Name + Color
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 3 - Name + Color",

        moneyworks_product(
            "MW-0001844",

            "Работни обувки PUMA "
            "VELOCITY 2.0 BLACK LOW "
            "S3 ESD",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 4
    # Name Only
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 4 - Name Only",

        moneyworks_product(
            "MW-0001845",

            "Работни обувки PUMA "
            "VELOCITY 2.0 BLACK LOW "
            "S3 ESD",
        ),
    )

    # ========================================================
    # TEST 5
    # Wrong Size
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 5 - Wrong Size",

        moneyworks_product(
            "MW-0001846",

            "Работни обувки PUMA "
            "VELOCITY 2.0 BLACK LOW "
            "S3 ESD",

            size="45",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 6
    # Different Product
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 6 - Different Product",

        moneyworks_product(
            "MW-0001847",

            "Safety Shoes Other Brand",

            size="40",

            color="Black",
        ),
    )

    # ========================================================
    # TEST 7
    # Unique Size
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 7 - Size Only",

        moneyworks_product(
            "MW-0001848",

            "PUMA Velocity 2.0 Black Low",

            size="42",
        ),
    )

    # ========================================================
    # TEST 8
    # NO SIZE / NO COLOR
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 8 - No Variant Information",

        moneyworks_product(
            "MW-0001849",

            "PUMA Velocity 2.0 Black Low",
        ),
    )

    # ========================================================
    # TEST 9
    # CONFLICTING SIZE
    # ========================================================

    run_test(
        matcher,
        product,
        "TEST 9 - Conflicting Size",

        moneyworks_product(
            "MW-0001850",

            "PUMA Velocity 2.0 Black Low",

            size="45",

            color="Black",
        ),
    )

    print()
    print(
        "========================================"
    )

    print(
        "Product Matcher v0.4 test completed."
    )

    print(
        "========================================"
    )
