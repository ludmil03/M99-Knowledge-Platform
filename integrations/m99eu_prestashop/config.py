from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import os


@dataclass(frozen=True)
class M99EUPrestaShopConfig:
    base_url: str
    api_key: str
    test_category_id: int
    timeout_seconds: int = 20

    @property
    def api_base(self) -> str:
        return self.base_url.rstrip("/") + "/api"

    def validate(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https":
            raise ValueError("M99EU_BASE_URL must use https")
        if parsed.hostname is None or parsed.hostname.lower() not in {"m99.eu", "www.m99.eu"}:
            raise ValueError("M99EU_BASE_URL must point to m99.eu")
        if len(self.api_key.strip()) < 16:
            raise ValueError("M99EU_PS_API_KEY appears too short")
        if self.test_category_id <= 0:
            raise ValueError("M99EU_PS_TEST_CATEGORY_ID must be positive")
        if not (5 <= self.timeout_seconds <= 120):
            raise ValueError("timeout_seconds must be between 5 and 120")


def _read_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def load_m99eu_prestashop_config(env_path: Path | None = None) -> M99EUPrestaShopConfig:
    env_path = env_path or (
        Path(__file__).resolve().parents[2] / "admin-platform" / ".env.local"
    )
    values = _read_env(env_path)

    def get(name: str, default: str = "") -> str:
        return os.getenv(name, values.get(name, default)).strip()

    config = M99EUPrestaShopConfig(
        base_url=get("M99EU_BASE_URL", "https://m99.eu"),
        api_key=get("M99EU_PS_API_KEY"),
        test_category_id=int(get("M99EU_PS_TEST_CATEGORY_ID", "0")),
        timeout_seconds=int(get("M99EU_TIMEOUT_SECONDS", "20")),
    )
    config.validate()
    return config
