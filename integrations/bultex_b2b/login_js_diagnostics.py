from dataclasses import dataclass, asdict
from html import unescape
import re
from urllib.parse import urljoin
import requests

@dataclass
class FunctionDiagnostic:
    name: str
    source: str
    origin: str

@dataclass
class LoginJsDiagnostics:
    form_method: str
    form_action: str
    ordered_named_fields: list[str]
    visible_labels: list[str]
    checkit_functions: list[FunctionDiagnostic]
    referenced_field_names: list[str]
    script_urls_checked: list[str]

def _attr(tag, name):
    m = re.search(rf'\b{name}\s*=\s*(["\'])(.*?)\1', tag, re.I|re.S)
    return unescape(m.group(2)) if m else None

def _extract_function_body(source, function_name):
    m = re.search(rf'function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{', source, re.I)
    if not m:
        return None
    start = m.start()
    brace_start = source.find("{", m.start())
    depth = 0
    quote = None
    escaped = False
    for i in range(brace_start, len(source)):
        ch = source[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start:i+1]
    return None

def diagnose_login_javascript(base_url="https://b2b.bultex99.com:8823"):
    s = requests.Session()
    login_url = f"{base_url.rstrip('/')}/pap/login.php"
    r = s.get(login_url, timeout=30)
    r.raise_for_status()
    html = r.text

    forms = re.findall(r"<form\b.*?</form>", html, re.I|re.S)
    form = forms[0] if forms else ""
    opening_m = re.search(r"<form\b[^>]*>", form, re.I|re.S)
    opening = opening_m.group(0) if opening_m else ""
    method = (_attr(opening,"method") or "get").lower()
    action = _attr(opening,"action") or ""

    fields = []
    for tag in re.findall(r"<(?:input|select|textarea)\b[^>]*>", form, re.I|re.S):
        name = _attr(tag,"name")
        if name:
            fields.append(name)

    visible = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I|re.S)
    visible = re.sub(r"<style\b.*?</style>", " ", visible, flags=re.I|re.S)
    visible = re.sub(r"<[^>]+>", "\n", visible)
    labels = [x.strip() for x in unescape(visible).splitlines()
              if x.strip() and any(k in x.lower() for k in ("клиент","потребител","парола","вход","client","user","password","login"))]

    functions = []
    inline = "\n".join(re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.I|re.S))
    body = _extract_function_body(inline, "checkit")
    if body:
        functions.append(FunctionDiagnostic("checkit", body, "inline-login-page"))

    srcs = []
    for tag in re.findall(r"<script\b[^>]*>", html, re.I|re.S):
        src = _attr(tag,"src")
        if src:
            srcs.append(urljoin(r.url, src))

    checked = []
    for url in [u for u in srcs if any(x in u.lower() for x in ("common.js","dbn.js","msg.js"))]:
        checked.append(url)
        rr = s.get(url, timeout=30)
        rr.raise_for_status()
        body = _extract_function_body(rr.text, "checkit")
        if body:
            functions.append(FunctionDiagnostic("checkit", body, url))

    combined = "\n".join(f.source for f in functions)
    refs = sorted(set(re.findall(r'\b(?:CNum|edaderpu_[A-Fa-f0-9]+|edaderpp_[A-Fa-f0-9]+)\b', combined)))

    return LoginJsDiagnostics(method, action, fields, labels, functions, refs, checked)

def diagnostics_as_dict(diag):
    return asdict(diag)
