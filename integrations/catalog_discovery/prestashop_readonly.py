from __future__ import annotations

import os
import requests
from urllib.parse import urljoin

from .base import ReadOnlyCatalogAdapter, ReadOnlyAdapterConfig


class PrestaShopReadOnlyAdapter(ReadOnlyCatalogAdapter):
    def __init__(self, config: ReadOnlyAdapterConfig, api_key_env: str):
        super().__init__(config)
        self.api_key_env = api_key_env

    def _key(self) -> str | None:
        return os.environ.get(self.api_key_env)

    def configured(self) -> bool:
        return bool(self._key())

    def _get(self, path: str, params: dict) -> requests.Response:
        # Deliberately hard-coded GET; no write method exists.
        url = urljoin(self.config.base_url.rstrip("/") + "/", path.lstrip("/"))
        response = requests.get(
            url,
            params=params,
            auth=(self._key(), ""),
            timeout=self.config.timeout_seconds,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response

    @staticmethod
    def _product_rows(payload):
        if isinstance(payload, list):
            return payload
        if not isinstance(payload, dict):
            return []
        products = payload.get("products", payload.get("product", []))
        if isinstance(products, dict):
            return [products]
        return products or []

    def _search_reference(self, reference: str) -> list[dict]:
        if not reference:
            return []
        r = self._get(
            "/api/products",
            {
                "filter[reference]": f"[{reference}]",
                "display": "full",
                "output_format": "JSON",
            },
        )
        return self._product_rows(r.json())

    def _search_ean(self, ean: str) -> list[dict]:
        if not ean:
            return []
        r = self._get(
            "/api/products",
            {
                "filter[ean13]": f"[{ean}]",
                "display": "full",
                "output_format": "JSON",
            },
        )
        return self._product_rows(r.json())

    def _search_name(self, name: str) -> list[dict]:
        if not name:
            return []
        r = self._get(
            "/api/products",
            {
                "filter[name]": f"%[{name}]%",
                "display": "full",
                "output_format": "JSON",
            },
        )
        return self._product_rows(r.json())

    @staticmethod
    def _text(value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            if "value" in value:
                return str(value["value"])
            language = value.get("language")
            if isinstance(language, list) and language:
                item = language[0]
                if isinstance(item, dict):
                    return str(item.get("value", ""))
        if isinstance(value, list) and value:
            item = value[0]
            if isinstance(item, dict):
                return str(item.get("value", ""))
            return str(item)
        return ""

    def search(self, identity: dict) -> list[dict]:
        if not self.configured():
            return []

        rows = []
        seen = set()

        reference_rows = []
        for ref in [
            identity.get("manufacturer_item"),
            *(identity.get("legacy_identifiers") or []),
        ]:
            if ref:
                reference_rows.extend(self._search_reference(str(ref)))

        ean_rows = self._search_ean(str(identity.get("ean") or ""))
        name_rows = self._search_name(identity.get("model_name") or "")

        for raw in reference_rows + ean_rows + name_rows:
            product_id = str(raw.get("id", "")).strip()
            if not product_id or product_id in seen:
                continue
            seen.add(product_id)

            link_rewrite = self._text(raw.get("link_rewrite"))
            url = None
            if link_rewrite:
                url = self.config.base_url.rstrip("/") + "/" + link_rewrite

            rows.append({
                "product_id": product_id,
                "url": url,
                "name": self._text(raw.get("name")),
                "brand": None,
                "reference": str(raw.get("reference") or "").strip() or None,
                "ean": str(raw.get("ean13") or "").strip() or None,
                "legacy_identifiers": [],
                "protection_class": None,
                "active": str(raw.get("active", "1")) not in ("0", "False", "false"),
                "raw_source": "prestashop_webservice_get",
            })

        return rows
