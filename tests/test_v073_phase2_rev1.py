from pathlib import Path
import sys

import pytest
import requests
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

from app.connectors.suppliers.http_client import ReadOnlyHttpClient
from app.connectors.suppliers.registry import SupplierConnectorRegistry
from app.connectors.suppliers.stenso import StensoPublicConnector
from app.persistence.v073_phase2.database import create_temporary_or_explicit_schema
from app.services.v073_phase2.import_jobs import create_import_job, get_import_job
from app.services.v073_phase2.organization_registry import (
    add_supplier_source,
    approve_organization,
    list_operator_organizations,
    propose_organization,
    seed_reference_stenso,
)


@pytest.fixture
def db_url(tmp_path):
    url = f"sqlite:///{(tmp_path / 'phase2_rev1.sqlite3').as_posix()}"
    create_temporary_or_explicit_schema(url)
    return url


class FakeResponse:
    status_code = 200

    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        return None


CATEGORY_HTML = (
    '<html><body><article class="product-miniature">'
    '<a href="https://stenso.net/produkt/boti/4794-rabotni-obuvki-diadora-freedom-mid-o6-sr-black-olive-green">'
    '<img src="https://stenso.net/example.webp">'
    "\u0420\u0430\u0431\u043e\u0442\u043d\u0438 \u043e\u0431\u0443\u0432\u043a\u0438 DIADORA FREEDOM MID O6 SR BLACK/OLIVE GREEN"
    '</a>'
    '<span>99,20 EUR</span>'
    '</article></body></html>'
).encode("utf-8")


PRODUCT_HTML = (
    '<html><body>'
    '<h1>\u0411\u043e\u0442\u0438 MARINE O2 FO SRC 06200280</h1>'
    '<div class="price">65,20 EUR</div>'
    '<div class="sizes">'
    '<button class="size disabled" disabled aria-disabled="true">36</button>'
    '<button class="size disabled" disabled aria-disabled="true">37</button>'
    '<button class="size available" aria-disabled="false">38</button>'
    '<button class="size available" aria-disabled="false">39</button>'
    '<button class="size available" aria-disabled="false">40</button>'
    '<button class="size available" aria-disabled="false">41</button>'
    '<button class="size available" aria-disabled="false">42</button>'
    '<button class="size available" aria-disabled="false">43</button>'
    '<button class="size available" aria-disabled="false">44</button>'
    '<button class="size available" aria-disabled="false">45</button>'
    '<button class="size available" aria-disabled="false">46</button>'
    '<button class="size available" aria-disabled="false">47</button>'
    '<button class="size available" aria-disabled="false">48</button>'
    '</div>'
    '</body></html>'
).encode("utf-8")


class FakeSession:
    def __init__(self):
        self.headers = {}

    def get(self, url, timeout=None):
        if "/produkt/" in url:
            return FakeResponse(PRODUCT_HTML)
        return FakeResponse(CATEGORY_HTML)

    def head(self, url, timeout=None, allow_redirects=True):
        return FakeResponse(b"<html></html>")


def test_new_org_is_pending_and_hidden_until_super_admin_approval(db_url):
    proposed = propose_organization(
        db_url,
        name="TEST SUPPLIER",
        roles=["SUPPLIER", "MANUFACTURER"],
        created_by="operator-a",
    )
    assert proposed["status"] == "PENDING_SUPER_ADMIN_APPROVAL"
    assert proposed["visible_to_operators"] is False
    assert "TEST SUPPLIER" not in {x["name"] for x in list_operator_organizations(db_url)}

    approve_organization(db_url, proposed["organization_id"])
    assert "TEST SUPPLIER" in {x["name"] for x in list_operator_organizations(db_url)}


def test_stenso_reference_seed_is_persistent_and_operator_visible(db_url):
    seed_reference_stenso(db_url)
    orgs = list_operator_organizations(db_url)
    stenso = next(x for x in orgs if x["name"] == "STENSO")
    assert {"SUPPLIER", "MANUFACTURER"} == set(stenso["roles"])
    assert stenso["sources"][0]["connector_key"] == "stenso_public"
    assert stenso["sources"][0]["read_only"] is True


def test_supplier_source_requires_approved_organization(db_url):
    proposed = propose_organization(
        db_url, name="HIDDEN", roles=["SUPPLIER"], created_by="operator"
    )
    with pytest.raises(ValueError):
        add_supplier_source(
            db_url,
            organization_id=proposed["organization_id"],
            label="Hidden source",
            connector_key="stenso_public",
            source_type="PUBLIC_WEBSITE",
            base_url="https://stenso.net",
            capabilities=["IDENTITY"],
            catalog_roots=[],
        )


def test_read_only_http_client_blocks_writes():
    client = ReadOnlyHttpClient(
        allowed_hosts={"stenso.net"},
        session=FakeSession(),
    )
    with pytest.raises(PermissionError):
        client.post("https://stenso.net/anything")
    with pytest.raises(PermissionError):
        client.put("https://stenso.net/anything")
    with pytest.raises(PermissionError):
        client.delete("https://stenso.net/anything")


def test_read_only_http_client_blocks_unapproved_hosts():
    client = ReadOnlyHttpClient(
        allowed_hosts={"stenso.net"},
        session=FakeSession(),
    )
    with pytest.raises(ValueError):
        client.get("https://example.com/not-allowed")


def test_stenso_connector_parses_live_category_and_variant_availability_without_real_network():
    http = ReadOnlyHttpClient(
        allowed_hosts={"stenso.net"},
        session=FakeSession(),
    )
    connector = StensoPublicConnector(
        base_url="https://stenso.net",
        catalog_roots=[
            {
                "key": "diadora-work-shoes",
                "label": "DIADORA work shoes",
                "url": "https://stenso.net/211-rabotni-obuvki-diadora",
            }
        ],
        http_client=http,
    )

    categories = connector.list_categories()
    assert categories[0].key == "diadora-work-shoes"

    products = connector.list_products("diadora-work-shoes")
    assert len(products) == 1
    assert "DIADORA FREEDOM MID" in products[0].name
    assert "/produkt/" in products[0].url

    detail = connector.get_product(products[0].source_key)
    sizes = {v["value"]: v["availability"] for v in detail.variants}

    assert sizes["36"] == "OUT_OF_STOCK"
    assert sizes["37"] == "OUT_OF_STOCK"
    for size in ("38","39","40","41","42","43","44","45","46","47","48"):
        assert sizes[size] == "IN_STOCK"

    assert detail.availability_text == "PARTIAL_VARIANT_AVAILABILITY"
    assert detail.facts["availability_scope"] == "VARIANT"
    assert detail.facts["variant_count"] == 13


def test_stenso_variant_parser_does_not_depend_on_css_color():
    source = (
        '<html><body>'
        '<button class="size disabled" disabled>36</button>'
        '<button class="size available">38</button>'
        '</body></html>'
    ).encode("utf-8")
    http = ReadOnlyHttpClient(
        allowed_hosts={"stenso.net"},
        session=FakeSession(),
    )
    connector = StensoPublicConnector(
        base_url="https://stenso.net",
        catalog_roots=[],
        http_client=http,
    )
    tree = html.fromstring(source)
    variants = {v["value"]: v["availability"] for v in connector._parse_variant_availability(tree)}
    assert variants == {"36": "OUT_OF_STOCK", "38": "IN_STOCK"}


def test_connector_registry_rejects_unknown_connector():
    registry = SupplierConnectorRegistry()
    with pytest.raises(KeyError):
        registry.create("unknown")


def test_import_job_persists_requested_authorized_ready_blocked_scope(db_url):
    seed_reference_stenso(db_url)

    job = create_import_job(
        db_url,
        created_by="operator-a",
        source_organization_id="org-stenso",
        source_id="src-stenso-public",
        selection_mode="multiple_products",
        selected_products=["product-a", "product-b"],
        selected_categories=[],
        observation_ids=["obs-a", "obs-b"],
        target_scope={
            "requested_targets": ["m99.eu", "mela99.com", "alviro.ro"],
            "authorized_targets": ["m99.eu", "mela99.com", "alviro.ro"],
            "ready_targets": ["m99.eu", "mela99.com"],
            "blocked_targets": ["alviro.ro"],
        },
    )

    assert job["status"] == "DRAFT"
    assert job["dry_run"] is True
    assert job["requires_confirmation"] is True
    assert set(job["ready_targets"]) == {"m99.eu", "mela99.com"}
    assert job["blocked_targets"] == ["alviro.ro"]
    assert get_import_job(db_url, job["job_id"]) == job


def test_installer_scope_contains_no_production_db_migration():
    arch = (ROOT / "ARCHITECTURE_v0.7.3_PHASE2_REV1.md").read_text(encoding="utf-8-sig")
    assert "does not create production tables" in arch
    assert "does not run production Alembic upgrade" in arch


def test_supplier_connector_contract_is_read_only():
    contract = (ADMIN / "app/connectors/suppliers/contract.py").read_text(encoding="utf-8-sig")
    http_client = (ADMIN / "app/connectors/suppliers/http_client.py").read_text(encoding="utf-8-sig")
    assert "read_only: bool = True" in contract
    assert "POST is forbidden" in http_client
    assert "DELETE is forbidden" in http_client


def test_phase2_does_not_duplicate_daily_sync_architecture():
    arch = (ROOT / "ARCHITECTURE_v0.7.3_PHASE2_REV1.md").read_text(encoding="utf-8-sig")
    assert "designed to be reused by those" in arch
    assert "Daily Sync / Presence / External warehouses" in arch
