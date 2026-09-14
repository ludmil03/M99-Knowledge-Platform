from __future__ import annotations

from dataclasses import is_dataclass, replace
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urljoin, urlparse
import functools
import inspect
import ipaddress
import json
import re
import socket
import urllib.request

ADAPTER_ID = "M99_V073_PHASE46_R7J_PALLTEX_PRODUCT_HYDRATION_ADAPTER"
_ALLOWED_HOSTS = {"palltex.bg", "www.palltex.bg"}
_MAX_HTML_BYTES = 3_000_000
_USER_AGENT = "M99-Knowledge-Platform/0.7.3 PalltexReadOnlyHydration"

class PalltexHydrationAdapterError(RuntimeError):
    pass

class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self._skip = 0
        self._jsonld = False
        self.jsonld_chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_d = {str(k).lower(): str(v or "") for k, v in attrs}
        if tag in {"script", "style", "noscript"}:
            if tag == "script" and "ld+json" in attrs_d.get("type", "").lower():
                self._jsonld = True
            else:
                self._skip += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "script" and self._jsonld:
            self._jsonld = False
        elif tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._jsonld:
            self.jsonld_chunks.append(data)
            return
        if self._skip:
            return
        s = re.sub(r"\s+", " ", unescape(data or "")).strip()
        if s:
            self.lines.append(s)

def _host(url: str) -> str:
    return (urlparse(str(url or "")).hostname or "").lower().rstrip(".")

def _product_path_ok(url: str) -> bool:
    p = urlparse(str(url or ""))
    return p.scheme.lower() == "https" and _host(url) in _ALLOWED_HOSTS and "/p/" in p.path and re.search(r"/\d+/?$", p.path) is not None

def _validate_public_host(url: str, *, resolve: bool = True) -> str:
    if not _product_path_ok(url):
        raise PalltexHydrationAdapterError("URL must be an HTTPS Palltex product URL.")
    if resolve:
        host = _host(url)
        try:
            infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise PalltexHydrationAdapterError("Palltex DNS resolution failed.") from exc
        if not infos:
            raise PalltexHydrationAdapterError("Palltex DNS resolution returned no addresses.")
        for info in infos:
            addr = info[4][0]
            try:
                ip = ipaddress.ip_address(addr)
            except ValueError as exc:
                raise PalltexHydrationAdapterError("Palltex resolved to an invalid IP address.") from exc
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
                raise PalltexHydrationAdapterError("Palltex resolved to a non-public IP address.")
    return url

class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        resolved = urljoin(req.full_url, newurl)
        if _host(resolved) not in _ALLOWED_HOSTS or urlparse(resolved).scheme.lower() != "https":
            raise PalltexHydrationAdapterError("Cross-domain or non-HTTPS redirect blocked.")
        return super().redirect_request(req, fp, code, msg, headers, resolved)

def _fetch_html(url: str, *, timeout: float = 12.0) -> tuple[str, str]:
    _validate_public_host(url, resolve=True)
    opener = urllib.request.build_opener(_SameHostRedirect())
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            final_url = str(resp.geturl())
            _validate_public_host(final_url, resolve=False)
            ctype = str(resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype:
                raise PalltexHydrationAdapterError("Palltex response is not HTML.")
            raw = resp.read(_MAX_HTML_BYTES + 1)
    except PalltexHydrationAdapterError:
        raise
    except Exception as exc:
        raise PalltexHydrationAdapterError("Palltex read-only GET failed.") from exc
    if len(raw) > _MAX_HTML_BYTES:
        raise PalltexHydrationAdapterError("Palltex HTML exceeds safe size limit.")
    return raw.decode("utf-8", errors="replace"), final_url

def _clean_ref(value: str | None) -> str:
    s = re.sub(r"\s+", "", str(value or "")).strip()
    if not (2 <= len(s) <= 64):
        return ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{1,63}", s):
        return ""
    return s

def _jsonld_product_sku(chunks: list[str]) -> str:
    def walk(obj):
        if isinstance(obj, dict):
            typ = obj.get("@type")
            types = typ if isinstance(typ, list) else [typ]
            if any(str(x).lower() == "product" for x in types if x is not None):
                for key in ("sku", "mpn"):
                    ref = _clean_ref(obj.get(key))
                    if ref:
                        return ref
            graph = obj.get("@graph")
            if graph is not None:
                hit = walk(graph)
                if hit:
                    return hit
            for v in obj.values():
                hit = walk(v)
                if hit:
                    return hit
        elif isinstance(obj, list):
            for v in obj:
                hit = walk(v)
                if hit:
                    return hit
        return ""
    for chunk in chunks:
        try:
            obj = json.loads(chunk)
        except Exception:
            continue
        hit = walk(obj)
        if hit:
            return hit
    return ""

_SKU_LABEL_RE = re.compile(
    r"(?:Код\s+на\s+артикул|Артикулен\s+код|SKU|Код\s+продукт)\s*[:№#]?\s*([^\s<]+)",
    re.I,
)

def _looks_like_size_token(value: str) -> bool:
    return bool(_valid_size_token(str(value or "")))

def _local_product_fact_context(lines: list[str], label_index: int, candidate_index: int) -> bool:
    lo=max(0,label_index-6)
    hi=min(len(lines),candidate_index+22)
    window=[str(x or "").strip() for x in lines[lo:hi]]
    has_color=any(re.fullmatch(r"Цвят\s*:?",x,re.I) or re.match(r"Цвят\s*:\s*\S+",x,re.I) for x in window)
    has_selector=any("избери размер" in x.lower() for x in window)
    has_fact=any(re.match(r"(?:Марка|Наличност)\s*:",x,re.I) for x in window)
    return bool(has_color and (has_selector or has_fact))

def _extract_supplier_reference(lines: list[str], jsonld_chunks: list[str], *, final_url: str = "") -> tuple[str, int | None]:
    # Strong same-node evidence first.
    for i,line in enumerate(lines):
        m=_SKU_LABEL_RE.search(line)
        if m:
            ref=_clean_ref(m.group(1))
            if ref:
                return ref,i

    # Palltex live DOM can split label and value into adjacent text nodes.
    # Allow only immediate-next-node evidence inside a corroborated product-facts
    # neighborhood. Reject garment-size tokens and the URL product id.
    url_product_id=_product_id_from_url(final_url) if final_url else ""
    label_re=re.compile(r"(?:Код\s+на\s+артикул|Артикулен\s+код|SKU|Код\s+продукт)\s*:?\s*$",re.I)
    for i,line in enumerate(lines):
        if not label_re.fullmatch(str(line or "").strip()):
            continue
        j=i+1
        if j>=len(lines):
            continue
        ref=_clean_ref(str(lines[j] or "").strip())
        if not ref or _looks_like_size_token(ref):
            continue
        if url_product_id and ref==url_product_id:
            continue
        if _local_product_fact_context(lines,i,j):
            return ref,i

    # Structured Product JSON-LD remains a separate explicit source.
    ref=_jsonld_product_sku(jsonld_chunks)
    return ref,None

def _extract_color(lines: list[str], sku_index: int | None) -> str:
    def candidate(i: int) -> str:
        line=lines[i]
        m=re.match(r"Цвят\s*:\s*(.+)$",line,re.I)
        if m:
            v=m.group(1).strip()
            if 1<=len(v)<=80:
                return v
        if re.fullmatch(r"Цвят\s*:?",line,re.I):
            for nxt in lines[i+1:i+3]:
                if nxt and len(nxt)<=80 and not re.search(r"(код|sku|цена|налич|избери размер)",nxt,re.I):
                    return nxt
        return ""

    if sku_index is not None:
        # Product color is a fact belonging to the selected product. Palltex
        # renders color-swatch navigation before the product facts, so never
        # search backwards from a verified SKU anchor.
        hi=min(len(lines),sku_index+14)
        for i in range(sku_index,hi):
            v=candidate(i)
            if v:
                return v
        return ""

    # No SKU anchor => conservative fallback.
    for i in range(len(lines)):
        v=candidate(i)
        if v:
            return v
    return ""

_ALPHA_SIZE_RE = re.compile(r"^(?:[2-8]?XS|XS|S|M|L|XL|[2-8]XL|XXL|XXXL|XXXXL)(?:/[A-Z0-9]+)?$", re.I)
_NUM_SIZE_RE = re.compile(r"^\d{2,3}(?:[./-]\d{2,3})?$")

def _valid_size_token(token: str) -> str:
    s = re.sub(r"\s+", "", str(token or "")).upper()
    if not s or len(s) > 16:
        return ""
    if _ALPHA_SIZE_RE.fullmatch(s):
        return s
    if _NUM_SIZE_RE.fullmatch(s):
        nums = [int(x) for x in re.split(r"[./-]", s)]
        if all(20 <= n <= 80 for n in nums):
            return s
    return ""

def _extract_sizes(lines: list[str]) -> tuple[list[str], bool]:
    markers = []
    for i, line in enumerate(lines):
        low = line.lower()
        if "избери размер" in low or re.fullmatch(r"размер\s*:?", low):
            markers.append(i)
    saw_selector = bool(markers)
    found: list[str] = []
    seen = set()
    for start in markers:
        for line in lines[start + 1:start + 35]:
            low = line.lower()
            if "моля изберете размер" in low or "добави в колич" in low or "количество" == low:
                break
            # One line can contain "XS S M"; accept only when every token is size-like.
            parts = [x for x in re.split(r"[\s,;|]+", line) if x]
            if 1 <= len(parts) <= 12:
                vals = [_valid_size_token(x) for x in parts]
                if vals and all(vals):
                    for val in vals:
                        if val not in seen:
                            seen.add(val)
                            found.append(val)
            val = _valid_size_token(line)
            if val and val not in seen:
                seen.add(val)
                found.append(val)
        if found:
            break
    return found, saw_selector

def _product_id_from_url(url: str) -> str:
    m = re.search(r"/(\d+)/?$", urlparse(url).path)
    return m.group(1) if m else ""

def parse_palltex_product_html(html: str, final_url: str, *, image_url: str = "") -> dict:
    _validate_public_host(final_url, resolve=False)
    parser = _TextParser()
    parser.feed(str(html or ""))
    lines = parser.lines
    sku, sku_index = _extract_supplier_reference(lines, parser.jsonld_chunks, final_url=final_url)
    color = _extract_color(lines, sku_index)
    sizes, saw_size_selector = _extract_sizes(lines)

    variants: list[dict] = []
    if sku and (sizes or not saw_size_selector):
        size_rows = [
            {
                "size": size,
                "value": size,
                "availability": "SUPPLIER_VISIBLE",
                "availability_semantics": "EXTERNAL_SUPPLIER_SELECTION_EVIDENCE_NOT_M99_STOCK",
            }
            for size in sizes
        ]
        variants.append(
            {
                "type": "COLOR_SIZE" if sizes else "PRODUCT",
                "value": color or "Selected product",
                "code": sku,
                "source_variant_id": _product_id_from_url(final_url),
                "url": final_url,
                "image_url": str(image_url or ""),
                "sizes": size_rows,
                "availability_semantics": "EXTERNAL_SUPPLIER_EVIDENCE_NOT_M99_PHYSICAL_STOCK",
            }
        )

    return {
        "supplier_reference": sku,
        "color": color,
        "sizes": sizes,
        "saw_size_selector": saw_size_selector,
        "variants": variants,
        "final_url": final_url,
    }

def fetch_and_parse(url: str, *, image_url: str = "") -> dict:
    html, final_url = _fetch_html(url)
    return parse_palltex_product_html(html, final_url, image_url=image_url)

def _field_value(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)

def _replace_result(result, updates: dict):
    if isinstance(result, dict):
        out = dict(result)
        out.update(updates)
        return out
    if is_dataclass(result):
        allowed = {f.name for f in result.__dataclass_fields__.values()}
        return replace(result, **{k: v for k, v in updates.items() if k in allowed})
    if hasattr(result, "_replace"):
        fields = set(getattr(result, "_fields", ()))
        return result._replace(**{k: v for k, v in updates.items() if k in fields})
    sig = None
    try:
        sig = inspect.signature(type(result))
    except Exception:
        pass
    if sig:
        vals = {}
        for name in sig.parameters:
            if name == "self":
                continue
            if name in updates:
                vals[name] = updates[name]
            elif hasattr(result, name):
                vals[name] = getattr(result, name)
        try:
            return type(result)(**vals)
        except Exception:
            pass
    raise PalltexHydrationAdapterError("Unsupported Palltex hydration result type.")

_SOLVABLE = {
    "SUPPLIER_REFERENCE_NOT_FOUND",
    "PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER",
}

def enhance_hydrated_result(result, product_url: str):
    host = _host(product_url)
    if host not in _ALLOWED_HOSTS:
        return result

    images = tuple(_field_value(result, "images", ()) or ())
    image_url = str(images[0] if images else "")
    try:
        parsed = fetch_and_parse(product_url, image_url=image_url)
    except Exception as exc:
        warnings = list(_field_value(result, "warnings", ()) or ())
        marker = "PALLTEX_ADAPTER_READ_FAILED"
        if marker not in warnings:
            warnings.append(marker)
        return _replace_result(result, {
            "warnings": tuple(warnings),
            "hydration_pass": False,
        })

    sku = parsed["supplier_reference"]
    variants = tuple(parsed["variants"])
    saw_size_selector = bool(parsed["saw_size_selector"])
    sizes = list(parsed["sizes"])

    original_warnings = [str(x) for x in (_field_value(result, "warnings", ()) or ())]
    remaining: list[str] = []
    for warning in original_warnings:
        if warning == "SUPPLIER_REFERENCE_NOT_FOUND" and sku:
            continue
        if warning == "PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER":
            parser_valid = bool(variants) and (bool(sizes) or not saw_size_selector)
            if parser_valid:
                continue
        remaining.append(warning)

    # Never turn a different/unknown blocker into PASS.
    original_pass = bool(_field_value(result, "hydration_pass", False))
    only_known_before = all(w in _SOLVABLE for w in original_warnings)
    solved_known = (
        bool(sku)
        and bool(variants)
        and ("SUPPLIER_REFERENCE_NOT_FOUND" not in remaining)
        and ("PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER" not in remaining)
    )
    hydration_pass = original_pass or (only_known_before and solved_known and not remaining)

    updates = {
        "supplier_reference": sku or _field_value(result, "supplier_reference", None),
        "variants": variants or tuple(_field_value(result, "variants", ()) or ()),
        "warnings": tuple(remaining),
        "hydration_pass": bool(hydration_pass),
    }
    return _replace_result(result, updates)

def install_adapter(namespace: dict) -> tuple[str, ...]:
    patched: list[str] = []
    module_name = str(namespace.get("__name__") or "")
    for name, obj in list(namespace.items()):
        if not inspect.isclass(obj) or getattr(obj, "__module__", "") != module_name:
            continue
        original = getattr(obj, "get_product", None)
        if not callable(original):
            continue
        if getattr(original, "_m99_palltex_r7j_adapter", False):
            patched.append(f"{name}.get_product")
            continue

        @functools.wraps(original)
        def wrapped(self, product_url, *args, __original=original, **kwargs):
            result = __original(self, product_url, *args, **kwargs)
            return enhance_hydrated_result(result, product_url)

        wrapped._m99_palltex_r7j_adapter = True
        setattr(obj, "get_product", wrapped)
        patched.append(f"{name}.get_product")

    if not patched:
        raise PalltexHydrationAdapterError("No Palltex get_product class method found to attach adapter.")
    namespace["M99_PALLTEX_ADAPTER_PATCHED"] = tuple(patched)
    return tuple(patched)
