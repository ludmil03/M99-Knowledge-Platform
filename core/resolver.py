#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Identity Resolver v0.2

Responsible for resolving external identities to:

    M99 Product Master
        ↓
    M99 Product Variant

External systems may contain:

    - Manufacturer SKU
    - Supplier SKU
    - Supplier product reference
    - EAN
    - Legacy article number
    - Legacy article name
    - Dolibarr reference
    - MoneyWorks article number

IMPORTANT:

External identifiers NEVER become the M99 identity.

M99 Product ID and M99 SKU remain authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# CONSTANTS
# ============================================================

VALID_SOURCE_TYPES = {
    "manufacturer",
    "supplier",
    "ean",
    "moneyworks",
    "dolibarr",
    "legacy",
    "website",
    "manual",
}

VALID_MATCH_TYPES = {
    "exact",
    "normalized",
    "manual",
}

VALID_MATCH_STATUSES = {
    "confirmed",
    "high_confidence",
    "review",
    "rejected",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_identifier(
    value: Any
) -> Optional[str]:
    """
    Normalize an external identifier.

    Examples:

        " 06100288 "
            ->
        "06100288"

        "TB-P1648-A12467"
            ->
        "TB-P1648-A12467"
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value.upper()


def normalize_name(
    value: Any
) -> Optional[str]:
    """
    Basic normalization of an external article name.

    This is NOT intended to replace semantic matching.
    It only prepares names for comparison.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = " ".join(
        value.split()
    )

    return value.casefold()


# ============================================================
# EXTERNAL REFERENCE
# ============================================================

@dataclass(frozen=True)
class ExternalReference:
    """
    Represents one external identity.

    Example:

        source_type = supplier
        source_id   = STENSO
        identifier  = 06100288
    """

    source_type: str

    source_id: str

    identifier: str

    name: Optional[str] = None

    attributes: dict[str, str] = field(
        default_factory=dict
    )

    def normalized_identifier(
        self
    ) -> Optional[str]:

        return normalize_identifier(
            self.identifier
        )

    def normalized_name(
        self
    ) -> Optional[str]:

        return normalize_name(
            self.name
        )

    def validate(self) -> list[str]:

        errors: list[str] = []

        if (
            self.source_type
            not in VALID_SOURCE_TYPES
        ):

            errors.append(
                "Invalid source type: "
                f"{self.source_type}"
            )

        if not self.source_id:

            errors.append(
                "Source ID is missing."
            )

        if not self.identifier:

            errors.append(
                "External identifier is missing."
            )

        return errors


# ============================================================
# IDENTITY MAPPING
# ============================================================

@dataclass
class IdentityMapping:
    """
    Maps an external identity to an M99 identity.

    M99 remains authoritative.

    Example:

        MoneyWorks:
            article = 000123

        maps to:

            M99 Product:
                M99-PM-000001

            M99 Variant:
                M99-PV-000001
    """

    external: ExternalReference

    m99_product_id: str

    m99_variant_id: Optional[str] = None

    match_type: str = "manual"

    confidence: float = 0.0

    status: str = "review"

    notes: Optional[str] = None

    def validate(self) -> list[str]:

        errors: list[str] = []

        if not self.m99_product_id:

            errors.append(
                "M99 Product ID is missing."
            )

        if (
            self.match_type
            not in VALID_MATCH_TYPES
        ):

            errors.append(
                "Invalid match type: "
                f"{self.match_type}"
            )

        if (
            self.status
            not in VALID_MATCH_STATUSES
        ):

            errors.append(
                "Invalid match status: "
                f"{self.status}"
            )

        if not (
            0 <= self.confidence <= 100
        ):

            errors.append(
                "Confidence must be "
                "between 0 and 100."
            )

        errors.extend(
            self.external.validate()
        )

        return errors

    def to_dict(self) -> dict[str, Any]:

        return {
            "external": {
                "source_type":
                    self.external.source_type,

                "source_id":
                    self.external.source_id,

                "identifier":
                    self.external.identifier,

                "name":
                    self.external.name,

                "attributes":
                    self.external.attributes,
            },

            "m99_product_id":
                self.m99_product_id,

            "m99_variant_id":
                self.m99_variant_id,

            "match_type":
                self.match_type,

            "confidence":
                self.confidence,

            "status":
                self.status,

            "notes":
                self.notes,
        }


# ============================================================
# RESOLUTION RESULT
# ============================================================

@dataclass
class ResolutionResult:
    """
    Result returned by the resolver.
    """

    found: bool = False

    m99_product_id: Optional[str] = None

    m99_variant_id: Optional[str] = None

    confidence: float = 0.0

    status: str = "not_found"

    match_type: Optional[str] = None

    matched_reference: Optional[
        ExternalReference
    ] = None

    candidates: list[
        IdentityMapping
    ] = field(
        default_factory=list
    )

    message: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:

        return {
            "found":
                self.found,

            "m99_product_id":
                self.m99_product_id,

            "m99_variant_id":
                self.m99_variant_id,

            "confidence":
                self.confidence,

            "status":
                self.status,

            "match_type":
                self.match_type,

            "matched_reference":
                (
                    self.matched_reference.identifier
                    if self.matched_reference
                    else None
                ),

            "candidates":
                [
                    candidate.to_dict()
                    for candidate in self.candidates
                ],

            "message":
                self.message,
        }


# ============================================================
# IDENTITY RESOLVER
# ============================================================

class IdentityResolver:
    """
    Central identity resolution engine.

    Priority:

        1. Exact external identifier
        2. Exact EAN
        3. Exact normalized identifier
        4. Manual mapping
        5. Candidate review

    The resolver NEVER creates a new M99 Product automatically.
    """

    def __init__(
        self,
        mappings: Optional[
            list[IdentityMapping]
        ] = None,
    ) -> None:

        self.mappings = mappings or []

    # ========================================================
    # ADD MAPPING
    # ========================================================

    def add_mapping(
        self,
        mapping: IdentityMapping
    ) -> None:

        errors = mapping.validate()

        if errors:

            raise ValueError(
                "Invalid identity mapping: "
                + "; ".join(errors)
            )

        self.mappings.append(
            mapping
        )

    # ========================================================
    # EXACT IDENTIFIER SEARCH
    # ========================================================

    def find_exact(
        self,
        reference: ExternalReference
    ) -> list[IdentityMapping]:

        normalized_identifier = (
            reference.normalized_identifier()
        )

        if not normalized_identifier:

            return []

        results: list[
            IdentityMapping
        ] = []

        for mapping in self.mappings:

            external = mapping.external

            if (
                external.source_type
                != reference.source_type
            ):

                continue

            if (
                external.source_id
                != reference.source_id
            ):

                continue

            if (
                external.normalized_identifier()
                == normalized_identifier
            ):

                results.append(
                    mapping
                )

        return results

    # ========================================================
    # EAN SEARCH
    # ========================================================

    def find_ean(
        self,
        ean: str
    ) -> list[IdentityMapping]:

        normalized_ean = (
            normalize_identifier(ean)
        )

        if not normalized_ean:

            return []

        results = []

        for mapping in self.mappings:

            if (
                mapping.external.source_type
                != "ean"
            ):

                continue

            if (
                mapping.external.normalized_identifier()
                == normalized_ean
            ):

                results.append(
                    mapping
                )

        return results

    # ========================================================
    # NAME CANDIDATES
    # ========================================================

    def find_name_candidates(
        self,
        name: str
    ) -> list[IdentityMapping]:

        normalized = normalize_name(
            name
        )

        if not normalized:

            return []

        results = []

        for mapping in self.mappings:

            external_name = (
                mapping.external.normalized_name()
            )

            if not external_name:

                continue

            if (
                normalized
                == external_name
            ):

                results.append(
                    mapping
                )

        return results

    # ========================================================
    # RESOLVE
    # ========================================================

    def resolve(
        self,
        reference: ExternalReference
    ) -> ResolutionResult:

        # ----------------------------------------------------
        # VALIDATE INPUT
        # ----------------------------------------------------

        errors = reference.validate()

        if errors:

            return ResolutionResult(
                found=False,
                status="invalid",
                message="; ".join(errors),
            )

        # ----------------------------------------------------
        # EXACT MATCH
        # ----------------------------------------------------

        exact_matches = self.find_exact(
            reference
        )

        if len(exact_matches) == 1:

            mapping = exact_matches[0]

            return ResolutionResult(
                found=True,
                m99_product_id=(
                    mapping.m99_product_id
                ),
                m99_variant_id=(
                    mapping.m99_variant_id
                ),
                confidence=100.0,
                status=mapping.status,
                match_type="exact",
                matched_reference=(
                    mapping.external
                ),
                candidates=[
                    mapping
                ],
                message=(
                    "Exact identity match."
                ),
            )

        # ----------------------------------------------------
        # MULTIPLE EXACT MATCHES
        # ----------------------------------------------------

        if len(exact_matches) > 1:

            return ResolutionResult(
                found=False,
                confidence=100.0,
                status="review",
                match_type="exact",
                candidates=exact_matches,
                message=(
                    "Multiple exact mappings "
                    "found. Manual review required."
                ),
            )

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        return ResolutionResult(
            found=False,
            status="not_found",
            confidence=0.0,
            candidates=[],
            message=(
                "No exact identity mapping found."
            ),
        )

    # ========================================================
    # RESOLVE EXTERNAL DATA
    # ========================================================

    def resolve_external(
        self,
        source_type: str,
        source_id: str,
        identifier: str,
        name: Optional[str] = None,
        attributes: Optional[
            dict[str, str]
        ] = None,
    ) -> ResolutionResult:

        reference = ExternalReference(
            source_type=source_type,
            source_id=source_id,
            identifier=identifier,
            name=name,
            attributes=attributes or {},
        )

        return self.resolve(
            reference
        )

    # ========================================================
    # REVIEW CANDIDATES
    # ========================================================

    def candidates_for_review(
        self,
        reference: ExternalReference
    ) -> list[IdentityMapping]:

        """
        Return possible mappings for manual review.

        This intentionally does NOT automatically
        assign an M99 identity.
        """

        results = []

        normalized_name = (
            reference.normalized_name()
        )

        normalized_identifier = (
            reference.normalized_identifier()
        )

        for mapping in self.mappings:

            external = mapping.external

            score = 0

            if (
                normalized_identifier
                and
                external.normalized_identifier()
                == normalized_identifier
            ):

                score += 100

            if (
                normalized_name
                and
                external.normalized_name()
                == normalized_name
            ):

                score += 50

            if score > 0:

                results.append(
                    mapping
                )

        return results

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> list[str]:

        errors: list[str] = []

        seen: set[
            tuple[str, str, str]
        ] = set()

        for mapping in self.mappings:

            errors.extend(
                mapping.validate()
            )

            key = (
                mapping.external.source_type,
                mapping.external.source_id,
                mapping.external.normalized_identifier()
                or "",
            )

            if key in seen:

                errors.append(
                    "Duplicate external identity: "
                    f"{key}"
                )

            seen.add(
                key
            )

        return errors


# ============================================================
# HELPER
# ============================================================

def create_mapping(
    source_type: str,
    source_id: str,
    identifier: str,
    m99_product_id: str,
    m99_variant_id: Optional[str] = None,
    name: Optional[str] = None,
    attributes: Optional[
        dict[str, str]
    ] = None,
    match_type: str = "manual",
    confidence: float = 0.0,
    status: str = "review",
    notes: Optional[str] = None,
) -> IdentityMapping:

    reference = ExternalReference(
        source_type=source_type,
        source_id=source_id,
        identifier=identifier,
        name=name,
        attributes=attributes or {},
    )

    return IdentityMapping(
        external=reference,
        m99_product_id=m99_product_id,
        m99_variant_id=m99_variant_id,
        match_type=match_type,
        confidence=confidence,
        status=status,
        notes=notes,
    )


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
        "Identity Resolver v0.2"
    )
    print(
        "========================================"
    )
    print()

    resolver = IdentityResolver()

    # --------------------------------------------------------
    # Manufacturer mapping
    # --------------------------------------------------------

    resolver.add_mapping(
        create_mapping(
            source_type="manufacturer",
            source_id="PUMA-SAFETY",
            identifier="643870",
            m99_product_id="M99-PM-000001",
            name="PUMA Velocity 2.0 Black Low",
            match_type="exact",
            confidence=100,
            status="confirmed",
        )
    )

    # --------------------------------------------------------
    # Supplier mapping
    # --------------------------------------------------------

    resolver.add_mapping(
        create_mapping(
            source_type="supplier",
            source_id="STENSO",
            identifier="06100288",
            m99_product_id="M99-PM-000001",
            name=(
                "PUMA VELOCITY 2.0 BLACK LOW "
                "S3 ESD"
            ),
            match_type="exact",
            confidence=100,
            status="confirmed",
        )
    )

    # --------------------------------------------------------
    # MoneyWorks mapping
    # --------------------------------------------------------

    resolver.add_mapping(
        create_mapping(
            source_type="moneyworks",
            source_id="GENSOFT-MONEYWORK",
            identifier="MW-0001842",
            m99_product_id="M99-PM-000001",
            m99_variant_id="M99-PV-000001",
            name=(
                "Работни обувки PUMA VELOCITY "
                "2.0 BLACK LOW S3 ESD"
            ),
            attributes={
                "size": "40",
                "color": "Black",
            },
            match_type="manual",
            confidence=98,
            status="confirmed",
            notes=(
                "Legacy article mapped to "
                "M99 Variant."
            ),
        )
    )

    # --------------------------------------------------------
    # Dolibarr mapping
    # --------------------------------------------------------

    resolver.add_mapping(
        create_mapping(
            source_type="dolibarr",
            source_id="DOLIBARR",
            identifier="TB-P1648-A12467",
            m99_product_id="M99-PM-000001",
            m99_variant_id="M99-PV-000001",
            name=(
                "Работни обувки PUMA VELOCITY "
                "2.0 BLACK LOW S3 ESD - Shoes Size: 40"
            ),
            attributes={
                "size": "40",
                "color": "Black",
            },
            match_type="manual",
            confidence=99,
            status="confirmed",
        )
    )

    # ========================================================
    # TEST SUPPLIER
    # ========================================================

    print(
        "Testing supplier identity..."
    )

    result = resolver.resolve_external(
        source_type="supplier",
        source_id="STENSO",
        identifier="06100288",
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # TEST MONEYWORKS
    # ========================================================

    print(
        "Testing MoneyWorks identity..."
    )

    result = resolver.resolve_external(
        source_type="moneyworks",
        source_id="GENSOFT-MONEYWORK",
        identifier="MW-0001842",
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # TEST DOLIBARR
    # ========================================================

    print(
        "Testing Dolibarr identity..."
    )

    result = resolver.resolve_external(
        source_type="dolibarr",
        source_id="DOLIBARR",
        identifier="TB-P1648-A12467",
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # TEST UNKNOWN
    # ========================================================

    print(
        "Testing unknown article..."
    )

    result = resolver.resolve_external(
        source_type="moneyworks",
        source_id="GENSOFT-MONEYWORK",
        identifier="UNKNOWN-123",
    )

    print(
        result.to_dict()
    )

    print()

    # ========================================================
    # VALIDATION
    # ========================================================

    errors = resolver.validate()

    if errors:

        print(
            "VALIDATION ERRORS:"
        )

        for error in errors:

            print(
                f"ERROR: {error}"
            )

    else:

        print(
            "Identity mappings: VALID"
        )

    print()

    print(
        "========================================"
    )
    print(
        "Identity Resolver test completed."
    )
    print(
        "========================================"
    )
