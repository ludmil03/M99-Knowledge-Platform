from __future__ import annotations

from urllib.parse import urlparse

import requests


class ReadOnlyHttpClient:
    """Supplier HTTP client that permits GET/HEAD only and enforces host allowlist."""

    def __init__(
        self,
        *,
        allowed_hosts: set[str],
        timeout_seconds: float = 20.0,
        user_agent: str = "M99-Knowledge-Platform/0.7.3 SupplierBrowser",
        session: requests.Session | None = None,
    ) -> None:
        self.allowed_hosts = {h.lower() for h in allowed_hosts}
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _check_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Supplier source URL must use HTTP or HTTPS.")
        if (parsed.hostname or "").lower() not in self.allowed_hosts:
            raise ValueError("Supplier source host is not allowed.")

    def get(self, url: str) -> requests.Response:
        self._check_url(url)
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response

    def head(self, url: str) -> requests.Response:
        self._check_url(url)
        response = self.session.head(url, timeout=self.timeout_seconds, allow_redirects=True)
        response.raise_for_status()
        return response

    def post(self, *args, **kwargs):
        raise PermissionError("Supplier Browser is read-only; POST is forbidden.")

    def put(self, *args, **kwargs):
        raise PermissionError("Supplier Browser is read-only; PUT is forbidden.")

    def patch(self, *args, **kwargs):
        raise PermissionError("Supplier Browser is read-only; PATCH is forbidden.")

    def delete(self, *args, **kwargs):
        raise PermissionError("Supplier Browser is read-only; DELETE is forbidden.")
