from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from integrations.m99eu_prestashop import (
    PrestaShopWebserviceClient,
    build_inactive_product_xml,
    extract_created_product_id,
    load_m99eu_prestashop_config,
    verify_product_readback,
)
from integrations.m99eu_prestashop.publisher import (
    inspect_draft_plan,
    parse_active_language_ids,
)


@dataclass(frozen=True)
class AdminDryRunResult:
    channel: str
    category_id: int
    language_ids: list[str]
    plan: dict[str, object]
    xml_payload: str


@dataclass(frozen=True)
class AdminCreateResult:
    product_id: int
    plan: dict[str, object]
    readback: dict[str, object]
    success: bool


def _client_and_config():
    cfg = load_m99eu_prestashop_config()
    return cfg, PrestaShopWebserviceClient(cfg)


def live_preflight() -> dict[str, object]:
    cfg, client = _client_and_config()
    root = ET.fromstring(client.get_api_root())
    products = root.find(".//api/products")
    language_ids = parse_active_language_ids(client.get_languages())
    return {
        "channel": "m99.eu",
        "api_base": cfg.api_base,
        "test_category_id": cfg.test_category_id,
        "language_ids": language_ids,
        "products_get": products is not None and products.attrib.get("get") == "true",
        "products_post": products is not None and products.attrib.get("post") == "true",
    }


def build_live_dry_run() -> AdminDryRunResult:
    cfg, client = _client_and_config()
    language_ids = parse_active_language_ids(client.get_languages())
    blank = client.get_product_blank_schema()
    xml_payload, plan = build_inactive_product_xml(
        blank,
        language_ids=language_ids,
        category_id=cfg.test_category_id,
    )
    return AdminDryRunResult(
        channel="m99.eu",
        category_id=cfg.test_category_id,
        language_ids=language_ids,
        plan=inspect_draft_plan(plan),
        xml_payload=xml_payload,
    )


def create_inactive_after_ui_confirmation() -> AdminCreateResult:
    cfg, client = _client_and_config()
    root = ET.fromstring(client.get_api_root())
    products = root.find(".//api/products")
    if products is None or products.attrib.get("post") != "true":
        raise RuntimeError("CREATE BLOCKED: products POST permission is missing")

    language_ids = parse_active_language_ids(client.get_languages())
    blank = client.get_product_blank_schema()
    xml_payload, plan = build_inactive_product_xml(
        blank,
        language_ids=language_ids,
        category_id=cfg.test_category_id,
    )

    created_xml = client.create_product(xml_payload)
    product_id = extract_created_product_id(created_xml)
    readback = verify_product_readback(plan, client.get_product(product_id))

    return AdminCreateResult(
        product_id=product_id,
        plan=inspect_draft_plan(plan),
        readback=readback,
        success=bool(readback.get("pass")),
    )


def result_to_dict(result):
    return asdict(result)
