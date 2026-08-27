from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
from threading import Lock
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

UA = "M99KnowledgePlatform/0.7.3-phase45 (+controlled supplier read; no write)"
PRICE_RE = re.compile(r"\b\d{1,5}(?:[.,]\d{2})?\s*(?:лв\.?|€|EUR)\b", re.I)
REF_PATTERNS = (
    re.compile(r"(?:Арт\.?\s*№|Арт(?:икул)?(?:ен)?\s*№|Код|Референтен\s*номер|Reference|Ref\.?)\s*[:#]?\s*([0-9A-Za-z._/-]{4,40})", re.I),
    re.compile(r"\b(0[0-9]{7})\b"),
)
SIZE_RE = re.compile(r"^(3[4-9]|4[0-9]|5[0-2])$")

class SupplierReadError(RuntimeError):
    pass

_CACHE_TTL_SECONDS = 600
_HYDRATION_CACHE = {}
_HYDRATION_CACHE_LOCK = Lock()

def _cache_get(url: str):
    now = time.time()
    with _HYDRATION_CACHE_LOCK:
        item = _HYDRATION_CACHE.get(url)
        if not item:
            return None
        created, data = item
        if now - created > _CACHE_TTL_SECONDS:
            _HYDRATION_CACHE.pop(url, None)
            return None
        return dict(data)

def _cache_put(url: str, data: dict):
    with _HYDRATION_CACHE_LOCK:
        _HYDRATION_CACHE[url] = (time.time(), dict(data))

def clear_hydration_cache():
    with _HYDRATION_CACHE_LOCK:
        _HYDRATION_CACHE.clear()

def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def same_host(url: str, base_url: str) -> bool:
    return urlparse(url).netloc.lower().split(":")[0] == urlparse(base_url).netloc.lower().split(":")[0]

def fetch_html(url: str, timeout: float = 20.0) -> tuple[str, str, int]:
    url = normalize_url(url)
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "bg,en;q=0.8",
            },
        ) as client:
            response = client.get(url)
            if response.status_code >= 400:
                raise SupplierReadError(f"HTTP {response.status_code}")
            ctype = (response.headers.get("content-type") or "").lower()
            if "html" not in ctype and "text" not in ctype:
                raise SupplierReadError(f"Unexpected content-type: {ctype}")
            return str(response.url), response.text, response.status_code
    except httpx.HTTPError as exc:
        raise SupplierReadError(str(exc)) from exc

def page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text(" ", strip=True):
        return h1.get_text(" ", strip=True)[:500]
    if soup.title:
        return soup.title.get_text(" ", strip=True)[:500]
    return ""

def detect_stenso_supplier_ref(text: str) -> str:
    for pattern in REF_PATTERNS:
        match = pattern.search(text or "")
        if match:
            return match.group(1).strip()
    return ""

def classify_page(url: str, soup: BeautifulSoup) -> str:
    path = urlparse(url).path.lower()
    if "/produkt/" in path or soup.select_one('[itemtype*="Product"], .product-info, .product-prices'):
        return "product"
    if re.search(r"/\d+[-_/]", path) or soup.select(".product-miniature, .product-container, article.product-miniature"):
        return "category"
    return "unknown"

def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()

def _absolute(final_url: str, value: str | None) -> str:
    return urljoin(final_url, value or "")

def extract_product_links(final_url: str, soup: BeautifulSoup, limit: int = 200) -> list[dict]:
    host = urlparse(final_url).netloc.lower()
    found: dict[str, dict] = {}
    selectors = (
        "a.product-thumbnail", "a.product-name", "h2.product-title a", "h3.product-title a",
        ".product-miniature a[href]", "article.product-miniature a[href]",
        ".product-container a[href]",
    )
    for selector in selectors:
        for anchor in soup.select(selector):
            href = anchor.get("href")
            if not href:
                continue
            url = urljoin(final_url, href).split("#", 1)[0]
            if urlparse(url).netloc.lower() != host:
                continue
            path = urlparse(url).path.lower()
            if "/produkt/" not in path and "/product/" not in path:
                continue
            title = _clean_text(anchor.get("title") or anchor.get_text(" ", strip=True))
            found.setdefault(url, {"url": url, "title": title[:500]})
            if len(found) >= limit:
                return list(found.values())

    if not found:
        for anchor in soup.find_all("a", href=True):
            url = urljoin(final_url, anchor["href"]).split("#", 1)[0]
            if urlparse(url).netloc.lower() != host:
                continue
            if "/produkt/" not in urlparse(url).path.lower():
                continue
            title = _clean_text(anchor.get("title") or anchor.get_text(" ", strip=True))
            found.setdefault(url, {"url": url, "title": title[:500]})
            if len(found) >= limit:
                break
    return list(found.values())

def _product_price(soup: BeautifulSoup, text: str) -> str:
    for selector, attr in (
        ('[itemprop="price"]', "content"),
        ('meta[property="product:price:amount"]', "content"),
        ('.current-price [itemprop="price"]', "content"),
    ):
        node = soup.select_one(selector)
        if node:
            raw = node.get(attr) or node.get_text(" ", strip=True)
            if raw:
                currency = ""
                currency_node = soup.select_one('[itemprop="priceCurrency"]')
                if currency_node:
                    currency = currency_node.get("content") or currency_node.get_text(" ", strip=True)
                return _clean_text(f"{raw} {currency}")
    for selector in (".current-price", ".product-price", ".price", ".product-prices"):
        node = soup.select_one(selector)
        if node:
            match = PRICE_RE.search(node.get_text(" ", strip=True))
            if match:
                return _clean_text(match.group(0))
    match = PRICE_RE.search(text)
    return _clean_text(match.group(0)) if match else ""

def _product_images(final_url: str, soup: BeautifulSoup, product_name: str) -> list[str]:
    urls: list[str] = []
    selectors = (
        '[data-image-large-src]',
        '.product-cover img',
        '.product-images img',
        '.images-container img',
        '.product-left-column img',
        '[itemprop="image"]',
    )
    for selector in selectors:
        for node in soup.select(selector):
            values = (
                node.get("data-image-large-src"),
                node.get("data-large-src"),
                node.get("data-src"),
                node.get("src"),
                node.get("content"),
            )
            for raw in values:
                if not raw:
                    continue
                url = _absolute(final_url, raw)
                low = url.lower()
                if any(x in low for x in ("logo", "icon", "cart", "search", "phone", "sprite")):
                    continue
                if url not in urls:
                    urls.append(url)
    if not urls:
        wanted = product_name.casefold()
        for img in soup.find_all("img"):
            alt = _clean_text(img.get("alt") or "").casefold()
            if wanted and wanted[:20] not in alt and alt not in wanted:
                continue
            raw = img.get("data-src") or img.get("src")
            if raw:
                url = _absolute(final_url, raw)
                if url not in urls:
                    urls.append(url)
    return urls[:20]

def _description_and_specs(soup: BeautifulSoup) -> tuple[str, list[dict]]:
    candidates = []
    for selector in (
        '#description', '.product-description', '.product-information .tab-content',
        '[id*="description"]', '.description', '.product-features',
    ):
        for node in soup.select(selector):
            text = "\n".join(
                _clean_text(x)
                for x in node.stripped_strings
                if _clean_text(x)
            )
            if len(text) >= 40:
                candidates.append(text)
    # Prefer the longest meaningful product content block.
    description = max(candidates, key=len) if candidates else ""
    description = description[:12000]

    specs: list[dict] = []
    seen = set()

    for row in soup.select("table tr"):
        cells = [_clean_text(x.get_text(" ", strip=True)) for x in row.find_all(["th", "td"])]
        if len(cells) >= 2 and cells[0] and cells[1]:
            key = cells[0][:200]
            value = cells[1][:1000]
            pair = (key.casefold(), value.casefold())
            if pair not in seen:
                specs.append({"name": key, "value": value})
                seen.add(pair)

    source = description or "\n".join(_clean_text(x) for x in soup.stripped_strings)

    # STENSO descriptions often render technical fields as plain text in one
    # HTML text node (for example: "... САЯ: ... ПОДПЛАТА: ...").  Splitting
    # only on newlines therefore merges the prose and all fields into one bad
    # specification.  Detect uppercase field labels followed by ':' and slice
    # each value up to the next label.  This also works when the source keeps
    # the original line breaks.
    label_re = re.compile(
        r"(?<![\wА-Яа-я])([A-ZА-Я][A-ZА-Я0-9 .()/_+\-]{0,79}):\s*",
        re.UNICODE,
    )
    matches = list(label_re.finditer(source))
    for index, match in enumerate(matches):
        name = _clean_text(match.group(1))
        value_start = match.end()
        value_end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        value = _clean_text(source[value_start:value_end])
        if 1 <= len(name) <= 100 and value:
            pair = (name.casefold(), value.casefold())
            if pair not in seen:
                specs.append({"name": name[:200], "value": value[:1000]})
                seen.add(pair)

    return description, specs[:50]

def _size_label(node: Tag) -> str:
    values = [
        node.get_text(" ", strip=True),
        node.get("data-size"),
        node.get("data-value"),
        node.get("title"),
        node.get("aria-label"),
    ]
    # Input values can be internal IDs, so consider `value` last.
    if node.name in {"option", "button"}:
        values.append(node.get("value"))
    for raw in values:
        raw = _clean_text(raw or "")
        match = re.search(r"\b(3[4-9]|4[0-9]|5[0-2])\b", raw)
        if match:
            return match.group(1)
    return ""

def _availability_evidence(node: Tag) -> tuple[str, list[str]]:
    evidence: list[str] = []
    chain = [node]
    parent = node.parent if isinstance(node.parent, Tag) else None
    if parent:
        chain.append(parent)
        grand = parent.parent if isinstance(parent.parent, Tag) else None
        if grand:
            chain.append(grand)

    blob_parts = []
    disabled = False
    explicit_available = False

    for item in chain:
        classes = " ".join(item.get("class") or [])
        attrs = {
            "class": classes,
            "aria-disabled": item.get("aria-disabled"),
            "disabled": "disabled" if item.has_attr("disabled") else None,
            "data-available": item.get("data-available"),
            "data-stock": item.get("data-stock"),
            "data-in-stock": item.get("data-in-stock"),
            "style": item.get("style"),
        }
        blob = " ".join(str(v) for v in attrs.values() if v).casefold()
        blob_parts.append(blob)
        if item.has_attr("disabled") or (item.get("aria-disabled") or "").casefold() == "true":
            disabled = True
            evidence.append("disabled/aria-disabled")
        da = str(item.get("data-available") or item.get("data-stock") or item.get("data-in-stock") or "").casefold()
        if da in {"0", "false", "no", "out", "out_of_stock"}:
            disabled = True
            evidence.append("data stock=false")
        if da in {"1", "true", "yes", "in", "in_stock"}:
            explicit_available = True
            evidence.append("data stock=true")

    blob = " ".join(blob_parts)
    unavailable_tokens = (
        "disabled", "unavailable", "not-available", "not_available", "out-of-stock",
        "out_of_stock", "sold-out", "sold_out", "no-stock", "nostock",
    )
    available_tokens = ("in-stock", "in_stock", "available", "active", "selected")

    if any(token in blob for token in unavailable_tokens):
        disabled = True
        evidence.append("unavailable CSS/state token")

    # Stenso visual fallback: disabled sizes are rendered pale/grey. We only use
    # inline semantic visual state as fallback; no screenshot/color guessing.
    style_match = re.search(r"opacity\s*:\s*(0(?:\.\d+)?|1(?:\.0+)?)", blob)
    if style_match:
        try:
            opacity = float(style_match.group(1))
            if opacity < 0.75:
                disabled = True
                evidence.append(f"opacity={opacity}")
        except ValueError:
            pass
    if "pointer-events:none" in blob.replace(" ", ""):
        disabled = True
        evidence.append("pointer-events:none")

    if disabled:
        return "OUT_OF_STOCK", evidence
    if explicit_available or any(token in blob for token in available_tokens):
        return "IN_STOCK", evidence or ["available CSS/state token"]
    # A selectable size control without disabled evidence is treated as available.
    if node.name in {"button", "label", "option"} or node.get("role") == "button":
        return "IN_STOCK", ["selectable size control, no disabled evidence"]
    return "UNKNOWN", evidence

def _variants(soup: BeautifulSoup) -> list[dict]:
    selectors = (
        'button', 'label', 'option', '[role="button"]',
        '[data-size]', '[data-value]',
    )
    found: dict[str, dict] = {}
    for selector in selectors:
        for node in soup.select(selector):
            size = _size_label(node)
            if not size or not SIZE_RE.match(size):
                continue
            status, evidence = _availability_evidence(node)
            item = {
                "type": "SIZE",
                "value": size,
                "availability": status,
                "source_disabled": status == "OUT_OF_STOCK",
                "evidence": evidence,
            }
            existing = found.get(size)
            # OUT_OF_STOCK evidence wins over ambiguous/available duplicate controls.
            if existing is None or status == "OUT_OF_STOCK":
                found[size] = item
    return [found[key] for key in sorted(found, key=int)]

def hydrate_stenso_product(url: str, supplier_base_url: str = "https://stenso.net", use_cache: bool = True) -> dict:
    url = normalize_url(url)
    if use_cache:
        cached = _cache_get(url)
        if cached is not None:
            cached["cache_status"] = "HIT"
            return cached
    final_url, html, http = fetch_html(url)
    if supplier_base_url and not same_host(final_url, supplier_base_url):
        raise SupplierReadError("URL host does not match selected supplier.")

    soup = BeautifulSoup(html, "html.parser")
    text = _clean_text(soup.get_text(" ", strip=True))
    reference = detect_stenso_supplier_ref(text)
    raw_name = page_title(soup)
    name = raw_name
    if reference:
        name = re.sub(rf"\s+{re.escape(reference)}\s*$", "", raw_name).strip() or raw_name

    description, specifications = _description_and_specs(soup)
    variants = _variants(soup)
    statuses = {v["availability"] for v in variants}
    if variants and statuses == {"OUT_OF_STOCK"}:
        availability = "OUT_OF_STOCK"
    elif "OUT_OF_STOCK" in statuses and "IN_STOCK" in statuses:
        availability = "PARTIAL_VARIANT_AVAILABILITY"
    elif "IN_STOCK" in statuses:
        availability = "IN_STOCK"
    else:
        low = text.casefold()
        if "изчерпан" in low or "out of stock" in low:
            availability = "OUT_OF_STOCK"
        elif "в наличност" in low or "in stock" in low:
            availability = "IN_STOCK"
        else:
            availability = "UNKNOWN"

    return {
        "url": final_url,
        "http": http,
        "title": name,
        "supplier_reference": reference,
        "price_text": _product_price(soup, text),
        "availability_text": availability,
        "images": _product_images(final_url, soup, name),
        "description": description,
        "specifications": specifications,
        "variants": variants,
        "hydration_status": "PASS",
        "hydration_error": "",
    }

def _hydrate_one(item: dict, supplier_base_url: str) -> dict:
    try:
        detail = hydrate_stenso_product(item["url"], supplier_base_url)
        # Preserve discovered title as fallback only.
        if not detail.get("title"):
            detail["title"] = item.get("title") or ""
        return detail
    except Exception as exc:
        return {
            **item,
            "supplier_reference": "",
            "price_text": "",
            "availability_text": "UNKNOWN",
            "images": [],
            "description": "",
            "specifications": [],
            "variants": [],
            "hydration_status": "FAIL",
            "hydration_error": str(exc),
        }

def hydrate_stenso_products(items: list[dict], supplier_base_url: str, max_workers: int = 6) -> list[dict]:
    if not items:
        return []
    results: list[dict | None] = [None] * len(items)
    with ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as executor:
        future_map = {
            executor.submit(_hydrate_one, item, supplier_base_url): index
            for index, item in enumerate(items)
        }
        for future in as_completed(future_map):
            results[future_map[future]] = future.result()
    return [x for x in results if x is not None]

def inspect_supplier_page(url: str, supplier_base_url: str) -> dict:
    final_url, html, http = fetch_html(url)
    if supplier_base_url and not same_host(final_url, supplier_base_url):
        raise SupplierReadError("URL host does not match selected supplier.")

    soup = BeautifulSoup(html, "html.parser")
    typ = classify_page(final_url, soup)
    title = page_title(soup)
    text = soup.get_text(" ", strip=True)
    result = {
        "url": final_url,
        "http": http,
        "type": typ,
        "title": title,
        "supplier_reference": "",
        "products": [],
        "hydration_total": 0,
        "hydration_pass": 0,
        "hydration_fail": 0,
    }

    is_stenso = "stenso.net" in urlparse(supplier_base_url or final_url).netloc.lower()

    if typ == "product":
        if is_stenso:
            detail = hydrate_stenso_product(final_url, supplier_base_url)
            result["supplier_reference"] = detail["supplier_reference"]
            result["products"] = [detail]
        else:
            result["supplier_reference"] = detect_stenso_supplier_ref(text)
            result["products"] = [{
                "url": final_url, "title": title,
                "supplier_reference": result["supplier_reference"],
                "hydration_status": "NOT_IMPLEMENTED",
            }]
    elif typ == "category":
        links = extract_product_links(final_url, soup)
        result["products"] = [
            {
                **item,
                "supplier_reference": "",
                "price_text": "",
                "availability_text": "UNKNOWN",
                "images": [],
                "description": "",
                "specifications": [],
                "variants": [],
                "hydration_status": "WAITING" if is_stenso else "NOT_IMPLEMENTED",
                "hydration_error": "",
                "cache_status": "NONE",
            }
            for item in links
        ]

    result["hydration_total"] = len(result["products"])
    result["hydration_pass"] = sum(1 for p in result["products"] if p.get("hydration_status") == "PASS")
    result["hydration_fail"] = sum(1 for p in result["products"] if p.get("hydration_status") == "FAIL")
    return result
