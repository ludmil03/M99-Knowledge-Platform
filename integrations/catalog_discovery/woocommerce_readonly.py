from __future__ import annotations

import os
import requests
from urllib.parse import urljoin

from .base import ReadOnlyCatalogAdapter, ReadOnlyAdapterConfig


class WooCommerceReadOnlyAdapter(ReadOnlyCatalogAdapter):
    def __init__(self, config: ReadOnlyAdapterConfig, key_env: str, secret_env: str):
        super().__init__(config)
        self.key_env = key_env
        self.secret_env = secret_env

    def configured(self) -> bool:
        return bool(os.environ.get(self.key_env) and os.environ.get(self.secret_env))

    def _get(self, params: dict):
        url = urljoin(
            self.config.base_url.rstrip("/") + "/",
            "wp-json/wc/v3/products",
        )
        response = requests.get(
            url,
            params=params,
            auth=(os.environ.get(self.key_env), os.environ.get(self.secret_env)),
            timeout=self.config.timeout_seconds,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []

    def search(self, identity: dict) -> list[dict]:
        if not self.configured():
            return []

        rows, seen = [], set()
        name = identity.get("model_name") or ""

        raw_rows = []
        for sku in [
            identity.get("manufacturer_item"),
            *(identity.get("legacy_identifiers") or []),
        ]:
            if sku:
                raw_rows.extend(self._get({"sku": str(sku), "per_page": 100}))
        if name:
            raw_rows.extend(self._get({"search": name, "per_page": 100}))

        for raw in raw_rows:
            product_id = str(raw.get("id", "")).strip()
            if not product_id or product_id in seen:
                continue
            seen.add(product_id)

            rows.append({
                "product_id": product_id,
                "url": raw.get("permalink"),
                "name": raw.get("name"),
                "brand": None,
                "reference": str(raw.get("sku") or "").strip() or None,
                "ean": None,
                "legacy_identifiers": [],
                "protection_class": None,
                "active": raw.get("status") == "publish",
                "raw_source": "woocommerce_rest_get",
            })

        return rows
