from __future__ import annotations

import json

from integrations.m99eu import (
    M99EUClient,
    build_test_draft_payload,
    load_m99eu_config,
    verify_product_readback,
)


def main() -> int:
    print("=" * 68)
    print("M99EU SANDBOX CREATE DRAFT")
    print("=" * 68)
    print("This will CREATE exactly one WooCommerce product with status=draft.")
    print("It is intended to remain hidden from the public catalog.")
    print()
    answer = input("Type CREATE_DRAFT to continue: ").strip()
    if answer != "CREATE_DRAFT":
        print("Cancelled. Nothing was sent.")
        return 0

    config = load_m99eu_config()
    client = M99EUClient(config)

    print("Running read-only API preflight...")
    preflight = client.preflight()
    if not preflight.get("products_endpoint_readable"):
        print("Preflight failed. Nothing was created.")
        return 2

    payload = build_test_draft_payload()
    print("\nCreating draft...")
    created = client.create_product_draft(payload)

    product_id = created.get("id")
    if not isinstance(product_id, int) or product_id <= 0:
        print("API response did not contain a valid product ID.")
        return 3

    print(f"Draft created. WooCommerce product ID: {product_id}")
    print("Running mandatory read-back verification...")

    actual = client.get_product(product_id)
    checks = verify_product_readback(payload, actual)

    print(json.dumps(checks, indent=2, ensure_ascii=False))
    print()
    print("Created product summary:")
    print(json.dumps(
        {
            "id": actual.get("id"),
            "name": actual.get("name"),
            "sku": actual.get("sku"),
            "status": actual.get("status"),
            "permalink": actual.get("permalink"),
        },
        indent=2,
        ensure_ascii=False,
    ))

    if not checks["pass"]:
        print("\nREAD-BACK VERIFICATION: FAIL")
        return 4

    print("\nREAD-BACK VERIFICATION: PASS")
    print("The product remains DRAFT. No publish action was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
