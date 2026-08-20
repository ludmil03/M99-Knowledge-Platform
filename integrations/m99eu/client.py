from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .config import M99EUConfig


class M99EUAPIError(RuntimeError):
    pass


@dataclass
class M99EUClient:
    config: M99EUConfig
    session: Any = None

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = self.config.api_base.rstrip("/") + "/" + endpoint.lstrip("/")
        kwargs.setdefault(
            "auth",
            (self.config.consumer_key, self.config.consumer_secret),
        )
        kwargs.setdefault("timeout", self.config.timeout_seconds)
        kwargs.setdefault("allow_redirects", False)

        response = self.session.request(method, url, **kwargs)

        if 300 <= response.status_code < 400:
            raise M99EUAPIError(
                f"Unexpected redirect blocked: HTTP {response.status_code}"
            )

        if response.status_code >= 400:
            body = response.text[:600]
            raise M99EUAPIError(
                f"m99.eu API error HTTP {response.status_code}: {body}"
            )

        try:
            return response.json()
        except Exception as exc:
            raise M99EUAPIError("m99.eu returned non-JSON response") from exc

    def preflight(self) -> dict[str, Any]:
        products = self._request(
            "GET",
            "products",
            params={"per_page": 1, "status": "any"},
        )
        return {
            "api_base": self.config.api_base,
            "authenticated": True,
            "products_endpoint_readable": isinstance(products, list),
            "sample_count": len(products) if isinstance(products, list) else None,
        }

    def create_product_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("status") != "draft":
            raise ValueError("Sandbox publisher only permits status=draft")
        return self._request("POST", "products", json=payload)

    def get_product(self, product_id: int) -> dict[str, Any]:
        return self._request("GET", f"products/{int(product_id)}")
