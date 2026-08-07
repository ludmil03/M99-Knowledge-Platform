#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
core.validator

Validates a loaded Gold Master product.

Validator v0.1
"""

from pathlib import Path
from typing import Any, Dict, List


class ValidationError(Exception):
    """Raised when a product cannot be validated."""
    pass


class ProductValidator:

    # =================================================
    # CONFIGURATION
    # =================================================

    REQUIRED_MANIFEST_FIELDS = [
        "knowledge_id",
        "product_id",
        "version",
    ]

    REQUIRED_PRODUCT_OBJECTS = [
        "identity",
        "specifications",
        "materials",
        "technologies",
        "standards",
        "applications",
        "certifications",
    ]

    # =================================================
    # INITIALIZATION
    # =================================================

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    # =================================================
    # RESET
    # =================================================

    def reset(self):
        """Reset validation results."""

        self.errors = []
        self.warnings = []

    # =================================================
    # BASIC HELPERS
    # =================================================

    def error(self, message: str):
        """Register validation error."""

        self.errors.append(message)

    def warning(self, message: str):
        """Register validation warning."""

        self.warnings.append(message)

    # =================================================
    # MANIFEST VALIDATION
    # =================================================

    def validate_manifest(
        self,
        manifest: Dict[str, Any]
    ):
        """
        Validate product.json manifest.
        """

        if not isinstance(manifest, dict):

            self.error(
                "product.json must contain a JSON object."
            )

            return

        # ---------------------------------------------
        # Required fields
        # ---------------------------------------------

        for field in self.REQUIRED_MANIFEST_FIELDS:

            value = manifest.get(field)

            if value is None or value == "":

                self.error(
                    f"product.json: missing required field "
                    f"'{field}'."
                )

        # ---------------------------------------------
        # Product ID
        # ---------------------------------------------

        product_id = manifest.get("product_id")

        if product_id:

            if not isinstance(product_id, str):

                self.error(
                    "product.json: product_id must be a string."
                )

        # ---------------------------------------------
        # Version
        # ---------------------------------------------

        version = manifest.get("version")

        if version:

            if not isinstance(version, str):

                self.error(
                    "product.json: version must be a string."
                )

    # =================================================
    # OBJECT VALIDATION
    # =================================================

    def validate_objects(
        self,
        product: Dict[str, Any]
    ):
        """
        Validate required Knowledge Objects.
        """

        for object_name in self.REQUIRED_PRODUCT_OBJECTS:

            if object_name not in product:

                self.error(
                    f"Missing Knowledge Object: "
                    f"{object_name}"
                )

                continue

            value = product[object_name]

            if value is None:

                self.error(
                    f"Knowledge Object '{object_name}' "
                    f"is null."
                )

            elif not isinstance(
                value,
                (dict, list)
            ):

                self.error(
                    f"Knowledge Object '{object_name}' "
                    f"must be a JSON object or array."
                )

    # =================================================
    # IDENTITY VALIDATION
    # =================================================

    def validate_identity(
        self,
        identity: Dict[str, Any]
    ):
        """
        Validate product identity.
        """

        if not isinstance(identity, dict):

            self.error(
                "identity.json must contain a JSON object."
            )

            return

        required_fields = [
            "sku",
            "brand",
            "model",
        ]

        for field in required_fields:

            value = identity.get(field)

            if value is None or value == "":

                self.error(
                    f"identity.json: missing required field "
                    f"'{field}'."
                )

    # =================================================
    # CONTENT VALIDATION
    # =================================================

    def validate_content(
        self,
        content: Dict[str, Any]
    ):
        """
        Validate product content.
        """

        if not isinstance(content, dict):

            self.error(
                "content must be a JSON object."
            )

            return

        # Bulgarian content is currently required
        # for M99 product generation.

        if "bg" not in content:

            self.error(
                "content.bg.json is required."
            )

            return

        if content["bg"] is None:

            self.error(
                "content.bg.json is null."
            )

    # =================================================
    # MEDIA VALIDATION
    # =================================================

    def validate_media(
        self,
        media: Dict[str, Any]
    ):
        """
        Validate media section.
        """

        if not isinstance(media, dict):

            self.warning(
                "Media section is missing or invalid."
            )

            return

        if "images" not in media:

            self.warning(
                "images.json is not loaded."
            )

    # =================================================
    # CONSISTENCY VALIDATION
    # =================================================

    def validate_consistency(
        self,
        manifest: Dict[str, Any],
        product: Dict[str, Any]
    ):
        """
        Validate consistency between manifest
        and loaded Knowledge Objects.
        """

        manifest_product_id = manifest.get(
            "product_id"
        )

        if not manifest_product_id:
            return

        # ---------------------------------------------
        # Identity SKU
        # ---------------------------------------------

        identity = product.get(
            "identity",
            {}
        )

        if isinstance(identity, dict):

            sku = identity.get("sku")

            if sku and sku != manifest_product_id:

                self.warning(
                    "identity.json: SKU "
                    f"'{sku}' does not match "
                    f"manifest product_id "
                    f"'{manifest_product_id}'."
                )

    # =================================================
    # FULL VALIDATION
    # =================================================

    def validate(
        self,
        product: Dict[str, Any]
    ) -> bool:
        """
        Validate complete product.

        Returns:
            True  = valid
            False = invalid
        """

        self.reset()

        if not isinstance(product, dict):

            self.error(
                "Product must be a dictionary."
            )

            return False

        # ---------------------------------------------
        # Manifest
        # ---------------------------------------------

        manifest = product.get(
            "manifest"
        )

        if manifest is None:

            self.error(
                "Product manifest is missing."
            )

            return False

        self.validate_manifest(
            manifest
        )

        # ---------------------------------------------
        # Knowledge Objects
        # ---------------------------------------------

        self.validate_objects(
            product
        )

        # ---------------------------------------------
        # Identity
        # ---------------------------------------------

        identity = product.get(
            "identity"
        )

        if identity is not None:

            self.validate_identity(
                identity
            )

        # ---------------------------------------------
        # Content
        # ---------------------------------------------

        content = product.get(
            "content"
        )

        if content is not None:

            self.validate_content(
                content
            )

        # ---------------------------------------------
        # Media
        # ---------------------------------------------

        media = product.get(
            "media"
        )

        if media is not None:

            self.validate_media(
                media
            )

        # ---------------------------------------------
        # Consistency
        # ---------------------------------------------

        self.validate_consistency(
            manifest,
            product
        )

        return len(self.errors) == 0

    # =================================================
    # REPORT
    # =================================================

    def report(self) -> str:
        """
        Generate human-readable validation report.
        """

        lines = []

        lines.append(
            "========================================"
        )

        lines.append(
            "M99 Knowledge Platform"
        )

        lines.append(
            "Product Validation Report"
        )

        lines.append(
            "========================================"
        )

        lines.append("")

        # ---------------------------------------------
        # Errors
        # ---------------------------------------------

        if self.errors:

            lines.append(
                f"ERRORS: {len(self.errors)}"
            )

            lines.append("")

            for index, error in enumerate(
                self.errors,
                start=1
            ):

                lines.append(
                    f"[ERROR {index}] {error}"
                )

            lines.append("")

        else:

            lines.append(
                "ERRORS: 0"
            )

            lines.append("")

        # ---------------------------------------------
        # Warnings
        # ---------------------------------------------

        if self.warnings:

            lines.append(
                f"WARNINGS: {len(self.warnings)}"
            )

            lines.append("")

            for index, warning in enumerate(
                self.warnings,
                start=1
            ):

                lines.append(
                    f"[WARNING {index}] {warning}"
                )

            lines.append("")

        else:

            lines.append(
                "WARNINGS: 0"
            )

            lines.append("")

        # ---------------------------------------------
        # Result
        # ---------------------------------------------

        if self.errors:

            lines.append(
                "RESULT: INVALID"
            )

        else:

            lines.append(
                "RESULT: VALID"
            )

        lines.append("")

        lines.append(
            "========================================"
        )

        return "\n".join(lines)


# =====================================================
# SIMPLE STANDALONE TEST
# =====================================================

if __name__ == "__main__":

    print()
    print(
        "M99 Knowledge Platform"
    )

    print(
        "Validator module"
    )

    print()

    print(
        "This module is designed to be "
        "called by the M99 Engine."
    )

    print()
