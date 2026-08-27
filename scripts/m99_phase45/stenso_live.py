from __future__ import annotations
import re
from lxml import html
from .common import Report, require_requests, safe_text

DEFAULT_CATEGORY = "https://stenso.net/211-rabotni-obuvki-diadora"
DEFAULT_PRODUCT = "https://stenso.net/produkt/boti/4794-rabotni-obuvki-diadora-freedom-mid-o6-sr-black-olive-green"

def _extract_sizes(doc):
    candidates = []
    for el in doc.xpath("//*[self::a or self::button or self::span or self::label or self::li]"):
        txt = " ".join(el.text_content().split())
        if re.fullmatch(r"(?:3[4-9]|4[0-9]|5[0-2])", txt):
            classes = " ".join([
                el.get("class", ""),
                el.get("style", ""),
                el.get("aria-disabled", ""),
                el.get("disabled", ""),
            ]).lower()
            parent = el.getparent()
            if parent is not None:
                classes += " " + " ".join([
                    parent.get("class", ""),
                    parent.get("style", ""),
                    parent.get("aria-disabled", ""),
                ]).lower()
            unavailable_tokens = (
                "disabled", "unavailable", "not-available", "out-of-stock",
                "out_of_stock", "sold-out", "soldout", "grey", "gray",
                "opacity", "no-stock"
            )
            unavailable = any(t in classes for t in unavailable_tokens)
            candidates.append({"size": txt, "unavailable": unavailable, "evidence": classes[:300]})
    # dedupe, prefer unavailable if any evidence says unavailable
    by = {}
    for item in candidates:
        s = item["size"]
        if s not in by or item["unavailable"]:
            by[s] = item
    return [by[k] for k in sorted(by, key=int)]

def run(report: Report, category_url: str = DEFAULT_CATEGORY, product_url: str = DEFAULT_PRODUCT):
    requests = require_requests()
    headers = {"User-Agent": "Mozilla/5.0 M99-Phase45-Validation/1.0"}

    try:
        r = requests.get(category_url, timeout=25, headers=headers)
        if r.status_code != 200:
            report.add("STENSO category live GET", "FAIL", f"HTTP {r.status_code}", {"body": safe_text(r)})
            return
        report.add("STENSO category live GET", "PASS", f"HTTP 200, {len(r.content)} bytes")
    except Exception as exc:
        report.add("STENSO category live GET", "FAIL", repr(exc))
        return

    try:
        r = requests.get(product_url, timeout=25, headers=headers)
        if r.status_code != 200:
            report.add("STENSO product live GET", "FAIL", f"HTTP {r.status_code}", {"body": safe_text(r)})
            return
        doc = html.fromstring(r.content)
        sizes = _extract_sizes(doc)
        if not sizes:
            report.add("STENSO live size extraction", "FAIL", "No size candidates detected; selector/parser needs adapter alignment")
            return
        report.add("STENSO live size extraction", "PASS", f"Detected {len(sizes)} sizes", {"sizes": sizes})

        by = {x["size"]: x for x in sizes}
        # Known visual reference supplied by operator: sizes 36 and 37 were unavailable.
        if "36" in by and "37" in by:
            if by["36"]["unavailable"] and by["37"]["unavailable"]:
                report.add("STENSO known 36/37 availability semantics", "PASS", "36 and 37 detected as unavailable")
            else:
                report.add(
                    "STENSO known 36/37 availability semantics",
                    "FAIL",
                    "36/37 present but current DOM heuristics do not classify both as unavailable",
                    {"36": by["36"], "37": by["37"]},
                )
        else:
            report.add(
                "STENSO known 36/37 availability semantics",
                "FAIL",
                "36 and/or 37 not found in live product DOM",
                {"sizes": sizes},
            )
    except Exception as exc:
        report.add("STENSO product live parse", "FAIL", repr(exc))
