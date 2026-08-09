from dataclasses import dataclass, asdict
from html import unescape
import re
from urllib.parse import urlparse, parse_qs
from .safe_live_auth import BultexSafeReadOnlyClient

@dataclass
class AuthResponseDiagnostics:
    request_method: str
    submitted_parameter_names: list[str]
    status_code: int
    final_path: str
    final_query_parameter_names: list[str]
    response_is_login_page: bool
    visible_messages: list[str]
    response_form_names: list[str]
    cookie_names: list[str]

def _visible_text(html):
    s=re.sub(r"<script\b.*?</script>"," ",html,flags=re.I|re.S)
    s=re.sub(r"<style\b.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>","\n",s)
    return [re.sub(r"\s+"," ",unescape(x)).strip() for x in s.splitlines() if re.sub(r"\s+"," ",unescape(x)).strip()]

def diagnose_authentication_response(client: BultexSafeReadOnlyClient):
    client_code, username, password = client._credentials()
    form = client.discover_login_form(client_code_hint=client_code)
    params = {
        form.client_code_field: client_code,
        form.username_field: username,
        form.password_field: password,
        form.action_field: form.action_value,
    }
    r = client.session.get(form.action_url, params=params, timeout=30)
    r.raise_for_status()
    parsed=urlparse(r.url)

    form_names=[]
    for tag in re.findall(r"<form\b[^>]*>",r.text,flags=re.I|re.S):
        m=re.search(r'name\s*=\s*(["\'])(.*?)\1',tag,flags=re.I|re.S)
        if m: form_names.append(m.group(2))

    keywords=("греш","невалид","липс","парол","потребител","клиент","вход","login","error","invalid","wrong","failed","успеш")
    messages=[]
    for line in _visible_text(r.text):
        if len(line)<=180 and any(k in line.lower() for k in keywords):
            if line not in messages:
                messages.append(line)

    body=r.text.lower()
    is_login=("checkit()" in r.text) or ("потребителско име" in body and "парола" in body)

    return AuthResponseDiagnostics(
        request_method="GET",
        submitted_parameter_names=sorted(params.keys()),
        status_code=r.status_code,
        final_path=parsed.path,
        final_query_parameter_names=sorted(parse_qs(parsed.query).keys()),
        response_is_login_page=is_login,
        visible_messages=messages,
        response_form_names=sorted(set(form_names)),
        cookie_names=sorted(client.session.cookies.keys()),
    )

def diagnostics_as_dict(d):
    return asdict(d)
