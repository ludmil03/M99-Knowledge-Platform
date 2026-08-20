from __future__ import annotations

from dataclasses import replace

import pytest

from integrations.m99eu.client import M99EUAPIError, M99EUClient
from integrations.m99eu.config import M99EUConfig
from integrations.m99eu.publisher import (
    build_test_draft_payload,
    verify_product_readback,
)


class FakeResponse:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data
        self.text = text

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


@pytest.fixture
def config():
    return M99EUConfig(
        base_url="https://m99.eu",
        api_path="/wp-json/wc/v3",
        consumer_key="ck_" + "a" * 20,
        consumer_secret="cs_" + "b" * 20,
    )


def test_config_rejects_non_https(config):
    with pytest.raises(ValueError):
        replace(config, base_url="http://m99.eu").validate()


def test_config_rejects_other_host(config):
    with pytest.raises(ValueError):
        replace(config, base_url="https://example.com").validate()


def test_payload_is_always_draft_and_hidden():
    payload = build_test_draft_payload(sku="M99-TEST-1", name="Test")
    assert payload["status"] == "draft"
    assert payload["catalog_visibility"] == "hidden"
    assert payload["sku"] == "M99-TEST-1"
    assert payload["manage_stock"] is False


def test_preflight_is_read_only_get(config):
    session = FakeSession([FakeResponse(200, [])])
    result = M99EUClient(config, session=session).preflight()
    assert result["products_endpoint_readable"] is True
    assert session.calls[0][0] == "GET"


def test_client_blocks_redirect(config):
    session = FakeSession([FakeResponse(302, {}, "redirect")])
    with pytest.raises(M99EUAPIError):
        M99EUClient(config, session=session).preflight()


def test_create_rejects_non_draft_payload(config):
    client = M99EUClient(config, session=FakeSession([]))
    with pytest.raises(ValueError):
        client.create_product_draft({"status": "publish"})


def test_create_draft_uses_post_and_readback_get(config):
    created = {"id": 100, "name": "Test", "sku": "M99-1", "status": "draft"}
    readback = dict(created)
    session = FakeSession([
        FakeResponse(200, []),
        FakeResponse(201, created),
        FakeResponse(200, readback),
    ])
    client = M99EUClient(config, session=session)

    assert client.preflight()["authenticated"]
    payload = build_test_draft_payload(sku="M99-1", name="Test")
    result = client.create_product_draft(payload)
    actual = client.get_product(result["id"])

    assert [call[0] for call in session.calls] == ["GET", "POST", "GET"]
    assert verify_product_readback(payload, actual)["pass"] is True


def test_readback_fails_if_site_publishes_product():
    expected = build_test_draft_payload(sku="M99-1", name="Test")
    actual = {"id": 1, "name": "Test", "sku": "M99-1", "status": "publish"}
    checks = verify_product_readback(expected, actual)
    assert checks["pass"] is False
    assert checks["status_draft"] is False
