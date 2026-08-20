from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_test_draft_payload(
    *,
    sku: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    sku = sku or f"M99-API-TEST-{stamp}"
    name = name or f"M99 API Sandbox Test {stamp}"

    return {
        "name": name,
        "type": "simple",
        "status": "draft",
        "catalog_visibility": "hidden",
        "sku": sku,
        "description": (
            "<p>M99 Knowledge Platform API sandbox test. "
            "Draft only; not intended for public publication.</p>"
        ),
        "short_description": (
            "<p>M99 API sandbox test draft.</p>"
        ),
        "manage_stock": False,
        "meta_data": [
            {"key": "_m99_sandbox", "value": "1"},
            {"key": "_m99_source", "value": "M99-Knowledge-Platform"},
        ],
    }


def verify_product_readback(
    expected: dict[str, Any],
    actual: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "id_present": isinstance(actual.get("id"), int) and actual["id"] > 0,
        "status_draft": actual.get("status") == "draft",
        "name_match": actual.get("name") == expected.get("name"),
        "sku_match": actual.get("sku") == expected.get("sku"),
    }
    checks["pass"] = all(checks.values())
    return checks
