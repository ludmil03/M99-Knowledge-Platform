from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import os
import re
from urllib.parse import urljoin, urlparse

import requests

from .parser import parse_product_page


class BultexAuthError(RuntimeError):
    pass


@dataclass
class DiscoveredLoginForm:
    action_url: str
    method: str
    client_code_field: str
    username_field: str
    password_field: str
    action_field: str
    action_value: str


class BultexSafeReadOnlyClient:
    """
    Authenticated READ-ONLY client.

    Allowed:
      GET login page
      GET login form submission (portal's native login method)
      GET product page /pap/minfo.php?i=<numeric id>

    No basket/order/document/Dolibarr/channel write methods exist here.
    """

    def __init__(self, base_url="https://b2b.bultex99.com:8823"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "M99-Knowledge-Platform/0.5.6.5 read-only supplier connector"
        })

    def _credentials(self):
        vals = (
            os.getenv("BULTEX_B2B_CLIENT_CODE", ""),
            os.getenv("BULTEX_B2B_USERNAME", ""),
            os.getenv("BULTEX_B2B_PASSWORD", ""),
        )
        if not all(vals):
            raise BultexAuthError("Missing Bultex B2B credentials in process environment")
        return vals

    @staticmethod
    def _attr(tag, name):
        m = re.search(rf'\b{name}\s*=\s*(["\'])(.*?)\1', tag, re.I|re.S)
        return unescape(m.group(2)) if m else None

    def discover_login_form(self, client_code_hint=None):
        url = f"{self.base_url}/pap/login.php"
        params = {"CNum": client_code_hint} if client_code_hint else None
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        html = r.text

        forms = re.findall(r"<form\b.*?</form>", html, re.I|re.S)
        form = next((f for f in forms if "checkit()" in f), forms[0] if forms else "")
        if not form:
            raise BultexAuthError("Login form not found")

        opening_m = re.search(r"<form\b[^>]*>", form, re.I|re.S)
        opening = opening_m.group(0) if opening_m else ""
        action = self._attr(opening, "action") or "/pap/login.php"
        method = (self._attr(opening, "method") or "get").lower()

        names = []
        for tag in re.findall(r"<input\b[^>]*>", form, re.I|re.S):
            name = self._attr(tag, "name")
            if name:
                names.append(name)

        user_fields = [n for n in names if re.fullmatch(r"edaderpu_[A-Fa-f0-9]+", n)]
        pass_fields = [n for n in names if re.fullmatch(r"edaderpp_[A-Fa-f0-9]+", n)]

        if len(user_fields) != 1 or len(pass_fields) != 1:
            raise BultexAuthError(
                "Could not safely identify exactly one dynamic username/password field"
            )
        if "CNum" not in names or "act" not in names:
            raise BultexAuthError("Required CNum/act login fields missing")
        if method != "get":
            raise BultexAuthError(f"Unexpected login method: {method}")

        action_url = urljoin(r.url, action)

        return DiscoveredLoginForm(
            action_url=action_url,
            method=method,
            client_code_field="CNum",
            username_field=user_fields[0],
            password_field=pass_fields[0],
            action_field="act",
            action_value="li",
        )

    def login(self):
        client_code, username, password = self._credentials()
        form = self.discover_login_form(client_code_hint=client_code)

        params = {
            form.client_code_field: client_code,
            form.username_field: username,
            form.password_field: password,
            form.action_field: form.action_value,
        }

        r = self.session.get(form.action_url, params=params, timeout=30)
        r.raise_for_status()

        body = r.text.lower()
        parsed = urlparse(r.url)

        # Portal may redirect or return an authenticated landing page.
        still_login = (
            parsed.path.endswith("/pap/login.php")
            and ("липсва парола" in body or "потребителско име" in body or "клиентски код" in body)
            and "checkit()" in body
        )
        if still_login:
            raise BultexAuthError("Authentication did not leave the login page")

        return {
            "authenticated": True,
            "final_path": parsed.path,
            "status_code": r.status_code,
        }

    def read_product(self, product_id, warehouse_code, warehouse_name):
        if not re.fullmatch(r"\d+", str(product_id)):
            raise ValueError("product_id must be numeric")

        url = f"{self.base_url}/pap/minfo.php"
        r = self.session.get(url, params={"i": str(product_id)}, timeout=30)
        r.raise_for_status()

        # If session expired, refuse to parse login HTML as product data.
        if "checkit()" in r.text and "/pap/login.php" in r.text:
            raise BultexAuthError("Session is not authenticated or has expired")

        return parse_product_page(
            r.text,
            source_url=f"{url}?i={product_id}",
            warehouse_code=warehouse_code,
            warehouse_name=warehouse_name,
        )
