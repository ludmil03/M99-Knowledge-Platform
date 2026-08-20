from __future__ import annotations

from integrations.m99eu_prestashop import (
    PrestaShopWebserviceClient,
    build_inactive_product_xml,
    load_m99eu_prestashop_config,
)
from integrations.m99eu_prestashop.publisher import inspect_draft_plan, parse_active_language_ids


def main() -> int:
    cfg = load_m99eu_prestashop_config()
    client = PrestaShopWebserviceClient(cfg)

    language_ids = parse_active_language_ids(client.get_languages())
    blank = client.get_product_blank_schema()

    xml_body, plan = build_inactive_product_xml(
        blank,
        language_ids=language_ids,
        category_id=cfg.test_category_id,
    )

    print("M99EU PRESTASHOP DRY RUN")
    print("Nothing is POSTed by this command.")
    print(inspect_draft_plan(plan))
    print("\nXML payload:\n")
    print(xml_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
