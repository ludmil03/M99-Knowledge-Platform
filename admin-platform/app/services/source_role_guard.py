from __future__ import annotations
from urllib.parse import urlparse

def normalized_host(url: str) -> str:
    host=(urlparse(url or "").hostname or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host

def validate_manufacturer_source(supplier_base_url: str, manufacturer_url: str) -> tuple[bool,str]:
    supplier_host=normalized_host(supplier_base_url)
    manufacturer_host=normalized_host(manufacturer_url)

    if not manufacturer_host:
        return False,"MANUFACTURER_URL_REQUIRED"
    if not supplier_host:
        return False,"SUPPLIER_HOST_UNKNOWN"
    if manufacturer_host==supplier_host:
        return False,"MANUFACTURER_MUST_DIFFER_FROM_SUPPLIER"
    return True,"PASS"
