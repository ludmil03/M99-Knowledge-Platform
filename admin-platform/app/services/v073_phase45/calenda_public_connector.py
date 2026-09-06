from __future__ import annotations
import html as html_lib

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
import re

BASE_URL = "https://calenda.bg"
MAX_HTML_BYTES = 5_000_000
USER_AGENT = "M99-Knowledge-Platform/Rev31-Phase4.3-R3.6.1E2"


class CalendaConnectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class SupplierCategory:
    key: str
    label: str
    url: str
    parent_key: str | None = None


@dataclass(frozen=True)
class ProductVariantSummary:
    code: str
    label: str
    url: str


@dataclass(frozen=True)
class ProductSummary:
    source_key: str
    name: str
    url: str
    price_text: str | None = None
    availability_text: str | None = None
    image_url: str | None = None
    supplier_reference: str | None = None
    calenda_product_id: str | None = None
    variants: tuple[ProductVariantSummary, ...] = ()


@dataclass(frozen=True)
class ProductHydration:
    source_key: str
    name: str
    url: str
    supplier_reference: str | None
    brand: str | None
    price_text: str | None
    currency: str | None
    availability_text: str | None
    description: str | None
    images: tuple[str, ...]
    variants: tuple[dict, ...]
    hydration_pass: bool
    warnings: tuple[str, ...]
    calenda_product_id: str | None = None
    selected_variant_code: str | None = None


def _host(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def _safe_url(url: str) -> str:
    if _host(url) != "calenda.bg":
        raise CalendaConnectorError("URL is outside approved calenda.bg domain.")
    return url


def _fetch(url: str, timeout: int = 25) -> tuple[int, str, str]:
    _safe_url(url)
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.7",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            final_url = resp.geturl()
            _safe_url(final_url)
            status = int(getattr(resp, "status", 200))
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype:
                raise CalendaConnectorError(f"Expected HTML, got {ctype or 'unknown'}")
            raw = resp.read(MAX_HTML_BYTES + 1)
    except CalendaConnectorError:
        raise
    except Exception as exc:
        raise CalendaConnectorError(f"Calenda read-only request failed: {exc}") from exc

    if len(raw) > MAX_HTML_BYTES:
        raise CalendaConnectorError("Calenda page exceeds safe HTML discovery size.")
    return status, final_url, raw.decode("utf-8", errors="replace")


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.images: list[str] = []
        self.image_records: list[dict] = []
        self.meta: dict[str, str] = {}
        self._context_stack: list[str] = []
        self._after_related_products = False
        self.variant_records: list[dict] = []
        self._variant_capture: dict | None = None
        self._variant_capture_depth = 0
        self.text_parts: list[str] = []
        self.headings: list[tuple[str, str]] = []
        self._href: str | None = None
        self._anchor_parts: list[str] = []
        self._heading: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        tag = tag.lower()

        attr_blob = " ".join(f"{k}={v}" for k, v in attrs if v is not None)
        color_code = None
        if not self._after_related_products:
            for pattern in (
                r"(?:[?&])color=(\d+)",
                r"(?:^|\s)data-color(?:-id|-code)?=['\"]?(\d+)",
                r"(?:^|\s)data-color=['\"]?(\d+)",
                r"selectColor\(['\"]?(\d+)['\"]?\)",
            ):
                m = re.search(pattern, attr_blob, re.I)
                if m:
                    color_code = m.group(1)
                    break

        if color_code and self._variant_capture is None and tag in {"a", "button", "div", "li", "label", "span"}:
            self._variant_capture = {
                "tag": tag,
                "code": color_code,
                "attrs": dict(attrs),
                "text_parts": [],
                "images": [],
            }
            self._variant_capture_depth = 1
        elif self._variant_capture is not None:
            self._variant_capture_depth += 1

        if tag in {"div", "section", "article", "aside", "main", "li", "figure", "picture", "a"}:
            context = " ".join(
                x for x in (d.get("id", ""), d.get("class", ""), d.get("role", ""))
                if x
            ).strip().lower()
            self._context_stack.append(context)

        if tag == "a":
            self._href = d.get("href")
            self._anchor_parts = []
        if tag in {"h1", "h2", "h3"}:
            self._heading = tag
            self._heading_parts = []
        if tag == "img":
            src = d.get("src") or d.get("data-src") or d.get("data-lazy-src")
            if src:
                self.images.append(src)
                if self._variant_capture is not None:
                    self._variant_capture["images"].append(src)
                self.image_records.append(
                    {
                        "src": src,
                        "alt": " ".join((d.get("alt") or "").split()),
                        "title": " ".join((d.get("title") or "").split()),
                        "context": " ".join(x for x in self._context_stack if x),
                        "after_related": self._after_related_products,
                    }
                )
        if tag == "meta":
            key = (d.get("property") or d.get("name") or "").lower()
            value = d.get("content") or ""
            if key and value:
                self.meta[key] = value

    def handle_endtag(self, tag):
        tag = tag.lower()

        if self._variant_capture is not None:
            self._variant_capture_depth -= 1
            if self._variant_capture_depth <= 0:
                self.variant_records.append(self._variant_capture)
                self._variant_capture = None
                self._variant_capture_depth = 0

        if tag == "a":
            if self._href:
                label = " ".join("".join(self._anchor_parts).split())
                self.links.append((self._href, label))
            self._href = None
            self._anchor_parts = []
        if self._heading == tag:
            label = " ".join("".join(self._heading_parts).split())
            if label:
                self.headings.append((tag, label))
            self._heading = None
            self._heading_parts = []

        if tag in {"div", "section", "article", "aside", "main", "li", "figure", "picture", "a"}:
            if self._context_stack:
                self._context_stack.pop()

    def handle_data(self, data):
        cleaned = " ".join(data.split())
        if cleaned:
            low = cleaned.lower()
            if "свързани продукти" in low or "подобни продукти" in low:
                self._after_related_products = True
            self.text_parts.append(cleaned)
            if self._variant_capture is not None:
                self._variant_capture["text_parts"].append(cleaned)
        if self._href is not None:
            self._anchor_parts.append(data)
        if self._heading is not None:
            self._heading_parts.append(data)

    @property
    def text(self) -> str:
        return "\n".join(self.text_parts)


def _parse(html: str) -> _Parser:
    p = _Parser()
    p.feed(html)
    return p


def _is_category(url: str) -> bool:
    p = urlparse(url)
    return _host(url) == "calenda.bg" and p.path.startswith("/categories/")


def _is_product(url: str) -> bool:
    p = urlparse(url)
    return _host(url) == "calenda.bg" and re.fullmatch(r"/products/\d+/?", p.path) is not None


def _category_key(url: str) -> str:
    return urlparse(url).path.rstrip("/").split("/")[-1]


def _product_id(url: str) -> str:
    return urlparse(url).path.rstrip("/").split("/")[-1]


def _canonical_product_url(url: str) -> str:
    """Same Calenda product identity regardless of ?color=... variant."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path.rstrip("/"), "", "", ""))


def _variant_code(url: str) -> str | None:
    values = parse_qs(urlparse(url).query).get("color") or []
    return values[0].strip() if values and values[0].strip() else None


def _dedupe(items, keyfn):
    seen, out = set(), []
    for item in items:
        k = keyfn(item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


_PRICE_RE = re.compile(
    r"(?P<eur>\d+(?:[.,]\d+)?)\s*€\s*/\s*(?P<bgn>\d+(?:[.,]\d+)?)\s*лв\.\s*без\s*ДДС",
    re.I,
)
_CODE_RE = re.compile(r"(?:КОД|ID)\s*:?\s*([A-Za-zА-Яа-я0-9._/-]+)", re.I)
_STOCK_RE = re.compile(r"(\d+)\s*бр\.", re.I)
_COLOR_RE = re.compile(r"Цвят\s*:\s*([^\n]+)", re.I)
_SUPPLIER_REF_ONLY_RE = re.compile(r"^(?:ID|MF|MFF)?\d+[A-Za-z0-9._/-]*$", re.I)


def _first_price(text: str) -> str | None:
    m = _PRICE_RE.search(text)
    if not m:
        return None
    return m.group("eur").replace(",", ".")


def _availability(text: str) -> str | None:
    quantities = [int(x) for x in _STOCK_RE.findall(text)]
    if not quantities:
        if "по запитване" in text.lower():
            return "ON_REQUEST"
        return None
    total = sum(quantities)
    return f"IN_STOCK ({total} pcs observed)" if total > 0 else "OUT_OF_STOCK"


def _description(text: str) -> str | None:
    marker = "Описание:"
    if marker not in text:
        return None
    tail = text.split(marker, 1)[1]
    stop_words = ("Свързани продукти:", "Подобни продукти", "Добави в количката")
    for stop in stop_words:
        if stop in tail:
            tail = tail.split(stop, 1)[0]
    lines = [x.strip() for x in tail.splitlines() if x.strip()]
    return " ".join(lines[:12])[:4000] or None



_BRAND_INLINE_RE = re.compile(r"Марка\s*:\s*(.+)$", re.I)
_BAD_IMAGE_TOKENS = (
    "logo", "icon", "banner", "sprite", "loader", "flag", "footer", "header",
    "related", "similar", "podob", "svurz", "promo-stars", "promostars",
    "calenda-logo", "click", "cursor",
)
_GALLERY_CONTEXT_TOKENS = (
    "product", "gallery", "image", "images", "thumb", "thumbnail", "slider",
    "carousel", "zoom", "detail", "photo", "photos",
)


def _extract_brand(parts: list[str]) -> str | None:
    """Extract explicit supplier brand evidence, including split 'Марка:' + value nodes."""
    for idx, raw in enumerate(parts):
        part = " ".join((raw or "").split())
        if not part:
            continue
        m = _BRAND_INLINE_RE.search(part)
        if m:
            value = " ".join(m.group(1).split()).strip(" :-")
            if value:
                return value[:200]
        if part.rstrip(":").strip().lower() == "марка":
            for nxt in parts[idx + 1: idx + 5]:
                value = " ".join((nxt or "").split()).strip(" :-")
                if value and value.lower() not in {"допълнителна информация", "описание"}:
                    return value[:200]
    return None


def _clean_variant_label(label: str, code: str) -> str:
    label = " ".join((label or "").split()).strip()
    if not label:
        return f"Color {code}"
    # Calenda may render numeric color id plus human label inside the same anchor.
    label = re.sub(rf"^\s*{re.escape(str(code))}\s*", "", label).strip(" :-")
    return label or f"Color {code}"


def _variants_from_product_page(parser: _Parser, final_url: str) -> tuple[dict, ...]:
    """Discover same-product ?color=... links as variants; never treat related products as variants."""
    canonical = _canonical_product_url(final_url)
    found: dict[str, dict] = {}
    for href, raw_label in parser.links:
        url = urljoin(final_url, href)
        if not _is_product(url):
            continue
        if _canonical_product_url(url) != canonical:
            continue
        code = _variant_code(url)
        if not code:
            continue
        label = _clean_variant_label(raw_label, code)
        current = found.get(code)
        if current is None or current["value"].startswith("Color "):
            found[code] = {
                "type": "COLOR",
                "value": label,
                "code": code,
                "url": url,
            }
    return tuple(
        found[k] for k in sorted(
            found,
            key=lambda x: (int(x) if str(x).isdigit() else 10**12, str(x)),
        )
    )


def _looks_like_bad_image(url: str, alt: str = "", title: str = "", context: str = "") -> bool:
    hay = " ".join((url, alt, title, context)).lower()
    return any(token in hay for token in _BAD_IMAGE_TOKENS)


def _product_images(
    parser: _Parser,
    final_url: str,
    product_name: str,
    supplier_ref: str | None,
) -> tuple[str, ...]:
    """
    Evidence-first image selection.

    1) Keep same-domain og:image as the strongest product-image evidence.
    2) Never include images observed after Related/Similar Products.
    3) Exclude obvious logos/icons/banners/brand graphics.
    4) Add extra images only when gallery/product context or ALT/title ties them to this product.
    """
    candidates: list[str] = []
    og = parser.meta.get("og:image")
    if og:
        full = urljoin(final_url, og)
        if _host(full) == "calenda.bg" and not _looks_like_bad_image(full):
            candidates.append(full)

    name_low = " ".join((product_name or "").split()).lower()
    ref_low = (supplier_ref or "").lower()

    for rec in parser.image_records:
        if rec.get("after_related"):
            continue
        full = urljoin(final_url, rec.get("src") or "")
        if _host(full) != "calenda.bg":
            continue
        alt = rec.get("alt") or ""
        title = rec.get("title") or ""
        context = rec.get("context") or ""
        if _looks_like_bad_image(full, alt, title, context):
            continue

        hay_text = f"{alt} {title}".lower()
        context_low = context.lower()
        strong_identity = bool(
            (name_low and name_low in hay_text)
            or (ref_low and ref_low in hay_text)
        )
        gallery_context = any(token in context_low for token in _GALLERY_CONTEXT_TOKENS)

        # Be conservative: no global-page image collection.
        if strong_identity or gallery_context:
            candidates.append(full)

    return tuple(_dedupe(candidates, lambda x: x))


def _availability_for_hydration(text: str) -> tuple[str, str | None]:
    """
    UNKNOWN is a valid supplier-observation state when the public page exposes no stock.
    It is not converted to zero/out-of-stock and it does not block identity/DRAFT readiness.
    """
    observed = _availability(text)
    if observed:
        return observed, None
    return "UNKNOWN", "AVAILABILITY_NOT_PUBLISHED"



_VARIANT_ATTR_IMAGE_KEYS = (
    "data-image", "data-img", "data-src", "data-photo", "data-picture",
    "data-zoom-image", "data-large-image", "data-original",
)


def _variant_url(base_url: str, code: str, attrs: dict | None = None) -> str:
    attrs = attrs or {}
    href = attrs.get("href") or ""
    if href:
        resolved = urljoin(base_url, href)
        if _is_product(resolved) and _variant_code(resolved):
            return resolved
    p = urlparse(_canonical_product_url(base_url))
    return urlunparse((p.scheme, p.netloc, p.path, "", urlencode({"color": code}), ""))


def _variant_image_from_attrs(base_url: str, attrs: dict, images: list[str]) -> str | None:
    for raw in images:
        full = urljoin(base_url, raw)
        if _host(full) == "calenda.bg" and not _looks_like_bad_image(full):
            return full
    for key in _VARIANT_ATTR_IMAGE_KEYS:
        raw = attrs.get(key)
        if raw:
            full = urljoin(base_url, raw)
            if _host(full) == "calenda.bg" and not _looks_like_bad_image(full):
                return full
    style = attrs.get("style") or ""
    m = re.search(r"background-image\s*:\s*url\(['\"]?([^)'\"]+)", style, re.I)
    if m:
        full = urljoin(base_url, m.group(1))
        if _host(full) == "calenda.bg" and not _looks_like_bad_image(full):
            return full
    return None



def _variants_from_parser_links_and_records(parser: _Parser, final_url: str) -> tuple[dict, ...]:
    """Combine ordinary links and captured data-driven controls into one live-DOM variant set."""
    return _merge_variants(
        _variants_from_product_page(parser, final_url),
        _variants_from_live_controls(parser, final_url),
    )



_TEXTILE_COLORS_BLOCK_RE = re.compile(
    r"(?is)<div\s+id=[\"']textileProductColors[\"'][^>]*>(.*?)</div>\s*</div>\s*<div\s+id=[\"']product-right[\"']"
)
_TEXTILE_COLOR_FORM_RE = re.compile(
    r"(?is)<div\s+class=[\"'][^\"']*\btextile-color\b[^\"']*[\"'][^>]*>\s*<form\b[^>]*method=[\"']?GET[\"']?[^>]*>(.*?)</form>"
)
_COLOR_QUERY_INPUT_RE = re.compile(
    r"(?is)<input\b(?=[^>]*\bname=[\"']color[\"'])(?=[^>]*\bvalue=[\"']([^\"']+)[\"'])[^>]*>"
)
_COLOR_BUTTON_RE = re.compile(r"(?is)<button\b[^>]*>(.*?)</button>")
_COLOR_LABEL_AFTER_BUTTON_RE = re.compile(r"(?is)</button>\s*<div\b[^>]*>(.*?)</div>")


def _strip_tags(value: str) -> str:
    value = re.sub(r"(?is)<[^>]+>", " ", value or "")
    value = html_lib.unescape(value)
    return " ".join(value.split()).strip()


def _variants_from_textile_forms(html: str, final_url: str) -> tuple[dict, ...]:
    """Parse Calenda's exact textile GET-form color structure proven by live diagnostics."""
    m = _TEXTILE_COLORS_BLOCK_RE.search(html)
    block = m.group(1) if m else html

    found: dict[str, dict] = {}
    for fm in _TEXTILE_COLOR_FORM_RE.finditer(block):
        form_html = fm.group(1)
        qm = _COLOR_QUERY_INPUT_RE.search(form_html)
        bm = _COLOR_BUTTON_RE.search(form_html)
        lm = _COLOR_LABEL_AFTER_BUTTON_RE.search(form_html)
        if not qm or not bm:
            continue

        source_variant_id = _strip_tags(qm.group(1))
        visible_code = _strip_tags(bm.group(1))
        label = _strip_tags(lm.group(1)) if lm else ""

        if not re.fullmatch(r"\d+", source_variant_id or ""):
            continue
        if not re.fullmatch(r"\d+", visible_code or ""):
            continue

        base = _canonical_product_url(final_url)
        p = urlparse(base)
        variant_url = urlunparse(
            (p.scheme, p.netloc, p.path, "", urlencode({"color": source_variant_id}), "")
        )

        found[visible_code] = {
            "type": "COLOR",
            "value": label or f"Color {visible_code}",
            "code": visible_code,
            "source_variant_id": source_variant_id,
            "url": variant_url,
            "image_url": None,
        }

    return tuple(
        found[k]
        for k in sorted(found, key=lambda x: (int(x) if x.isdigit() else 10**12, x))
    )


def _requested_variant_matches(variant: dict, requested_variant: str | None) -> bool:
    if not requested_variant:
        return False
    return (
        str(variant.get("source_variant_id") or "") == requested_variant
        or str(variant.get("code") or "") == requested_variant
    )


def _variants_from_live_controls(parser: _Parser, final_url: str) -> tuple[dict, ...]:
    found: dict[str, dict] = {}
    base_id = _product_id(final_url)
    for rec in parser.variant_records:
        code = str(rec.get("code") or "").strip()
        if not code:
            continue
        attrs = rec.get("attrs") or {}
        url = _variant_url(final_url, code, attrs)
        candidate_id = _product_id(url)
        if base_id and candidate_id and candidate_id != base_id:
            continue
        raw_label = " ".join(rec.get("text_parts") or [])
        found[code] = {
            "type": "COLOR",
            "value": _clean_variant_label(raw_label, code),
            "code": code,
            "url": url,
            "image_url": _variant_image_from_attrs(final_url, attrs, rec.get("images") or []),
        }
    return tuple(found[k] for k in sorted(found, key=lambda x: (int(x) if x.isdigit() else 10**12, x)))


def _variants_from_raw_html(html: str, final_url: str) -> tuple[dict, ...]:
    found: dict[str, dict] = {}
    patterns = (
        r'href\s*=\s*["\']([^"\']*[?&]color=(\d+)[^"\']*)["\']',
        r'data-color(?:-id|-code)?\s*=\s*["\']?(\d+)["\']?',
        r'(?:color_id|colorId|variant-color)\s*[:=]\s*["\']?(\d+)["\']?',
    )
    for pat_idx, pattern in enumerate(patterns):
        for m in re.finditer(pattern, html, re.I):
            if pat_idx == 0:
                href, code = m.group(1), m.group(2)
                url = urljoin(final_url, href)
            else:
                code = m.group(1)
                url = _variant_url(final_url, code)
            if code not in found:
                found[code] = {
                    "type": "COLOR",
                    "value": f"Color {code}",
                    "code": code,
                    "url": url,
                    "image_url": None,
                }
    return tuple(found[k] for k in sorted(found, key=lambda x: (int(x) if x.isdigit() else 10**12, x)))


def _merge_variants(*variant_sets: tuple[dict, ...]) -> tuple[dict, ...]:
    found: dict[str, dict] = {}
    for variants in variant_sets:
        for variant in variants:
            code = str(variant.get("code") or "").strip()
            if not code:
                continue
            if code not in found:
                found[code] = dict(variant)
                continue
            current = found[code]
            if (not current.get("value") or str(current["value"]).startswith("Color ")) and variant.get("value"):
                current["value"] = variant["value"]
            if not current.get("source_variant_id") and variant.get("source_variant_id"):
                current["source_variant_id"] = variant["source_variant_id"]
            if not current.get("url") and variant.get("url"):
                current["url"] = variant["url"]
            if not current.get("image_url") and variant.get("image_url"):
                current["image_url"] = variant["image_url"]
    return tuple(found[k] for k in sorted(found, key=lambda x: (int(x) if x.isdigit() else 10**12, x)))


_CALENDA_CAROUSEL_ADD_IMAGE_RE = re.compile(
    r"""(?is)#product_carousel.*?add\.owl\.carousel.*?(?:href|src)=["']([^"']+\.(?:jpg|jpeg|png|webp)(?:\?[^"']*)?)["']"""
)

_CALENDA_TEXTILE_TABLE_IMAGE_RE = re.compile(
    r"""(?is)<table\b[^>]*id=["']textile-color-table["'][^>]*>(.*?)(?:</table>|$)"""
)


def _variant_image_from_html(
    html: str,
    final_url: str,
    supplier_ref: str | None,
    visible_code: str | None,
) -> str | None:
    """
    R3.6.1F evidence rule.

    Calenda's initial #product_carousel keeps the generic product image, while
    the selected textile color's real image is injected later by an inline
    add.owl.carousel script and is also repeated in #textile-color-table.

    Accept only a same-domain image tied to BOTH supplier reference and the
    visible color code. This prevents related/similar product images from
    becoming variant evidence.
    """
    ref = (supplier_ref or "").strip()
    code = (visible_code or "").strip()
    if not ref or not code:
        return None

    expected = f"{ref}_{code}".lower()
    candidates: list[str] = []

    for m in _CALENDA_CAROUSEL_ADD_IMAGE_RE.finditer(html):
        full = urljoin(final_url, html_lib.unescape(m.group(1)))
        if _host(full) == "calenda.bg" and expected in full.lower() and not _looks_like_bad_image(full):
            candidates.append(full)

    table = _CALENDA_TEXTILE_TABLE_IMAGE_RE.search(html)
    if table:
        for m in re.finditer(
            r"""(?is)<img\b[^>]*\bsrc=["']([^"']+\.(?:jpg|jpeg|png|webp)(?:\?[^"']*)?)["']""",
            table.group(1),
        ):
            full = urljoin(final_url, html_lib.unescape(m.group(1)))
            if _host(full) == "calenda.bg" and expected in full.lower() and not _looks_like_bad_image(full):
                candidates.append(full)

    deduped = _dedupe(candidates, lambda x: x)
    return deduped[0] if deduped else None



_TAG_RE = re.compile(r"(?is)<[^>]+>")
_TD_RE = re.compile(r"(?is)<td\b[^>]*>(.*?)</td>")
_TR_RE = re.compile(r"(?is)<tr\b[^>]*>(.*?)</tr>")
_QTY_RE = re.compile(r"(-?\d+)\s*бр\.", re.I)


def _cell_text(fragment: str) -> str:
    text = _TAG_RE.sub(" ", fragment)
    return " ".join(html_lib.unescape(text).split())


def _first_qty(fragment: str) -> int | None:
    m = _QTY_RE.search(_cell_text(fragment))
    return int(m.group(1)) if m else None


_SIZE_PRICE_RE = re.compile(
    r"(?P<eur>\d+(?:[.,]\d+)?)\s*€(?:\s*/?\s*(?P<bgn>\d+(?:[.,]\d+)?)\s*лв\.?)?",
    re.I,
)


def _first_size_price(text: str) -> str | None:
    """
    Calenda textile size rows publish EUR first and BGN on the next HTML line:
        20.40 &euro; <br/> 39.90 лв.
    After HTML normalization there may be no slash between the currencies.
    For canonical supplier evidence we therefore anchor on the explicit EUR
    amount and treat BGN as optional corroborating text.

    This parser is intentionally local to size-row evidence. Product-level
    price parsing remains unchanged.
    """
    m = _SIZE_PRICE_RE.search(text)
    if not m:
        return None
    return m.group("eur").replace(",", ".")


def _size_availability_from_html(
    html: str,
    supplier_ref: str | None,
    visible_code: str | None,
) -> tuple[dict, ...]:
    """
    R3.6.2 supplier evidence parser.

    Calenda textile variant pages expose a table with columns:
      image | size | price | Varna | 1-2 working days | 7-10 working days | quantity

    We capture the three supplier availability buckets exactly as published.
    They are supplier observations and MUST NOT be treated as M99-owned stock.
    """
    ref = (supplier_ref or "").strip()
    code = (visible_code or "").strip()
    if not ref or not code:
        return ()

    table_m = _CALENDA_TEXTILE_TABLE_IMAGE_RE.search(html)
    if not table_m:
        return ()

    expected_image_token = f"{ref}_{code}".lower()
    records: list[dict] = []

    for tr in _TR_RE.findall(table_m.group(1)):
        cells = _TD_RE.findall(tr)
        if len(cells) < 6:
            continue

        # A valid size row for the selected color repeats that color's product image.
        image_match = re.search(
            r"""(?is)<img\b[^>]*\bsrc=["']([^"']+)["']""",
            cells[0],
        )
        if not image_match or expected_image_token not in html_lib.unescape(image_match.group(1)).lower():
            continue

        size = _cell_text(cells[1]).strip()
        if not size:
            continue

        price = _first_size_price(_cell_text(cells[2]))
        varna = _first_qty(cells[3])
        delivery_1_2 = _first_qty(cells[4])
        delivery_7_10 = _first_qty(cells[5])

        # Exact quantities only when explicitly published.
        if varna is None or delivery_1_2 is None or delivery_7_10 is None:
            continue

        total = varna + delivery_1_2 + delivery_7_10
        records.append({
            "size": size,
            "price_eur": price,
            "supplier_availability": {
                "varna_qty": varna,
                "delivery_1_2_days_qty": delivery_1_2,
                "delivery_7_10_days_qty": delivery_7_10,
                "total_observed_qty": total,
                "status": "IN_STOCK" if total > 0 else "OUT_OF_STOCK",
                "evidence_scope": "SUPPLIER",
                "counts_as_m99_owned_stock": False,
            },
        })

    return tuple(records)


def _summarize_size_availability(records: tuple[dict, ...]) -> dict | None:
    if not records:
        return None
    varna = sum(int(r["supplier_availability"]["varna_qty"]) for r in records)
    d12 = sum(int(r["supplier_availability"]["delivery_1_2_days_qty"]) for r in records)
    d710 = sum(int(r["supplier_availability"]["delivery_7_10_days_qty"]) for r in records)
    total = varna + d12 + d710
    return {
        "sizes_observed": len(records),
        "varna_qty": varna,
        "delivery_1_2_days_qty": d12,
        "delivery_7_10_days_qty": d710,
        "total_observed_qty": total,
        "status": "IN_STOCK" if total > 0 else "OUT_OF_STOCK",
        "evidence_scope": "SUPPLIER",
        "counts_as_m99_owned_stock": False,
    }


def _hydrate_variant_images(
    variants: tuple[dict, ...],
    base_name: str,
    supplier_ref: str | None,
) -> tuple[dict, ...]:
    enriched: list[dict] = []
    for variant in variants:
        item = dict(variant)
        if item.get("image_url"):
            enriched.append(item)
            continue
        url = item.get("url")
        if not url:
            enriched.append(item)
            continue
        try:
            status, final_url, html = _fetch(url)
            if status == 200:
                visible_code = str(item.get("code") or "")

                # R3.6.1F: selected-color evidence outranks the generic
                # server-rendered product carousel image.
                variant_img = _variant_image_from_html(
                    html,
                    final_url,
                    supplier_ref,
                    visible_code,
                )
                if variant_img:
                    item["image_url"] = variant_img
                else:
                    # Compatibility fallback for non-textile / older pages.
                    p = _parse(html)
                    imgs = _product_images(p, final_url, base_name, supplier_ref)
                    if imgs:
                        item["image_url"] = imgs[0]

                # R3.6.2: exact supplier evidence by color x size.
                size_records = _size_availability_from_html(
                    html,
                    supplier_ref,
                    visible_code,
                )
                if size_records:
                    item["sizes"] = size_records
                    item["supplier_availability"] = _summarize_size_availability(size_records)
        except CalendaConnectorError:
            pass
        enriched.append(item)
    return tuple(enriched)


def _looks_like_reference(label: str) -> bool:
    label = " ".join((label or "").split())
    return bool(label and _SUPPLIER_REF_ONLY_RE.fullmatch(label))


def _looks_like_title(label: str) -> bool:
    label = " ".join((label or "").split())
    if not label:
        return False
    if _looks_like_reference(label):
        return False
    if label.lower().startswith("calenda product "):
        return False
    if label.isdigit():
        return False
    return any(ch.isalpha() for ch in label)


def _best_title(labels: list[str], product_id: str) -> str:
    candidates = [" ".join(x.split()) for x in labels if _looks_like_title(x)]
    if not candidates:
        return f"Product {product_id}"
    # Product titles are normally the most descriptive text among same-product links.
    return max(candidates, key=lambda x: (len(x), x))


def _best_reference(labels: list[str]) -> str | None:
    refs = [" ".join(x.split()) for x in labels if _looks_like_reference(x)]
    return refs[0] if refs else None


def _group_product_links(html: str, final_url: str) -> list[ProductSummary]:
    """
    R3.4 identity rule:
    /products/34408 and /products/34408?color=317 are ONE supplier product.
    The query-string entries become variants under the canonical product row.
    """
    p = _parse(html)
    groups: dict[str, dict] = {}

    for href, raw_label in p.links:
        url = urljoin(final_url, href)
        if not _is_product(url):
            continue

        base_url = _canonical_product_url(url)
        pid = _product_id(base_url)
        group = groups.setdefault(
            base_url,
            {
                "product_id": pid,
                "labels": [],
                "variant_urls": {},
            },
        )

        label = " ".join((raw_label or "").split())
        if label:
            group["labels"].append(label)

        code = _variant_code(url)
        if code:
            current = group["variant_urls"].get(code)
            # Prefer a label when Calenda exposes one; otherwise keep deterministic fallback.
            candidate_label = label if _looks_like_title(label) else ""
            if current is None or (candidate_label and not current["label"]):
                group["variant_urls"][code] = {
                    "url": url,
                    "label": candidate_label,
                }

    output: list[ProductSummary] = []
    for base_url, group in groups.items():
        pid = group["product_id"]
        name = _best_title(group["labels"], pid)
        supplier_reference = _best_reference(group["labels"])

        variants: list[ProductVariantSummary] = []
        for code, data in group["variant_urls"].items():
            label = data["label"] or f"Color {code}"
            variants.append(
                ProductVariantSummary(
                    code=str(code),
                    label=label,
                    url=data["url"],
                )
            )
        variants.sort(key=lambda v: (int(v.code) if v.code.isdigit() else 10**12, v.code))

        output.append(
            ProductSummary(
                source_key=pid,
                name=name,
                url=base_url,
                supplier_reference=supplier_reference,
                calenda_product_id=pid,
                variants=tuple(variants),
            )
        )

    output.sort(key=lambda x: (x.name.lower(), x.calenda_product_id or ""))
    return output



def _variant_evidence_summary(variants) -> dict:
    """Summarize exact supplier evidence without converting it to M99-owned stock."""
    prices: list[float] = []
    size_rows = 0
    availability_rows = 0
    positive_rows = 0

    for variant in variants or ():
        for row in (variant.get("sizes") or ()):
            size_rows += 1
            price = row.get("price_eur")
            if price not in (None, ""):
                try:
                    prices.append(float(str(price).replace(",", ".")))
                except ValueError:
                    pass

            ev = row.get("supplier_availability") or {}
            keys = ("varna_qty", "delivery_1_2_days_qty", "delivery_7_10_days_qty")
            if all(isinstance(ev.get(k), int) and ev.get(k) >= 0 for k in keys):
                availability_rows += 1
                total = ev.get("total_observed_qty")
                if isinstance(total, int) and total > 0:
                    positive_rows += 1

    unique_prices = sorted(set(prices))
    return {
        "size_rows": size_rows,
        "priced_rows": len(prices),
        "availability_rows": availability_rows,
        "positive_rows": positive_rows,
        "unique_prices": unique_prices,
        "has_price_evidence": bool(prices),
        "has_availability_evidence": availability_rows > 0,
    }


def _product_price_from_variant_evidence(summary: dict) -> str | None:
    prices = summary.get("unique_prices") or []
    if not prices:
        return None
    low, high = min(prices), max(prices)
    return f"{low:.2f}" if low == high else f"FROM {low:.2f}"


def _availability_from_variant_evidence(summary: dict) -> str | None:
    if not summary.get("has_availability_evidence"):
        return None
    return "AVAILABLE BY VARIANT" if summary.get("positive_rows", 0) > 0 else "OUT OF STOCK BY VARIANT"

class CalendaPublicConnector:
    """
    Supplier-specific read-only connector using the proven STENSO contract:
      health_check -> list_categories -> list_products -> get_product

    R3.4:
      product names + explicit IDs + grouping of ?color=... variants.
    """

    def __init__(self, base_url: str = BASE_URL):
        normalized = base_url.rstrip("/")
        if _host(normalized) != "calenda.bg":
            raise CalendaConnectorError("Calenda connector requires calenda.bg base URL.")
        self.base_url = normalized

    def health_check(self) -> dict:
        status, final_url, html = _fetch(self.base_url + "/")
        return {
            "ok": status == 200,
            "status": status,
            "url": final_url,
            "bytes": len(html.encode("utf-8")),
        }

    def list_categories(self) -> list[SupplierCategory]:
        status, final_url, html = _fetch(self.base_url + "/")
        if status != 200:
            raise CalendaConnectorError(f"Calenda root returned HTTP {status}.")
        p = _parse(html)
        categories = []
        for href, label in p.links:
            url = urljoin(final_url, href)
            if not _is_category(url):
                continue
            label = " ".join(label.split())
            if not label:
                slug = _category_key(url)
                label = slug.rsplit("-", 1)[0].replace("-", " ").strip().title()
            categories.append(
                SupplierCategory(
                    key=_category_key(url),
                    label=label,
                    url=url,
                    parent_key=None,
                )
            )
        categories = _dedupe(categories, lambda x: x.url.rstrip("/"))
        categories.sort(key=lambda x: x.label.lower())
        return categories

    def list_products(self, category: str | SupplierCategory) -> list[ProductSummary]:
        if isinstance(category, SupplierCategory):
            category_url = category.url
        elif category.startswith("http://") or category.startswith("https://"):
            category_url = category
        else:
            matches = [c for c in self.list_categories() if c.key == category]
            if not matches:
                raise CalendaConnectorError(f"Unknown Calenda category key: {category}")
            category_url = matches[0].url

        _safe_url(category_url)
        status, final_url, html = _fetch(category_url)
        if status != 200:
            raise CalendaConnectorError(f"Calenda category returned HTTP {status}.")

        return _group_product_links(html, final_url)

    def get_product(self, product_url: str) -> ProductHydration:
        _safe_url(product_url)
        if not _is_product(product_url):
            raise CalendaConnectorError("Selected URL is not a Calenda product URL (/products/<id>).")

        requested_variant = _variant_code(product_url)
        status, final_url, html = _fetch(product_url)
        if status != 200:
            raise CalendaConnectorError(f"Calenda product returned HTTP {status}.")
        p = _parse(html)
        text = p.text

        h1 = next((label for tag, label in p.headings if tag == "h1"), "")
        name = h1 or p.meta.get("og:title", "").strip()
        code_match = _CODE_RE.search(text)
        supplier_ref = code_match.group(1).strip() if code_match else None
        price = _first_price(text)
        availability, availability_warning = _availability_for_hydration(text)
        description = _description(text)
        brand = _extract_brand(p.text_parts)

        variants = _variants_from_textile_forms(html, final_url)
        if not variants:
            variants = _merge_variants(
                _variants_from_product_page(p, final_url),
                _variants_from_live_controls(p, final_url),
                _variants_from_raw_html(html, final_url),
            )

        if requested_variant and not any(_requested_variant_matches(v, requested_variant) for v in variants):
            variants = _merge_variants(
                variants,
                ({
                    "type": "COLOR",
                    "value": f"Color {requested_variant}",
                    "code": requested_variant,
                    "source_variant_id": requested_variant,
                    "url": product_url,
                    "image_url": None,
                },),
            )

        variants = _hydrate_variant_images(variants, name, supplier_ref)

        # R3.7R3: Calenda can omit a product-level price/availability while
        # publishing stronger exact Color x Size evidence. Use that evidence
        # for the operator hydration gate without flattening supplier stock.
        variant_evidence = _variant_evidence_summary(variants)
        if not price and variant_evidence["has_price_evidence"]:
            price = _product_price_from_variant_evidence(variant_evidence)
        if (not availability or availability == "UNKNOWN") and variant_evidence["has_availability_evidence"]:
            availability = _availability_from_variant_evidence(variant_evidence)
            availability_warning = None

        imgs = _product_images(p, final_url, name, supplier_ref)

        warnings = []
        if not name:
            warnings.append("TITLE_NOT_FOUND")
        if not supplier_ref:
            warnings.append("SUPPLIER_REFERENCE_NOT_FOUND")
        if not price:
            warnings.append("PRICE_NOT_FOUND")
        if availability_warning:
            warnings.append(availability_warning)
        if not description:
            warnings.append("DESCRIPTION_NOT_FOUND")
        if not brand:
            warnings.append("BRAND_NOT_FOUND")
        if not imgs:
            warnings.append("PRODUCT_IMAGES_NOT_FOUND")
        if not variants:
            warnings.append("VARIANTS_NOT_DETECTED")
        else:
            if any(not v.get("image_url") for v in variants):
                warnings.append("VARIANT_IMAGE_NOT_FOUND")
            if not any(v.get("sizes") for v in variants):
                warnings.append("SIZE_AVAILABILITY_NOT_FOUND")

        # R3.6: UNKNOWN supplier availability is valid evidence state, never zero.
        # Variants/brand remain visible warnings if the supplier page truly does not expose them.
        hydration_pass = bool(
            name
            and supplier_ref
            and price
            and description
            and imgs
            and (
                not variants
                or variant_evidence["has_availability_evidence"]
            )
        )
        calenda_product_id = _product_id(final_url)

        return ProductHydration(
            source_key=calenda_product_id,
            name=name,
            url=final_url,
            supplier_reference=supplier_ref,
            brand=brand,
            price_text=price,
            currency="EUR" if price else None,
            availability_text=availability,
            description=description,
            images=tuple(imgs),
            variants=tuple(variants),
            hydration_pass=hydration_pass,
            warnings=tuple(warnings),
            calenda_product_id=calenda_product_id,
            selected_variant_code=next(
                (str(v.get("code")) for v in variants if _requested_variant_matches(v, requested_variant)),
                requested_variant,
            ),
        )
