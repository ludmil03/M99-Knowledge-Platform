from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .config import M99EUPrestaShopConfig


class PrestaShopAPIError(RuntimeError):
    pass


@dataclass
class PrestaShopWebserviceClient:
    config: M99EUPrestaShopConfig
    session: Any = None

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session()

    def _request(self, method: str, path: str = "", **kwargs: Any):
        url = self.config.api_base.rstrip("/") + "/" + path.lstrip("/")
        kwargs.setdefault("auth", (self.config.api_key, ""))
        kwargs.setdefault("timeout", self.config.timeout_seconds)
        kwargs.setdefault("allow_redirects", False)
        kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("Accept", "application/xml")

        response = self.session.request(method, url, **kwargs)

        if 300 <= response.status_code < 400:
            raise PrestaShopAPIError(
                f"Unexpected redirect blocked: HTTP {response.status_code}"
            )
        if response.status_code >= 400:
            raise PrestaShopAPIError(
                f"PrestaShop API error HTTP {response.status_code}: {response.text[:1000]}"
            )
        return response

    def get_api_root(self) -> str:
        return self._request("GET", "").text

    def get_languages(self) -> str:
        return self._request(
            "GET",
            "languages",
            params={"display": "[id,iso_code,active]", "filter[active]": "1"},
        ).text

    def get_categories(self) -> str:
        return self._request(
            "GET",
            "categories",
            params={"display": "[id,name,active]", "limit": "50"},
        ).text

    def get_product_blank_schema(self) -> str:
        return self._request(
            "GET",
            "products",
            params={"schema": "blank"},
        ).text

    def get_product(self, product_id: int) -> str:
        return self._request("GET", f"products/{int(product_id)}").text

    def create_product(self, xml_body: str) -> str:
        return self._request(
            "POST",
            "products",
            data=xml_body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
        ).text
