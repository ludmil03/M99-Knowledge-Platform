#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Importer Engine v0.1

Purpose
-------
Imports external product/article records into the M99 identity pipeline.

The importer DOES NOT automatically create or modify Product Master data.

Pipeline:

    External Data
         ↓
    Normalize
         ↓
    Identity Resolver
         ↓
    Product Matcher
         ↓
    Decision Engine
         ↓
    Operator Override
         ↓
    Final M99 Identity

Supported external sources
---------------------------
- moneywork
- dolibarr
- supplier
- manufacturer
- other

Important
---------
MoneyWork records are expected to contain limited information:

    code
    name
    size
    color

Size and/or color may be missing.

The importer therefore treats missing information as UNKNOWN,
not as an error.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMPORT_FOLDER = PROJECT_ROOT / "imports"
IMPORT_FOLDER.mkdir(exist_ok=True)

IMPORT_RESULTS_FOLDER = PROJECT_ROOT / "output" / "imports"
IMPORT_RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

ENGINE_VERSION = "0.1"


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any) -> str:
    """
    Normalize arbitrary input into clean text.

    None / empty values become "".
    Multiple spaces are collapsed.
    """
    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    value = re.sub(r"\s+", " ", value)

    return value


def normalize_identifier(value: Any) -> str:
    """
    Normalize external identifiers.

    Example:

        " 06100288 " -> "06100288"
    """
    return clean_text(value)


def normalize_size(value: Any) -> Optional[str]:
    """
    Normalize product size.

    Examples:

        40 -> "40"
        " 40 " -> "40"
        "EU 40" -> "40"
        "" -> None
    """

    value = clean_text(value)

    if not value:
        return None

    value_upper = value.upper()

    value_upper = value_upper.replace("EU ", "")
    value_upper = value_upper.replace("SIZE ", "")

    return value_upper.strip()


def normalize_color(value: Any) -> Optional[str]:
    """
    Normalize product color.

    Examples:

        "Black" -> "black"
        " BLACK " -> "black"
        "" -> None
    """

    value = clean_text(value)

    if not value:
        return None

    return value.lower()


def normalize_name(value: Any) -> str:
    """
    Normalize product name while preserving useful words.
    """

    value = clean_text(value)

    if not value:
        return ""

    value = value.lower()

    # Replace common separators with spaces
    value = value.replace("-", " ")
    value = value.replace("_", " ")
    value = value.replace("/", " ")

    # Collapse spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# EXTERNAL RECORD
# ============================================================

class ExternalProductRecord:
    """
    Standard internal representation of an imported external record.

    This is NOT an M99 Product Master.

    It represents what the external system knows.
    """

    def __init__(
        self,
        source_type: str,
        source_id: str,
        identifier: str,
        name: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        ean: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.source_type = clean_text(source_type).lower()
        self.source_id = clean_text(source_id)

        self.identifier = normalize_identifier(identifier)

        self.name = clean_text(name)

        self.size = normalize_size(size)
        self.color = normalize_color(color)

        self.ean = clean_text(ean) or None

        self.raw = raw or {}

    # --------------------------------------------------------
    # Dictionary representation
    # --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "identifier": self.identifier,
            "name": self.name,
            "attributes": {
                "size": self.size,
                "color": self.color,
            },
            "ean": self.ean,
            "raw": self.raw,
        }

    # --------------------------------------------------------
    # Debug representation
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ExternalProductRecord("
            f"source_type={self.source_type!r}, "
            f"identifier={self.identifier!r}, "
            f"name={self.name!r}, "
            f"size={self.size!r}, "
            f"color={self.color!r})"
        )


# ============================================================
# IMPORTER
# ============================================================

class ProductImporter:
    """
    Main M99 Importer.

    Responsibilities
    ----------------
    1. Read external files.
    2. Normalize external records.
    3. Convert them to a common M99 external representation.
    4. Produce import records for Resolver / Matcher / Decision.
    5. Never silently overwrite M99 identity.
    """

    SUPPORTED_SOURCES = {
        "moneywork",
        "dolibarr",
        "supplier",
        "manufacturer",
        "external",
    }

    def __init__(
        self,
        project_root: Path = PROJECT_ROOT,
    ):
        self.project_root = Path(project_root)

        self.import_folder = (
            self.project_root / "imports"
        )

        self.output_folder = (
            self.project_root
            / "output"
            / "imports"
        )

        self.import_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # SOURCE VALIDATION
    # ========================================================

    def validate_source_type(
        self,
        source_type: str,
    ) -> str:

        source_type = clean_text(
            source_type
        ).lower()

        if source_type not in self.SUPPORTED_SOURCES:

            raise ValueError(
                f"Unsupported source type: "
                f"{source_type}"
            )

        return source_type

    # ========================================================
    # NORMALIZE ONE RECORD
    # ========================================================

    def normalize_record(
        self,
        source_type: str,
        source_id: str,
        record: Dict[str, Any],
    ) -> ExternalProductRecord:

        source_type = self.validate_source_type(
            source_type
        )

        # ----------------------------------------------------
        # Identifier
        # ----------------------------------------------------

        identifier = (
            record.get("code")
            or record.get("sku")
            or record.get("identifier")
            or record.get("product_code")
            or record.get("external_identifier")
            or ""
        )

        # ----------------------------------------------------
        # Name
        # ----------------------------------------------------

        name = (
            record.get("name")
            or record.get("product_name")
            or record.get("description")
            or ""
        )

        # ----------------------------------------------------
        # Size
        # ----------------------------------------------------

        size = (
            record.get("size")
            or record.get("Size")
            or record.get("размер")
            or record.get("Размер")
        )

        # ----------------------------------------------------
        # Color
        # ----------------------------------------------------

        color = (
            record.get("color")
            or record.get("Color")
            or record.get("цвят")
            or record.get("Цвят")
        )

        # ----------------------------------------------------
        # EAN
        # ----------------------------------------------------

        ean = (
            record.get("ean")
            or record.get("EAN")
            or record.get("barcode")
            or record.get("bar_code")
        )

        return ExternalProductRecord(
            source_type=source_type,
            source_id=source_id,
            identifier=identifier,
            name=name,
            size=size,
            color=color,
            ean=ean,
            raw=record,
        )

    # ========================================================
    # NORMALIZE LIST
    # ========================================================

    def normalize_records(
        self,
        source_type: str,
        source_id: str,
        records: List[Dict[str, Any]],
    ) -> List[ExternalProductRecord]:

        normalized = []

        for record in records:

            if not isinstance(record, dict):
                continue

            normalized.append(
                self.normalize_record(
                    source_type=source_type,
                    source_id=source_id,
                    record=record,
                )
            )

        return normalized

    # ========================================================
    # LOAD JSON
    # ========================================================

    def load_json(
        self,
        file_path: Path,
    ) -> List[Dict[str, Any]]:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Import file not found:\n"
                f"{file_path}"
            )

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        # ----------------------------------------------------
        # Supported JSON formats
        # ----------------------------------------------------

        if isinstance(data, list):

            return data

        if isinstance(data, dict):

            if isinstance(
                data.get("products"),
                list,
            ):
                return data["products"]

            if isinstance(
                data.get("items"),
                list,
            ):
                return data["items"]

            if isinstance(
                data.get("records"),
                list,
            ):
                return data["records"]

            # Single product record
            return [data]

        raise ValueError(
            "Unsupported JSON structure."
        )

    # ========================================================
    # LOAD CSV
    # ========================================================

    def load_csv(
        self,
        file_path: Path,
    ) -> List[Dict[str, Any]]:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Import file not found:\n"
                f"{file_path}"
            )

        records = []

        # utf-8-sig handles Excel-generated CSV
        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:
                records.append(
                    dict(row)
                )

        return records

    # ========================================================
    # LOAD FILE AUTOMATICALLY
    # ========================================================

    def load_file(
        self,
        source_type: str,
        source_id: str,
        file_path: Path,
    ) -> List[ExternalProductRecord]:

        file_path = Path(file_path)

        suffix = file_path.suffix.lower()

        print(
            f"Loading {file_path.name}"
        )

        if suffix == ".json":

            records = self.load_json(
                file_path
            )

        elif suffix == ".csv":

            records = self.load_csv(
                file_path
            )

        else:

            raise ValueError(
                f"Unsupported file type: "
                f"{suffix}"
            )

        return self.normalize_records(
            source_type=source_type,
            source_id=source_id,
            records=records,
        )

    # ========================================================
    # CREATE IMPORT PACKAGE
    # ========================================================

    def create_import_package(
        self,
        records: List[ExternalProductRecord],
    ) -> Dict[str, Any]:

        return {
            "engine": "M99 Knowledge Platform",
            "engine_version": ENGINE_VERSION,
            "imported_at": utc_now(),

            "record_count": len(records),

            "records": [
                record.to_dict()
                for record in records
            ],
        }

    # ========================================================
    # SAVE IMPORT PACKAGE
    # ========================================================

    def save_import_package(
        self,
        package: Dict[str, Any],
        filename: str,
    ) -> Path:

        output_file = (
            self.output_folder
            / filename
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                package,
                f,
                ensure_ascii=False,
                indent=2,
            )

        return output_file


# ============================================================
# REAL PRODUCT TEST
# ============================================================

def run_test() -> None:

    print(
        "========================================"
    )
    print(
        "M99 Knowledge Platform"
    )
    print(
        "Importer Engine v0.1"
    )
    print(
        "========================================"
    )
    print()

    importer = ProductImporter()

    # --------------------------------------------------------
    # REALISTIC MONEYWORK RECORD
    # --------------------------------------------------------
    #
    # This deliberately contains only the information
    # MoneyWork normally has.
    #

    moneywork_record = {
        "code": "MW-0001842",

        "name": (
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),

        "size": "40",

        "color": "Black",
    }

    print(
        "Testing real MoneyWork-style record..."
    )
    print()

    product = importer.normalize_record(
        source_type="moneywork",
        source_id="GENSOFT-MONEYWORK",
        record=moneywork_record,
    )

    print(
        json.dumps(
            product.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
    )

    print()

    # --------------------------------------------------------
    # PACKAGE
    # --------------------------------------------------------

    package = importer.create_import_package(
        [product]
    )

    output_file = importer.save_import_package(
        package,
        "test_moneywork_import.json",
    )

    print(
        "Import package created:"
    )

    print(output_file)

    print()

    # --------------------------------------------------------
    # SECOND TEST
    # --------------------------------------------------------
    #
    # MoneyWork may have size only.
    #

    size_only_record = {
        "code": "MW-0001843",

        "name": (
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),

        "size": "41",
    }

    print(
        "Testing size-only MoneyWork record..."
    )
    print()

    product_2 = importer.normalize_record(
        source_type="moneywork",
        source_id="GENSOFT-MONEYWORK",
        record=size_only_record,
    )

    print(
        json.dumps(
            product_2.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
    )

    print()

    # --------------------------------------------------------
    # THIRD TEST
    # --------------------------------------------------------
    #
    # MoneyWork may have color only.
    #

    color_only_record = {
        "code": "MW-0001844",

        "name": (
            "Работни обувки PUMA VELOCITY "
            "2.0 BLACK LOW S3 ESD"
        ),

        "color": "Black",
    }

    print(
        "Testing color-only MoneyWork record..."
    )
    print()

    product_3 = importer.normalize_record(
        source_type="moneywork",
        source_id="GENSOFT-MONEYWORK",
        record=color_only_record,
    )

    print(
        json.dumps(
            product_3.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
    )

    print()

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print(
        "========================================"
    )
    print(
        "Importer Engine test completed."
    )
    print(
        "========================================"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_test()
