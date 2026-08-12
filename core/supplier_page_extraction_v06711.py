from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from urllib.parse import quote, urljoin, urlparse
import json
import re
import requests

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/150 Safari/537.36"
}

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def norm(v):
    return re.sub(r"[^a-z0-9]+", "", str(v or "").lower())

def clean_text(v):
    if v is None:
        return None
    return re.sub(r"\s+", " ", unescape(str(v))).strip()

def fetch(url, timeout=30):
    r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return {
        "url": r.url,
        "status": r.status_code,
        "html": r.text,
        "observed_at_utc": utc_now()
    }

def discover_candidates(domain, brand="Cherokee", codes=("WW601","WWE601"), max_results=8):
    # Read-only discovery. Multiple queries reduce dependence on one spelling.
    urls = []
    errors = []
    for code in codes:
        q = quote(f"site:{domain} {brand} {code}")
        search_url = "https://www.google.com/search?q=" + q
        try:
            page = fetch(search_url)
            html = page["html"]
            # direct visible URLs and Google redirect target fragments
            patterns = [
                r'https?://[^"\'<>\s&]+',
                r'/url\?q=(https?%3A%2F%2F[^&"]+)'
            ]
            for pat in patterns:
                for raw in re.findall(pat, html, flags=re.I):
                    try:
                        from urllib.parse import unquote
                        u = unquote(raw)
                    except Exception:
                        u = raw
                    if domain in u:
                        u = u.split("&")[0]
                        if "/search" not in u and u not in urls:
                            urls.append(u)
        except Exception as e:
            errors.append(type(e).__name__ + ": " + str(e)[:200])
    return {
        "domain": domain,
        "queries": [f"{brand} {c}" for c in codes],
        "candidate_urls": urls[:max_results],
        "errors": errors
    }

def _jsonld_objects(soup):
    out = []
    if soup is None:
        return out
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                out.extend(data)
            else:
                out.append(data)
        except Exception:
            continue
    return out

def _walk_jsonld(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk_jsonld(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_jsonld(v)

def _product_jsonld(soup):
    for root in _jsonld_objects(soup):
        for obj in _walk_jsonld(root):
            typ = obj.get("@type")
            types = typ if isinstance(typ, list) else [typ]
            if any(str(x).lower() == "product" for x in types if x):
                return obj
    return {}

def _meta(soup, *names):
    if soup is None:
        return None
    for n in names:
        node = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"name": n})
        if node and node.get("content"):
            return clean_text(node.get("content"))
    return None

def _currency_from_text(text):
    low = (text or "").lower()
    if "лв" in low or "bgn" in low:
        return "BGN"
    if "€" in low or " eur" in low:
        return "EUR"
    return None

def _number(s):
    if s is None:
        return None
    m = re.search(r"(\d+(?:[.,]\d{1,2})?)", str(s).replace("\xa0"," "))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except Exception:
        return None

def _extract_prices(soup, text, product):
    offers = product.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = offers.get("price")
    currency = offers.get("priceCurrency")
    availability = offers.get("availability")
    promo = None

    if price is None:
        price = _meta(soup, "product:price:amount", "og:price:amount")
    if currency is None:
        currency = _meta(soup, "product:price:currency", "og:price:currency")

    # conservative visible-price fallback
    if price is None:
        for pat in [
            r'(?:Цена|Price)\s*:?\s*(\d+[.,]\d{1,2})\s*(лв\.?|BGN|EUR|€)?',
            r'(\d+[.,]\d{2})\s*(лв\.?|BGN|EUR|€)'
        ]:
            m = re.search(pat, text, flags=re.I)
            if m:
                price = _number(m.group(1))
                if not currency and len(m.groups()) > 1:
                    currency = _currency_from_text(m.group(2) or "")
                break

    return {
        "price": _number(price) if price is not None else None,
        "promo_price": _number(promo) if promo is not None else None,
        "currency": clean_text(currency) or _currency_from_text(text),
        "raw_availability": clean_text(availability)
    }

def _extract_reference(product, text):
    for key in ("sku", "mpn", "productID"):
        if product.get(key):
            return clean_text(product.get(key))
    for pat in [
        r'(?:Код|Артикул|SKU|Reference|Референция|Модел)\s*:?\s*([A-Za-z0-9._/-]{4,40})',
        r'\b(CK[-_. ]?WW601[-_.A-Za-z0-9]*)\b',
        r'\b(WWE?601[A-Za-z0-9._/-]*)\b'
    ]:
        m = re.search(pat, text, flags=re.I)
        if m:
            return clean_text(m.group(1))
    return None

def _extract_stock(text, raw_availability):
    raw = (raw_availability or "").lower()
    low = (text or "").lower()
    if "instock" in raw:
        return "IN_STOCK"
    if "outofstock" in raw:
        return "OUT_OF_STOCK"
    positive = ["в наличност", "наличен", "налична", "in stock"]
    negative = ["няма наличност", "изчерпан", "out of stock"]
    if any(x in low for x in negative):
        return "OUT_OF_STOCK"
    if any(x in low for x in positive):
        return "IN_STOCK"
    return None

def _extract_sizes(soup, text):
    values = []
    if soup:
        for node in soup.find_all(["option","button","label"]):
            t = clean_text(node.get_text(" ", strip=True))
            if t and re.fullmatch(r"(?:XXS|XS|S|M|L|XL|XXL|2XL|3XL|4XL|5XL|[0-9]{2,3})", t, flags=re.I):
                values.append(t)
    # keep unique in page order
    return list(dict.fromkeys(values))[:50]

def _extract_images(soup, product, base_url):
    urls = []
    image = product.get("image")
    if isinstance(image, str):
        urls.append(image)
    elif isinstance(image, list):
        urls.extend([x for x in image if isinstance(x, str)])
    if soup:
        og = _meta(soup, "og:image")
        if og:
            urls.append(og)
        for img in soup.find_all("img"):
            u = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if u:
                urls.append(urljoin(base_url, u))
    return list(dict.fromkeys(urls))[:20]

def _extract_technical_facts(soup):
    facts = {}
    if not soup:
        return facts
    # table rows
    for tr in soup.find_all("tr"):
        cells = [clean_text(x.get_text(" ", strip=True)) for x in tr.find_all(["th","td"])]
        if len(cells) >= 2 and cells[0] and cells[1]:
            facts[cells[0][:120]] = cells[1][:500]
    # definition lists
    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            k = clean_text(dt.get_text(" ", strip=True))
            v = clean_text(dd.get_text(" ", strip=True))
            if k and v:
                facts[k[:120]] = v[:500]
    return facts

def parse_supplier_page(supplier, candidate_url):
    page = fetch(candidate_url)
    html = page["html"]
    soup = BeautifulSoup(html, "html.parser") if BeautifulSoup else None
    if soup:
        for x in soup(["script","style","nav","footer","header","noscript"]):
            # retain JSON-LD scripts already parsed later? We parse product first below.
            pass
    product = _product_jsonld(soup)
    title = clean_text(product.get("name")) or _meta(soup, "og:title")
    if not title and soup and soup.title:
        title = clean_text(soup.title.get_text(" ", strip=True))

    # separate cleaned visible text
    visible = ""
    if soup:
        clone = BeautifulSoup(html, "html.parser")
        for x in clone(["script","style","nav","footer","header","noscript"]):
            x.decompose()
        visible = clean_text(clone.get_text(" ", strip=True)) or ""
    else:
        visible = clean_text(re.sub(r"<[^>]+>", " ", html)) or ""

    prices = _extract_prices(soup, visible, product)
    ref = _extract_reference(product, visible)
    desc = clean_text(product.get("description")) or _meta(soup, "og:description", "description")
    availability = _extract_stock(visible, prices["raw_availability"])

    return {
        "supplier": supplier,
        "source_url": page["url"],
        "http_status": page["status"],
        "observed_at_utc": page["observed_at_utc"],
        "title": title,
        "supplier_reference": ref,
        "price": prices["price"],
        "promo_price": prices["promo_price"],
        "currency": prices["currency"],
        "availability": availability,
        "size_availability": _extract_sizes(soup, visible),
        "description": desc,
        "technical_facts": _extract_technical_facts(soup),
        "images": _extract_images(soup, product, page["url"]),
        "raw_text_excerpt": visible[:4000],
    }

def identity_score(record, brand="Cherokee", canonical="WW601", requested="WWE601"):
    title = record.get("title") or ""
    ref = record.get("supplier_reference") or ""
    text = " ".join([title, ref, record.get("raw_text_excerpt") or ""])
    n = norm(text)
    brand_ok = norm(brand) in n
    canonical_ok = norm(canonical) in n
    requested_ok = norm(requested) in n

    # Exact code in reference is strongest.
    r = norm(ref)
    if brand_ok and r and (norm(canonical) in r or norm(requested) in r):
        return {"class":"EXACT","score":100,"reasons":["brand_match","style_code_in_supplier_reference"]}
    if brand_ok and canonical_ok:
        return {"class":"VERY_STRONG","score":85,"reasons":["brand_match","canonical_style_token"]}
    if brand_ok and requested_ok:
        return {"class":"VERY_STRONG","score":80,"reasons":["brand_match","requested_alias_token"]}
    if canonical_ok or requested_ok:
        return {"class":"NEAR_MATCH","score":50,"reasons":["style_token_without_brand_confirmation"]}
    return {"class":"REJECT","score":0,"reasons":["identity_not_proven"]}

def classify_candidates(records):
    out = []
    for rec in records:
        x = dict(rec)
        x["identity"] = identity_score(x)
        x["commercial_quarantined"] = x["identity"]["class"] not in ("EXACT","VERY_STRONG")
        out.append(x)
    return sorted(out, key=lambda x: x["identity"]["score"], reverse=True)

def build_supplier_summary(records):
    exact = [x for x in records if x["identity"]["class"] == "EXACT"]
    strong = [x for x in records if x["identity"]["class"] == "VERY_STRONG"]
    eligible = exact or strong
    return {
        "eligible_count": len(eligible),
        "best_candidate": eligible[0] if eligible else None,
        "all_prices": [
            {"url":x["source_url"],"price":x["price"],"currency":x["currency"],
             "identity":x["identity"]["class"]}
            for x in eligible if x.get("price") is not None
        ],
        "all_stock": [
            {"url":x["source_url"],"availability":x["availability"],
             "identity":x["identity"]["class"]}
            for x in eligible if x.get("availability") is not None
        ],
        "m99_selling_price_proposed": None
    }

def merge_evidence(stenso_records, palltex_records):
    return {
        "identity_authority": "MANUFACTURER_REQUIRED_FOR_CANONICAL",
        "supplier_evidence": {
            "Stenso": build_supplier_summary(stenso_records),
            "Palltex": build_supplier_summary(palltex_records),
        },
        "commercial_policy": {
            "preserve_per_supplier": True,
            "never_merge_supplier_stock": True,
            "never_auto_select_m99_selling_price": True
        },
        "content_generation_gate": {
            "supplier_evidence_present": any(
                x["identity"]["class"] in ("EXACT","VERY_STRONG")
                for x in stenso_records + palltex_records
            ),
            "manufacturer_evidence_required": True
        }
    }
