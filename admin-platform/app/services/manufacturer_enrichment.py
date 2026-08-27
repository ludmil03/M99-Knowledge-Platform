from __future__ import annotations
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

UA = "M99KnowledgePlatform/0.7.3-phase45 (+manufacturer evidence read; no write)"

class ManufacturerReadError(RuntimeError):
    pass

def _clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def fetch(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=25,
            headers={"User-Agent": UA, "Accept-Language": "en,bg;q=0.8"},
        ) as client:
            r = client.get(url)
            if r.status_code >= 400:
                raise ManufacturerReadError(f"HTTP {r.status_code}")
            return str(r.url), r.text, r.status_code
    except httpx.HTTPError as exc:
        raise ManufacturerReadError(str(exc)) from exc

def _heading_value(soup, heading):
    target = heading.casefold()
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        label = _clean(h.get_text(" ", strip=True)).casefold()
        if label == target:
            n = h.find_next()
            for _ in range(8):
                if n is None:
                    break
                if getattr(n, "name", None) and re.match(r"^h[1-6]$", n.name):
                    break
                text = _clean(n.get_text(" ", strip=True)) if hasattr(n, "get_text") else ""
                if text and text.casefold() != target:
                    return text
                n = n.find_next()
    return ""

def _images(final_url, soup):
    urls = []
    for img in soup.find_all("img"):
        raw = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
        if not raw:
            continue
        url = urljoin(final_url, raw)
        low = url.lower()
        if any(x in low for x in ("logo", "icon", "social", "flag", "sprite")):
            continue
        alt = _clean(img.get("alt") or "")
        if "marine" in alt.casefold() or "product" in " ".join(img.get("class") or []).casefold():
            if url not in urls:
                urls.append(url)
    return urls[:20]

def parse_panda_safety(url: str, html: str, status: int):
    soup = BeautifulSoup(html, "html.parser")
    h1s = [_clean(x.get_text(" ", strip=True)) for x in soup.find_all("h1")]
    h2s = [_clean(x.get_text(" ", strip=True)) for x in soup.find_all("h2")]
    all_heads = [x for x in h1s + h2s if x]

    model = ""
    for x in all_heads:
        if x.casefold() == "marine":
            model = x
            break
    if not model:
        # Prefer a short uppercase-like heading that is not a section label.
        banned = {"code","en iso","category of protection","slip resistance","mondopoint",
                  "packaging","size range","weight","technical specifications"}
        for x in all_heads:
            if x.casefold() not in banned and len(x) <= 80:
                model = x
                break

    text = _clean(soup.get_text(" ", strip=True))

    code = _heading_value(soup, "Code")
    if not code:
        m = re.search(r"\b(\d{4,8}\s+(?:O\d|S\d)[A-Z0-9 +_-]{0,25})\b", text)
        code = _clean(m.group(1)) if m else ""

    en_iso = _heading_value(soup, "EN ISO")
    protection = _heading_value(soup, "Category of Protection")
    slip = _heading_value(soup, "Slip Resistance")
    mondopoint = _heading_value(soup, "Mondopoint")
    packaging = _heading_value(soup, "Packaging")
    size_range = _heading_value(soup, "Size Range")
    weight = _heading_value(soup, "Weight")

    # Technical sections from manufacturer.
    sections = {}
    labels = ("SOLE", "UPPER", "LINING", "FOOTBED", "EXTRA", "PROTECTIVE ELEMENTS")
    for label in labels:
        candidates = []
        for node in soup.find_all(string=re.compile(rf"^\s*{re.escape(label)}(?:\s*-\s*.*)?\s*$", re.I)):
            parent = node.parent
            nxt = parent.find_next() if parent else None
            for _ in range(10):
                if nxt is None:
                    break
                txt = _clean(nxt.get_text(" ", strip=True)) if hasattr(nxt, "get_text") else ""
                if txt and len(txt) >= 40 and label.casefold() not in txt.casefold()[:25]:
                    candidates.append(txt)
                    break
                nxt = nxt.find_next()
        if candidates:
            sections[label] = max(candidates, key=len)[:4000]

    # Technical Data Sheet link.
    tds = ""
    for a in soup.find_all("a", href=True):
        label = _clean(a.get_text(" ", strip=True)).casefold()
        if "technical data sheet" in label or label == "tds":
            tds = urljoin(url, a["href"])
            break

    return {
        "source_type": "MANUFACTURER",
        "manufacturer": "PANDA SAFETY",
        "url": url,
        "http": status,
        "model": model,
        "manufacturer_code": code,
        "en_iso": en_iso,
        "protection_class": protection,
        "slip_resistance": slip,
        "mondopoint": mondopoint,
        "packaging": packaging,
        "size_range": size_range,
        "weight": weight,
        "technical_sections": sections,
        "images": _images(url, soup),
        "tds_url": tds,
        "raw_title": _clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
        "hydration_status": "PASS",
    }

def hydrate_manufacturer_product(url: str):
    final_url, html, status = fetch(url)
    host = urlparse(final_url).netloc.lower()
    if "pandasafety.com" in host:
        return parse_panda_safety(final_url, html, status)
    raise ManufacturerReadError(
        f"Manufacturer parser not configured for host: {host}. "
        "Add/approve the manufacturer source and parser before use."
    )

def normalize_model(value: str):
    value = re.sub(r"[^0-9A-Za-z]+", " ", value or "").casefold()
    return " ".join(value.split())

def compare_identity(supplier: dict, manufacturer: dict):
    supplier_name = normalize_model(supplier.get("title", ""))
    model = normalize_model(manufacturer.get("model", ""))
    model_match = bool(model and model in supplier_name)
    return {
        "model_match": model_match,
        "supplier_title": supplier.get("title", ""),
        "supplier_reference": supplier.get("supplier_reference", ""),
        "manufacturer_model": manufacturer.get("model", ""),
        "manufacturer_code": manufacturer.get("manufacturer_code", ""),
        "requires_operator_confirmation": True,
        "identity_status": "PROBABLE_MATCH" if model_match else "UNRESOLVED",
        "important": "Supplier reference and manufacturer code are separate identifiers.",
    }

def merged_evidence(supplier: dict, manufacturer: dict):
    return {
        "identity": {
            "name": manufacturer.get("model") or supplier.get("title"),
            "supplier_reference": supplier.get("supplier_reference"),
            "manufacturer_code": manufacturer.get("manufacturer_code"),
        },
        "commercial_truth": {
            "authority": "SUPPLIER",
            "price": supplier.get("price_text"),
            "availability": supplier.get("availability_text"),
            "variants": supplier.get("variants", []),
        },
        "technical_truth": {
            "authority": "MANUFACTURER",
            "en_iso": manufacturer.get("en_iso"),
            "protection_class": manufacturer.get("protection_class"),
            "slip_resistance": manufacturer.get("slip_resistance"),
            "size_range": manufacturer.get("size_range"),
            "weight": manufacturer.get("weight"),
            "technical_sections": manufacturer.get("technical_sections", {}),
            "tds_url": manufacturer.get("tds_url"),
        },
        "images": {
            "preferred_authority": "MANUFACTURER",
            "manufacturer_images": manufacturer.get("images", []),
            "supplier_images": supplier.get("images", []),
        },
        "sources": [
            {"role": "SUPPLIER", "url": supplier.get("url")},
            {"role": "MANUFACTURER", "url": manufacturer.get("url")},
        ],
    }
