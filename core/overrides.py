#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Operator Override Engine v0.1

Purpose:
    Allows an operator to manually correct or confirm
    automatic M99 identity decisions.

Architecture:

    External Source
          |
          v
    Identity Resolver
          |
          v
    Product Matcher
          |
          v
    Decision Engine
          |
          v
    Operator Override
          |
          v
    FINAL M99 IDENTITY

Important:
    Operator overrides NEVER modify the automatic decision.
    They are stored as a separate authoritative layer.

Author: M99 Knowledge Platform
"""

import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OVERRIDES_FOLDER = PROJECT_ROOT / "knowledge" / "overrides"
OVERRIDES_FILE = OVERRIDES_FOLDER / "overrides.json"

OVERRIDES_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONSTANTS
# ============================================================

VALID_ACTIONS = {
    "CONFIRM",
    "REJECT",
    "REMAP_PRODUCT",
    "REMAP_VARIANT",
    "IGNORE",
}

ACTIVE_STATUS = "active"
REVOKED_STATUS = "revoked"


# ============================================================
# HELPERS
# ============================================================

def utc_now():
    """
    Returns current UTC timestamp in ISO 8601 format.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize(value):
    """
    Normalizes identifiers and strings.
    """
    if value is None:
        return None

    return str(value).strip()


# ============================================================
# OVERRIDE ENGINE
# ============================================================

class OverrideEngine:
    """
    Manages operator overrides for M99 identity decisions.
    """

    def __init__(self, overrides_file=OVERRIDES_FILE):
        self.overrides_file = Path(overrides_file)
        self.overrides_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.data = self._load()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    def _load(self):
        """
        Loads overrides from JSON file.

        If the file does not exist, an empty structure is
        created.
        """

        if not self.overrides_file.exists():
            return {
                "version": "0.1.0",
                "overrides": []
            }

        try:
            with open(
                self.overrides_file,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid overrides JSON: {self.overrides_file}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "Override file root must be an object."
            )

        data.setdefault("version", "0.1.0")
        data.setdefault("overrides", [])

        if not isinstance(data["overrides"], list):
            raise ValueError(
                "'overrides' must be a list."
            )

        return data

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def _save(self):
        """
        Saves override database.
        """

        with open(
            self.overrides_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                ensure_ascii=False,
                indent=2
            )

    # --------------------------------------------------------
    # ID GENERATION
    # --------------------------------------------------------

    def _next_override_id(self):
        """
        Generates sequential M99 override IDs.

        Example:
            OVR-000001
            OVR-000002
            OVR-000003
        """

        highest = 0

        for override in self.data["overrides"]:

            override_id = override.get(
                "override_id",
                ""
            )

            if not override_id.startswith("OVR-"):
                continue

            try:
                number = int(
                    override_id.replace(
                        "OVR-",
                        ""
                    )
                )

                highest = max(
                    highest,
                    number
                )

            except ValueError:
                continue

        return f"OVR-{highest + 1:06d}"

    # --------------------------------------------------------
    # FIND
    # --------------------------------------------------------

    def _find_active_override(
        self,
        source_type,
        external_identifier
    ):
        """
        Finds active override for an external article.
        """

        source_type = normalize(source_type)
        external_identifier = normalize(
            external_identifier
        )

        for override in self.data["overrides"]:

            if override.get("status") != ACTIVE_STATUS:
                continue

            if override.get("source_type") != source_type:
                continue

            if (
                override.get("external_identifier")
                != external_identifier
            ):
                continue

            return override

        return None

    # --------------------------------------------------------
    # HAS OVERRIDE
    # --------------------------------------------------------

    def has_override(
        self,
        source_type,
        external_identifier
    ):
        """
        Returns True when an active operator override exists.
        """

        return (
            self._find_active_override(
                source_type,
                external_identifier
            )
            is not None
        )

    # --------------------------------------------------------
    # GET OVERRIDE
    # --------------------------------------------------------

    def get_override(
        self,
        source_type,
        external_identifier
    ):
        """
        Returns active override or None.
        """

        return self._find_active_override(
            source_type,
            external_identifier
        )

    # --------------------------------------------------------
    # GET FINAL DECISION
    # --------------------------------------------------------

    def resolve(
        self,
        source_type,
        external_identifier,
        automatic_result
    ):
        """
        Resolves the final identity.

        Priority:

            1. Active operator override
            2. Automatic engine decision

        The automatic result is NEVER modified.
        """

        override = self.get_override(
            source_type,
            external_identifier
        )

        if override is None:

            return {
                "source": "automatic",
                "override": None,
                "result": automatic_result
            }

        return {
            "source": "operator_override",
            "override": override,
            "result": override.get(
                "final_identity"
            )
        }

    # --------------------------------------------------------
    # CREATE OVERRIDE
    # --------------------------------------------------------

    def create_override(
        self,
        source_type,
        external_identifier,
        automatic_result,
        action,
        operator,
        reason,
        product_id=None,
        variant_id=None,
        notes=None
    ):
        """
        Creates a new operator override.

        Actions:

            CONFIRM
            REJECT
            REMAP_PRODUCT
            REMAP_VARIANT
            IGNORE
        """

        source_type = normalize(source_type)
        external_identifier = normalize(
            external_identifier
        )
        action = normalize(action)
        operator = normalize(operator)
        reason = normalize(reason)

        if not source_type:
            raise ValueError(
                "source_type is required."
            )

        if not external_identifier:
            raise ValueError(
                "external_identifier is required."
            )

        if action not in VALID_ACTIONS:
            raise ValueError(
                f"Invalid action '{action}'. "
                f"Allowed: {sorted(VALID_ACTIONS)}"
            )

        if not operator:
            raise ValueError(
                "operator is required."
            )

        if not reason:
            raise ValueError(
                "reason is required."
            )

        if action in {
            "CONFIRM",
            "REMAP_PRODUCT",
            "REMAP_VARIANT"
        }:

            if not product_id:
                raise ValueError(
                    f"{action} requires product_id."
                )

        if action == "REMAP_VARIANT":

            if not variant_id:
                raise ValueError(
                    "REMAP_VARIANT requires variant_id."
                )

        # ----------------------------------------------------
        # Prevent duplicate active overrides
        # ----------------------------------------------------

        existing = self._find_active_override(
            source_type,
            external_identifier
        )

        if existing is not None:
            raise ValueError(
                "An active override already exists for "
                f"{source_type}:{external_identifier}. "
                f"Override: {existing['override_id']}"
            )

        override_id = self._next_override_id()

        # ----------------------------------------------------
        # Final identity
        # ----------------------------------------------------

        if action == "REJECT":

            final_identity = {
                "status": "rejected",
                "product_id": None,
                "variant_id": None
            }

        elif action == "IGNORE":

            final_identity = {
                "status": "ignored",
                "product_id": None,
                "variant_id": None
            }

        else:

            final_identity = {
                "status": "confirmed",
                "product_id": product_id,
                "variant_id": variant_id
            }

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------

        override = {

            "override_id": override_id,

            "source_type": source_type,

            "external_identifier":
                external_identifier,

            "automatic_decision":
                automatic_result,

            "operator_decision": {

                "action": action,

                "operator": operator,

                "reason": reason,

                "notes": notes

            },

            "final_identity":
                final_identity,

            "status":
                ACTIVE_STATUS,

            "created_at":
                utc_now(),

            "updated_at":
                utc_now()

        }

        self.data["overrides"].append(
            override
        )

        self._save()

        return override

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    def confirm(
        self,
        source_type,
        external_identifier,
        automatic_result,
        operator,
        reason,
        product_id,
        variant_id=None,
        notes=None
    ):
        """
        Operator confirms or corrects an identity.
        """

        return self.create_override(
            source_type=source_type,
            external_identifier=external_identifier,
            automatic_result=automatic_result,
            action="CONFIRM",
            operator=operator,
            reason=reason,
            product_id=product_id,
            variant_id=variant_id,
            notes=notes
        )

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    def reject(
        self,
        source_type,
        external_identifier,
        automatic_result,
        operator,
        reason,
        notes=None
    ):
        """
        Operator rejects automatic identity.
        """

        return self.create_override(
            source_type=source_type,
            external_identifier=external_identifier,
            automatic_result=automatic_result,
            action="REJECT",
            operator=operator,
            reason=reason,
            notes=notes
        )

    # --------------------------------------------------------
    # REMAP PRODUCT
    # --------------------------------------------------------

    def remap_product(
        self,
        source_type,
        external_identifier,
        automatic_result,
        operator,
        reason,
        product_id,
        notes=None
    ):
        """
        Moves external article to another M99 Product Master.
        """

        return self.create_override(
            source_type=source_type,
            external_identifier=external_identifier,
            automatic_result=automatic_result,
            action="REMAP_PRODUCT",
            operator=operator,
            reason=reason,
            product_id=product_id,
            variant_id=None,
            notes=notes
        )

    # --------------------------------------------------------
    # REMAP VARIANT
    # --------------------------------------------------------

    def remap_variant(
        self,
        source_type,
        external_identifier,
        automatic_result,
        operator,
        reason,
        product_id,
        variant_id,
        notes=None
    ):
        """
        Moves external article to another M99 Variant.
        """

        return self.create_override(
            source_type=source_type,
            external_identifier=external_identifier,
            automatic_result=automatic_result,
            action="REMAP_VARIANT",
            operator=operator,
            reason=reason,
            product_id=product_id,
            variant_id=variant_id,
            notes=notes
        )

    # --------------------------------------------------------
    # IGNORE
    # --------------------------------------------------------

    def ignore(
        self,
        source_type,
        external_identifier,
        automatic_result,
        operator,
        reason,
        notes=None
    ):
        """
        Marks external article as intentionally ignored.
        """

        return self.create_override(
            source_type=source_type,
            external_identifier=external_identifier,
            automatic_result=automatic_result,
            action="IGNORE",
            operator=operator,
            reason=reason,
            notes=notes
        )

    # --------------------------------------------------------
    # REVOKE
    # --------------------------------------------------------

    def revoke(
        self,
        override_id,
        operator,
        reason
    ):
        """
        Revokes an existing override.

        Important:
            We do NOT delete history.
        """

        for override in self.data["overrides"]:

            if override.get(
                "override_id"
            ) != override_id:
                continue

            if override.get(
                "status"
            ) != ACTIVE_STATUS:

                raise ValueError(
                    f"Override {override_id} "
                    "is not active."
                )

            override["status"] = REVOKED_STATUS

            override["revocation"] = {

                "operator": operator,

                "reason": reason,

                "revoked_at": utc_now()

            }

            override["updated_at"] = utc_now()

            self._save()

            return override

        raise ValueError(
            f"Override not found: {override_id}"
        )

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def list_overrides(
        self,
        status=None
    ):
        """
        Returns override records.

        Optional status filter:
            active
            revoked
        """

        if status is None:
            return list(
                self.data["overrides"]
            )

        return [
            override
            for override in self.data["overrides"]
            if override.get("status") == status
        ]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("M99 Knowledge Platform")
    print("Operator Override Engine v0.1")
    print("========================================")
    print()

    engine = OverrideEngine()

    automatic_result = {

        "status": "REVIEW",

        "decision_code": "FINAL_REVIEW",

        "product_id":
            "M99-PM-000001",

        "variant_id":
            None

    }

    print("Creating test override...")
    print()

    test_identifier = "TEST-MW-000001"

    # --------------------------------------------------------
    # Remove previous test override if necessary
    # --------------------------------------------------------

    existing = engine.get_override(
        "moneywork",
        test_identifier
    )

    if existing:

        engine.revoke(
            existing["override_id"],
            "TEST",
            "Reset test override."
        )

    # --------------------------------------------------------
    # Create override
    # --------------------------------------------------------

    override = engine.confirm(

        source_type="moneywork",

        external_identifier=
            test_identifier,

        automatic_result=
            automatic_result,

        operator="TEST",

        reason=
            "Operator confirmed the correct M99 identity.",

        product_id=
            "M99-PM-000001",

        variant_id=
            "M99-PV-000001",

        notes=
            "Test override."
    )

    print("Override created:")
    print()

    print(
        json.dumps(
            override,
            ensure_ascii=False,
            indent=2
        )
    )

    print()

    # --------------------------------------------------------
    # Resolve
    # --------------------------------------------------------

    print("Testing final resolution...")
    print()

    result = engine.resolve(

        source_type="moneywork",

        external_identifier=
            test_identifier,

        automatic_result=
            automatic_result
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )

    print()

    # --------------------------------------------------------
    # Test has_override
    # --------------------------------------------------------

    print("Testing has_override()...")
    print()

    print(
        engine.has_override(
            "moneywork",
            test_identifier
        )
    )

    print()

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    print("Active overrides:")
    print()

    active = engine.list_overrides(
        status="active"
    )

    print(
        json.dumps(
            active,
            ensure_ascii=False,
            indent=2
        )
    )

    print()
    print("========================================")
    print("Override Engine test completed.")
    print("========================================")
