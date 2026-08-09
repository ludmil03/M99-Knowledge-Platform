from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import os
import re
from typing import Optional

import requests

from .parser import parse_product_page


@dataclass
class LoginFieldMap:
    action: str
    method: str
    client_code_field: Optional[str]
    username_field: Optional[str]
    password_field: Optional[str]
    submit_fields: dict[str, str]


class BultexLoginDiscoveryError(RuntimeError):
    pass


class BultexReadOnlyClient:
    """
    READ-ONLY integration client.

    Safety guarantees:
    - Only GET for discovery and product reads.
    - POST is used only for authentication.
    - No basket, order, document, Dolibarr or channel write endpoint exists here.
    - Credentials are loaded from environment variables only.
    """

    def __init__(self, base_url: str = "https://b2b.bultex99.com:8823"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "M99-Knowledge-Platform/0.5.6 read-only supplier connector"
        })

    @property
    def login_url(self) -> str:
        return f"{self.base_url}/pap/login.php"

    def discover_login_form(self) -> LoginFieldMap:
        response = self.session.get(self.login_url, timeout=30)
        response.raise_for_status()
        html = response.text

        forms = re.findall(r"<form\b.*?</form>", html, flags=re.I | re.S)
        if not forms:
            raise BultexLoginDiscoveryError("No login form found")

        # Pick the form that contains a password input.
        form = next(
            (f for f in forms if re.search(r'type=["\']password["\']', f, re.I)),
            None,
        )
        if not form:
            raise BultexLoginDiscoveryError("No form with password input found")

        action_m = re.search(r'action=["\']([^"\']*)["\']', form, re.I)
        method_m = re.search(r'method=["\']([^"\']*)["\']', form, re.I)
        action = unescape(action_m.group(1)) if action_m else "/pap/login.php"
        method = (method_m.group(1) if method_m else "post").lower()

        inputs = []
        for tag in re.findall(r"<input\b[^>]*>", form, flags=re.I):
            name_m = re.search(r'name=["\']([^"\']+)["\']', tag, re.I)
            type_m = re.search(r'type=["\']([^"\']+)["\']', tag, re.I)
            value_m = re.search(r'value=["\']([^"\']*)["\']', tag, re.I)
            if not name_m:
                continue
            inputs.append({
                "name": name_m.group(1),
                "type": (type_m.group(1).lower() if type_m else "text"),
                "value": (unescape(value_m.group(1)) if value_m else ""),
            })

        password = next((x["name"] for x in inputs if x["type"] == "password"), None)
        text_fields = [x["name"] for x in inputs if x["type"] in ("text", "number")]

        # We do not submit if the three identity fields cannot be distinguished.
        # The portal visibly has Client code, Username and Password.
        client_code = None
        username = None

        for name in text_fields:
            low = name.lower()
            if any(k in low for k in ("cnum", "client", "cust", "customer")):
                client_code = name
            elif any(k in low for k in ("user", "login", "name")):
                username = name

        # If semantic names are absent, use positional mapping only when exactly 2 text fields exist.
        if len(text_fields) == 2:
            client_code = client_code or text_fields[0]
            username = username or text_fields[1]

        submit_fields = {
            x["name"]: x["value"]
            for x in inputs
            if x["type"] in ("hidden", "submit") and x["value"] != ""
        }

        return LoginFieldMap(
            action=action,
            method=method,
            client_code_field=client_code,
            username_field=username,
            password_field=password,
            submit_fields=submit_fields,
        )

    def _credentials(self) -> tuple[str, str, str]:
        values = (
            os.getenv("BULTEX_B2B_CLIENT_CODE", ""),
            os.getenv("BULTEX_B2B_USERNAME", ""),
            os.getenv("BULTEX_B2B_PASSWORD", ""),
        )
        if not all(values):
            raise RuntimeError(
                "Missing BULTEX_B2B_CLIENT_CODE / BULTEX_B2B_USERNAME / BULTEX_B2B_PASSWORD"
            )
        return values

    def login(self, fields: LoginFieldMap) -> None:
        if fields.method != "post":
            raise RuntimeError("Unsupported login method; expected POST")
        if not all((
            fields.client_code_field,
            fields.username_field,
            fields.password_field,
        )):
            raise RuntimeError(
                "Login form fields could not be mapped safely. No authentication was attempted."
            )

        client_code, username, password = self._credentials()

        payload = dict(fields.submit_fields)
        payload[fields.client_code_field] = client_code
        payload[fields.username_field] = username
        payload[fields.password_field] = password

        if fields.action.startswith("http"):
            url = fields.action
        elif fields.action.startswith("/"):
            url = f"{self.base_url}{fields.action}"
        else:
            url = f"{self.base_url}/pap/{fields.action}"

        response = self.session.post(url, data=payload, timeout=30)
        response.raise_for_status()

        body = response.text.lower()
        # Positive/negative test without exposing credentials or cookies.
        if "потребителско име" in body and "парола" in body and "клиентски код" in body:
            raise RuntimeError("Authentication appears to have returned the login page")

    def read_product(
        self,
        product_id: str,
        warehouse_code: str,
        warehouse_name: str,
    ):
        # Strict allow-list: product information endpoint only.
        if not re.fullmatch(r"\d+", str(product_id)):
            raise ValueError("product_id must be numeric")

        url = f"{self.base_url}/pap/minfo.php"
        response = self.session.get(url, params={"i": product_id}, timeout=30)
        response.raise_for_status()

        return parse_product_page(
            response.text,
            source_url=f"{url}?i={product_id}",
            warehouse_code=warehouse_code,
            warehouse_name=warehouse_name,
        )
