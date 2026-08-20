from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import os


DEFAULT_BASE_URL = "https://m99.eu"
DEFAULT_API_PATH = "/wp-json/wc/v3"


@dataclass(frozen=True)
class M99EUConfig:
    base_url: str
    api_path: str
    consumer_key: str
    consumer_secret: str
    timeout_seconds: int = 20

    @property
    def api_base(self) -> str:
        return self.base_url.rstrip("/") + "/" + self.api_path.strip("/")

    def validate(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https":
            raise ValueError("M99EU_BASE_URL must use https")
        if parsed.hostname is None:
            raise ValueError("M99EU_BASE_URL has no hostname")
        if parsed.hostname.lower() not in {"m99.eu", "www.m99.eu"}:
            raise ValueError("M99EU_BASE_URL must point to m99.eu")
        if not self.consumer_key.startswith("ck_"):
            raise ValueError("WooCommerce Consumer Key should start with ck_")
        if not self.consumer_secret.startswith("cs_"):
            raise ValueError("WooCommerce Consumer Secret should start with cs_")
        if self.timeout_seconds < 5 or self.timeout_seconds > 120:
            raise ValueError("timeout_seconds must be between 5 and 120")


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_m99eu_config(env_path: Path | None = None) -> M99EUConfig:
    env_path = env_path or (
        Path(__file__).resolve().parents[2] / "admin-platform" / ".env.local"
    )
    file_values = _read_env_file(env_path)

    def get(name: str, default: str = "") -> str:
        return os.getenv(name, file_values.get(name, default)).strip()

    config = M99EUConfig(
        base_url=get("M99EU_BASE_URL", DEFAULT_BASE_URL),
        api_path=get("M99EU_API_PATH", DEFAULT_API_PATH),
        consumer_key=get("M99EU_WC_CONSUMER_KEY"),
        consumer_secret=get("M99EU_WC_CONSUMER_SECRET"),
        timeout_seconds=int(get("M99EU_TIMEOUT_SECONDS", "20")),
    )
    config.validate()
    return config
