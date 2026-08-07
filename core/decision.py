#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M99 Knowledge Platform
Decision Engine v0.1

Automatic matching NEVER has the final authority.

The Decision Engine:
1. receives matcher results
2. creates an operational decision
3. supports operator corrections
4. stores corrections separately
5. keeps an audit trail

Architecture:

External Source
      ↓
Identity Resolver
      ↓
Matcher
      ↓
Decision Engine
      ↓
AUTO_ACCEPT / REVIEW / REJECT
      ↓
Operator Override
      ↓
Confirmed M99 Mapping
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

OVERRIDES_FILE = DATA_DIR / "decision_overrides.json"
AUDIT_FILE = DATA_DIR / "decision_audit.jsonl"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# STATUS DEFINITIONS
# ============================================================

PRODUCT_AUTO_ACCEPT = {
    "HIGH_CONFIDENCE",
    "CONFIRMED",
}

VARIANT_AUTO_ACCEPT = {
    "HIGH_CONFIDENCE",
    "CONFIRMED",
}

REVIEW_STATUSES = {
    "REVIEW",
    "AMBIGUOUS",
    "NOT_DETERMINED",
}

REJECT_STATUSES = {
    "REJECTED",
}


# ============================================================
# HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    temp = path.with_suffix(path.suffix + ".tmp")

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    temp.replace(path)


def write_audit(event):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                event,
                ensure_ascii=False
            )
            + "\n"
        )


# ============================================================
# DECISION ENGINE
# ============================================================

class DecisionEngine:

    VERSION = "0.1"

    def __init__(self):

        self.overrides = load_json(
            OVERRIDES_FILE,
            {
                "version": self.VERSION,
                "overrides": []
            }
        )

        if "overrides" not in self.overrides:
            self.overrides["overrides"] = []

    # ========================================================
    # MAIN DECISION
    # ========================================================

    def decide(self, match_result):

        external = match_result.get(
            "external",
            {}
        )

        source_type = external.get(
            "source_type"
        )

        source_id = external.get(
            "source_id"
        )

        identifier = external.get(
            "identifier"
        )

        # ----------------------------------------------------
        # FIRST: CHECK OPERATOR OVERRIDE
        # ----------------------------------------------------

        override = self.find_override(
            source_type,
            source_id,
            identifier
        )

        if override:

            return self.apply_override(
                override
            )

        # ----------------------------------------------------
        # OTHERWISE: AUTOMATIC DECISION
        # ----------------------------------------------------

        return self.automatic_decision(
            match_result
        )

    # ========================================================
    # AUTOMATIC DECISION
    # ========================================================

    def automatic_decision(
        self,
        match_result
    ):

        product = match_result.get(
            "product"
        )

        variant = match_result.get(
            "variant"
        )

        if not product:

            return {
                "status": "REJECTED",
                "decision_code": "PRODUCT_REJECTED",
                "action": "REJECT",
                "product_id": None,
                "variant_id": None,
                "source": "automatic",
                "reasons": [
                    "Matcher returned no Product decision."
                ]
            }

        product_status = product.get(
            "status",
            "REVIEW"
        )

        variant_status = (
            variant.get("status")
            if variant
            else "NOT_DETERMINED"
        )

        product_id = product.get(
            "product_id"
        )

        variant_id = (
            variant.get("variant_id")
            if variant
            else None
        )

        # ----------------------------------------------------
        # PRODUCT REJECTED
        # ----------------------------------------------------

        if product_status in REJECT_STATUSES:

            return {
                "status": "REJECTED",
                "decision_code": "PRODUCT_REJECTED",
                "action": "REJECT",
                "product_id": None,
                "variant_id": None,
                "source": "automatic",
                "reasons": [
                    "Product identity rejected."
                ]
            }

        # ----------------------------------------------------
        # PRODUCT REVIEW
        # ----------------------------------------------------

        if product_status in REVIEW_STATUSES:

            return {
                "status": "REVIEW",
                "decision_code": "PRODUCT_REVIEW",
                "action": "REVIEW_REQUIRED",
                "product_id": product_id,
                "variant_id": variant_id,
                "source": "automatic",
                "reasons": [
                    "Product identity requires operator review."
                ]
            }

        # ----------------------------------------------------
        # VARIANT REJECTED
        # ----------------------------------------------------

        if variant_status in REJECT_STATUSES:

            return {
                "status": "REVIEW",
                "decision_code": "VARIANT_REJECTED_REVIEW",
                "action": "REVIEW_REQUIRED",
                "product_id": product_id,
                "variant_id": None,
                "source": "automatic",
                "reasons": [
                    "Requested variant does not exist."
                ]
            }

        # ----------------------------------------------------
        # VARIANT NOT DETERMINED
        # ----------------------------------------------------

        if variant_status == "NOT_DETERMINED":

            return {
                "status": "REVIEW",
                "decision_code": "VARIANT_NOT_DETERMINED",
                "action": "REVIEW_REQUIRED",
                "product_id": product_id,
                "variant_id": None,
                "source": "automatic",
                "reasons": [
                    "No size or color information."
                ]
            }

        # ----------------------------------------------------
        # VARIANT AMBIGUOUS
        # ----------------------------------------------------

        if variant_status == "AMBIGUOUS":

            return {
                "status": "REVIEW",
                "decision_code": "VARIANT_AMBIGUOUS",
                "action": "REVIEW_REQUIRED",
                "product_id": product_id,
                "variant_id": None,
                "source": "automatic",
                "reasons": [
                    "Multiple variants match."
                ]
            }

        # ----------------------------------------------------
        # PRODUCT + VARIANT CONFIRMED
        # ----------------------------------------------------

        if (
            product_status in PRODUCT_AUTO_ACCEPT
            and
            variant_status in VARIANT_AUTO_ACCEPT
        ):

            return {
                "status": "CONFIRMED",
                "decision_code": "PRODUCT_VARIANT_CONFIRMED",
                "action": "AUTO_ACCEPT",
                "product_id": product_id,
                "variant_id": variant_id,
                "source": "automatic",
                "reasons": [
                    "Product identity has sufficient confidence.",
                    "Variant identity has sufficient confidence."
                ]
            }

        # ----------------------------------------------------
        # SAFE DEFAULT
        # ----------------------------------------------------

        return {
            "status": "REVIEW",
            "decision_code": "DEFAULT_REVIEW",
            "action": "REVIEW_REQUIRED",
            "product_id": product_id,
            "variant_id": variant_id,
            "source": "automatic",
            "reasons": [
                "Decision could not be safely automated."
            ]
        }

    # ========================================================
    # FIND OVERRIDE
    # ========================================================

    def find_override(
        self,
        source_type,
        source_id,
        identifier
    ):

        for override in self.overrides.get(
            "overrides",
            []
        ):

            if not override.get(
                "active",
                True
            ):
                continue

            if (
                override.get("source_type")
                == source_type
                and
                override.get("source_id")
                == source_id
                and
                override.get("identifier")
                == identifier
            ):

                return override

        return None

    # ========================================================
    # OPERATOR CORRECTION
    # ========================================================

    def add_override(
        self,
        source_type,
        source_id,
        identifier,
        product_id=None,
        variant_id=None,
        status="CONFIRMED",
        reason="",
        operator="operator"
    ):

        if not source_type:
            raise ValueError(
                "source_type is required."
            )

        if not source_id:
            raise ValueError(
                "source_id is required."
            )

        if not identifier:
            raise ValueError(
                "identifier is required."
            )

        if not product_id and not variant_id:

            raise ValueError(
                "product_id or variant_id is required."
            )

        if status not in {
            "CONFIRMED",
            "REVIEW",
            "REJECTED"
        }:

            raise ValueError(
                "Invalid override status."
            )

        existing = self.find_override(
            source_type,
            source_id,
            identifier
        )

        now = utc_now()

        if existing:

            old_data = dict(existing)

            existing.update({

                "product_id": product_id,
                "variant_id": variant_id,
                "status": status,
                "reason": reason,
                "operator": operator,
                "updated_at": now,
                "active": True

            })

            override_id = existing[
                "override_id"
            ]

            event_type = "UPDATE_OVERRIDE"

        else:

            override_id = (
                "OVR-"
                + uuid.uuid4()
                .hex[:12]
                .upper()
            )

            new_override = {

                "override_id": override_id,

                "source_type": source_type,

                "source_id": source_id,

                "identifier": identifier,

                "product_id": product_id,

                "variant_id": variant_id,

                "status": status,

                "reason": reason,

                "operator": operator,

                "created_at": now,

                "updated_at": now,

                "active": True

            }

            self.overrides[
                "overrides"
            ].append(
                new_override
            )

            event_type = "CREATE_OVERRIDE"

            old_data = None

        save_json(
            OVERRIDES_FILE,
            self.overrides
        )

        write_audit({

            "event_id":
                "AUD-"
                + uuid.uuid4()
                .hex[:12]
                .upper(),

            "event":
                event_type,

            "timestamp":
                now,

            "operator":
                operator,

            "source_type":
                source_type,

            "source_id":
                source_id,

            "identifier":
                identifier,

            "product_id":
                product_id,

            "variant_id":
                variant_id,

            "status":
                status,

            "reason":
                reason,

            "previous":
                old_data

        })

        return self.find_override(
            source_type,
            source_id,
            identifier
        )

    # ========================================================
    # REMOVE / DEACTIVATE OVERRIDE
    # ========================================================

    def remove_override(
        self,
        source_type,
        source_id,
        identifier,
        operator="operator",
        reason=""
    ):

        override = self.find_override(
            source_type,
            source_id,
            identifier
        )

        if not override:
            return False

        override["active"] = False

        override["updated_at"] = utc_now()

        save_json(
            OVERRIDES_FILE,
            self.overrides
        )

        write_audit({

            "event_id":
                "AUD-"
                + uuid.uuid4()
                .hex[:12]
                .upper(),

            "event":
                "DEACTIVATE_OVERRIDE",

            "timestamp":
                utc_now(),

            "operator":
                operator,

            "source_type":
                source_type,

            "source_id":
                source_id,

            "identifier":
                identifier,

            "reason":
                reason

        })

        return True

    # ========================================================
    # APPLY OPERATOR DECISION
    # ========================================================

    def apply_override(
        self,
        override
    ):

        status = override.get(
            "status",
            "CONFIRMED"
        )

        if status == "CONFIRMED":

            action = "OPERATOR_ACCEPT"

            decision_code = (
                "OPERATOR_CONFIRMED"
            )

        elif status == "REVIEW":

            action = "REVIEW_REQUIRED"

            decision_code = (
                "OPERATOR_REVIEW"
            )

        else:

            action = "REJECT"

            decision_code = (
                "OPERATOR_REJECTED"
            )

        return {

            "status": status,

            "decision_code":
                decision_code,

            "action":
                action,

            "product_id":
                override.get(
                    "product_id"
                ),

            "variant_id":
                override.get(
                    "variant_id"
                ),

            "source":
                "operator_override",

            "override_id":
                override.get(
                    "override_id"
                ),

            "operator":
                override.get(
                    "operator"
                ),

            "reason":
                override.get(
                    "reason"
                ),

            "reasons": [

                "Operator override has priority "
                "over automatic matching."

            ]

        }


# ============================================================
# TEST
# ============================================================

def test():

    print("=" * 60)
    print("M99 Knowledge Platform")
    print("Decision Engine v0.1")
    print("=" * 60)
    print()

    engine = DecisionEngine()

    # --------------------------------------------------------
    # Example MoneyWork article
    # --------------------------------------------------------

    match_result = {

        "external": {

            "source_type":
                "moneywork",

            "source_id":
                "GENSOFT-MONEYWORK",

            "identifier":
                "MW-0001842"

        },

        "product": {

            "status":
                "REVIEW",

            "score":
                45.0,

            "product_id":
                "M99-PM-000001"

        },

        "variant": {

            "status":
                "CONFIRMED",

            "score":
                100.0,

            "variant_id":
                "M99-PV-000001"

        }

    }

    # --------------------------------------------------------
    # AUTOMATIC
    # --------------------------------------------------------

    print(
        "AUTOMATIC DECISION"
    )

    print("-" * 60)

    result = engine.decide(
        match_result
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
    # OPERATOR
    # --------------------------------------------------------

    print(
        "OPERATOR CORRECTION"
    )

    print("-" * 60)

    override = engine.add_override(

        source_type=
            "moneywork",

        source_id=
            "GENSOFT-MONEYWORK",

        identifier=
            "MW-0001842",

        product_id=
            "M99-PM-000001",

        variant_id=
            "M99-PV-000001",

        status=
            "CONFIRMED",

        reason=
            "Operator verified the legacy article.",

        operator=
            "admin"

    )

    print(
        json.dumps(
            override,
            ensure_ascii=False,
            indent=2
        )
    )

    print()

    # --------------------------------------------------------
    # AFTER OPERATOR
    # --------------------------------------------------------

    print(
        "DECISION AFTER OPERATOR CORRECTION"
    )

    print("-" * 60)

    corrected = engine.decide(
        match_result
    )

    print(
        json.dumps(
            corrected,
            ensure_ascii=False,
            indent=2
        )
    )

    print()

    print("=" * 60)
    print(
        "Decision Engine test completed."
    )
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    test()
