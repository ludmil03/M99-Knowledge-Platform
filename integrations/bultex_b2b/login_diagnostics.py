from __future__ import annotations

from dataclasses import dataclass, asdict
from html import unescape
import re
from urllib.parse import urlparse, parse_qs

import requests


@dataclass
class InputDescriptor:
    name: str | None
    input_type: str
    has_value: bool
    value_redacted: bool = True


@dataclass
class FormDescriptor:
    index: int
    action: str
    method: str
    inputs: list[InputDescriptor]
    onsubmit: str | None


@dataclass
class LoginPageDiagnostics:
    request_url: str
    final_url: str
    status_code: int
    query_parameter_names: list[str]
    forms: list[FormDescriptor]
    script_sources: list[str]
    inline_function_names: list[str]
    password_keyword_present: bool
    login_keyword_present: bool


def _attr(tag: str, name: str) -> str | None:
    m = re.search(
        rf'\b{name}\s*=\s*(["\'])(.*?)\1',
        tag,
        flags=re.I | re.S,
    )
    if m:
        return unescape(m.group(2))
    return None


def diagnose_login_page(
    base_url: str = "https://b2b.bultex99.com:8823",
    client_code_hint: str | None = None,
) -> LoginPageDiagnostics:
    """
    Safe diagnostics only:
    - GET login page
    - no credential submission
    - no cookie/session values printed
    - no input values returned
    """
    base_url = base_url.rstrip("/")
    url = f"{base_url}/pap/login.php"

    params = {}
    if client_code_hint:
        # Diagnostic request may preserve the same URL shape the portal uses,
        # but the actual client-code value is never returned in diagnostics.
        params["CNum"] = client_code_hint

    session = requests.Session()
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    html = response.text

    form_blocks = re.findall(r"<form\b.*?</form>", html, flags=re.I | re.S)
    forms: list[FormDescriptor] = []

    for idx, form_html in enumerate(form_blocks):
        opening = re.search(r"<form\b[^>]*>", form_html, flags=re.I | re.S)
        opening_tag = opening.group(0) if opening else "<form>"

        action = _attr(opening_tag, "action") or ""
        method = (_attr(opening_tag, "method") or "get").lower()
        onsubmit = _attr(opening_tag, "onsubmit")

        inputs: list[InputDescriptor] = []
        for tag in re.findall(r"<input\b[^>]*>", form_html, flags=re.I | re.S):
            name = _attr(tag, "name")
            input_type = (_attr(tag, "type") or "text").lower()
            value = _attr(tag, "value")
            inputs.append(
                InputDescriptor(
                    name=name,
                    input_type=input_type,
                    has_value=(value not in (None, "")),
                    value_redacted=True,
                )
            )

        # Some old portals use textarea/select for login identity.
        for tag in re.findall(r"<textarea\b[^>]*>", form_html, flags=re.I | re.S):
            inputs.append(
                InputDescriptor(
                    name=_attr(tag, "name"),
                    input_type="textarea",
                    has_value=False,
                    value_redacted=True,
                )
            )
        for tag in re.findall(r"<select\b[^>]*>", form_html, flags=re.I | re.S):
            inputs.append(
                InputDescriptor(
                    name=_attr(tag, "name"),
                    input_type="select",
                    has_value=False,
                    value_redacted=True,
                )
            )

        forms.append(
            FormDescriptor(
                index=idx,
                action=action,
                method=method,
                inputs=inputs,
                onsubmit=onsubmit,
            )
        )

    script_sources = []
    for tag in re.findall(r"<script\b[^>]*>", html, flags=re.I | re.S):
        src = _attr(tag, "src")
        if src:
            script_sources.append(src)

    inline_function_names = sorted(
        set(
            re.findall(
                r"(?:function\s+([A-Za-z_$][\w$]*)\s*\(|"
                r"([A-Za-z_$][\w$]*)\s*=\s*function\s*\()",
                html,
                flags=re.I,
            )
        )
    )
    flat_names = []
    for pair in inline_function_names:
        for name in pair:
            if name:
                flat_names.append(name)

    parsed = urlparse(response.url)
    query_parameter_names = sorted(parse_qs(parsed.query).keys())

    visible_text = re.sub(r"<[^>]+>", " ", html)
    visible_text = re.sub(r"\s+", " ", unescape(visible_text)).lower()

    return LoginPageDiagnostics(
        request_url=url,
        final_url=f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        + (("?" + "&".join(f"{k}=<redacted>" for k in query_parameter_names))
           if query_parameter_names else ""),
        status_code=response.status_code,
        query_parameter_names=query_parameter_names,
        forms=forms,
        script_sources=script_sources,
        inline_function_names=sorted(set(flat_names)),
        password_keyword_present=("парола" in visible_text or "password" in visible_text),
        login_keyword_present=("вход" in visible_text or "login" in visible_text),
    )


def diagnostics_as_dict(diag: LoginPageDiagnostics) -> dict:
    return asdict(diag)
