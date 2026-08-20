from __future__ import annotations

import xml.etree.ElementTree as ET

from integrations.m99eu_prestashop import (
    PrestaShopWebserviceClient,
    build_inactive_product_xml,
    extract_created_product_id,
    load_m99eu_prestashop_config,
    verify_product_readback,
)
from integrations.m99eu_prestashop.publisher import inspect_draft_plan, parse_active_language_ids


def main() -> int:
    print("=" * 72)
    print("M99EU PRESTASHOP 9 - CREATE INACTIVE SANDBOX PRODUCT")
    print("=" * 72)
    print("This can create exactly ONE product with active=0.")

    if input("Type CREATE_INACTIVE to continue: ").strip() != "CREATE_INACTIVE":
        print("Cancelled. Nothing was sent.")
        return 0

    cfg = load_m99eu_prestashop_config()
    client = PrestaShopWebserviceClient(cfg)

    root = ET.fromstring(client.get_api_root())
    products = root.find(".//api/products")
    if products is None or products.attrib.get("post") != "true":
        print("CREATE BLOCKED: POST permission for products is missing.")
        return 2

    language_ids = parse_active_language_ids(client.get_languages())
    blank = client.get_product_blank_schema()
    xml_body, plan = build_inactive_product_xml(
        blank,
        language_ids=language_ids,
        category_id=cfg.test_category_id,
    )

    print("Planned product:")
    print(inspect_draft_plan(plan))

    if input("Type CREATE_INACTIVE again to send POST: ").strip() != "CREATE_INACTIVE":
        print("Cancelled before POST.")
        return 0

    created_xml = client.create_product(xml_body)
    product_id = extract_created_product_id(created_xml)
    print(f"Inactive product created. PrestaShop product ID: {product_id}")

    checks = verify_product_readback(plan, client.get_product(product_id))
    print(checks)

    if not checks["pass"]:
        print("READ-BACK VERIFICATION: FAIL")
        return 4

    print("READ-BACK VERIFICATION: PASS")
    print("Product remains active=0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
