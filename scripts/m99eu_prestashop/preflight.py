from __future__ import annotations

import xml.etree.ElementTree as ET

from integrations.m99eu_prestashop import (
    PrestaShopWebserviceClient,
    load_m99eu_prestashop_config,
)
from integrations.m99eu_prestashop.publisher import parse_active_language_ids


def main() -> int:
    cfg = load_m99eu_prestashop_config()
    client = PrestaShopWebserviceClient(cfg)

    root = ET.fromstring(client.get_api_root())
    products = root.find(".//api/products")
    if products is None:
        print("PREFLIGHT FAIL: products resource is not visible.")
        return 2
    if products.attrib.get("get") != "true":
        print("PREFLIGHT FAIL: GET permission for products is missing.")
        return 3

    language_ids = parse_active_language_ids(client.get_languages())
    client.get_categories()
    ET.fromstring(client.get_product_blank_schema())

    print("M99EU PRESTASHOP 9 PREFLIGHT: PASS")
    print(f"API base: {cfg.api_base}")
    print(f"Active language IDs: {', '.join(language_ids)}")
    print(f"Configured test category ID: {cfg.test_category_id}")
    print(f"Products GET permission: {products.attrib.get('get')}")
    print(f"Products POST permission: {products.attrib.get('post')}")
    print("No product was created or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
