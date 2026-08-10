from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
import time
import requests


@dataclass
class Mela99ClientConfig:
    base_url: str
    api_key_env: str
    timeout_seconds: int = 30


class ControlledMela99Publisher:
    def __init__(self, config: Mela99ClientConfig):
        self.config = config

    def api_key(self) -> str:
        key = os.environ.get(self.config.api_key_env)
        if not key:
            raise RuntimeError(
                f"Missing environment variable: {self.config.api_key_env}"
            )
        return key

    def _url(self, path: str) -> str:
        return self.config.base_url.rstrip("/") + "/" + path.lstrip("/")

    def get_product_xml(self, product_id: str) -> str:
        response = requests.get(
            self._url(f"/api/products/{product_id}"),
            auth=(self.api_key(), ""),
            timeout=self.config.timeout_seconds,
            headers={"Accept": "application/xml"},
        )
        response.raise_for_status()
        return response.text

    def create_product_xml(self, xml_body: str) -> str:
        response = requests.post(
            self._url("/api/products"),
            data=xml_body.encode("utf-8"),
            auth=(self.api_key(), ""),
            timeout=self.config.timeout_seconds,
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml",
            },
        )
        response.raise_for_status()
        return response.text

    def update_product_xml(self, product_id: str, xml_body: str) -> str:
        response = requests.put(
            self._url(f"/api/products/{product_id}"),
            data=xml_body.encode("utf-8"),
            auth=(self.api_key(), ""),
            timeout=self.config.timeout_seconds,
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml",
            },
        )
        response.raise_for_status()
        return response.text

    def rollback_product_xml(self, product_id: str, original_xml: str) -> str:
        # Rollback is a full PUT of the exact product snapshot captured before update.
        response = requests.put(
            self._url(f"/api/products/{product_id}"),
            data=original_xml.encode("utf-8"),
            auth=(self.api_key(), ""),
            timeout=self.config.timeout_seconds,
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml",
            },
        )
        response.raise_for_status()
        return response.text


def write_audit_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    redacted = dict(record)
    # Never persist credentials or Authorization headers.
    for key in list(redacted.keys()):
        if "key" in key.lower() or "secret" in key.lower() or "password" in key.lower():
            redacted[key] = "***REDACTED***"
    path.write_text(
        json.dumps(redacted, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
