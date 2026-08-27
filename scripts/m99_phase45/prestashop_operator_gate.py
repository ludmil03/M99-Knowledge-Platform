from __future__ import annotations
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from .common import Report, test_ref, safe_text
from .prestashop_live import _session, _api, _langs, _blank_product, _product_xml, _extract_id

STATE_FILE = Path.home() / "Desktop" / "M99_V073_PHASE45_OPERATOR_PRODUCT.json"

def _read_product(s, base, product_id):
    return s.get(_api(base, f"products/{product_id}"), timeout=30)

def _xml_text(root, path):
    el = root.find(path)
    return (el.text or "").strip() if el is not None else ""

def _quality_checks(content: bytes, reference: str):
    root = ET.fromstring(content)
    product = root.find("product")
    checks = {}
    checks["reference"] = _xml_text(product, "reference") == reference
    checks["inactive"] = _xml_text(product, "active") == "0"
    checks["not_orderable"] = _xml_text(product, "available_for_order") == "0"
    checks["hidden"] = _xml_text(product, "visibility") == "none"
    checks["category_present"] = bool(_xml_text(product, "id_category_default"))
    checks["price_present"] = bool(_xml_text(product, "price"))
    checks["name_present"] = len(product.findall("./name/language")) > 0
    checks["slug_present"] = len(product.findall("./link_rewrite/language")) > 0
    checks["description_present"] = len(product.findall("./description/language")) > 0
    checks["meta_title_present"] = len(product.findall("./meta_title/language")) > 0
    checks["meta_description_present"] = len(product.findall("./meta_description/language")) > 0
    return checks

def run(report: Report, base_url: str, api_key: str, category_id: str):
    if not base_url or not api_key:
        report.add("m99.eu credentials", "SKIP", "M99EU_BASE_URL or M99EU_API_KEY not supplied")
        return

    s = _session(base_url, api_key)
    reference = test_ref("M99-P45-KEEP")
    product_id = None

    try:
        langs = _langs(s, base_url)
        if not langs:
            report.add("m99.eu dynamic language discovery", "FAIL", "No active languages returned")
            return
        report.add("m99.eu dynamic language discovery", "PASS", f"{len(langs)} active languages",
                   {"languages": langs})

        blank = _blank_product(s, base_url)
        payload = _product_xml(blank, reference, category_id, langs, "1.00")
        cr = s.post(_api(base_url, "products"), data=payload,
                    headers={"Content-Type": "application/xml"}, timeout=30)
        if cr.status_code not in (200, 201):
            report.add("m99.eu CREATE operator-review product", "FAIL",
                       f"HTTP {cr.status_code}", {"body": safe_text(cr)})
            return

        product_id = _extract_id(cr.content)
        if not product_id:
            report.add("m99.eu CREATE operator-review product", "FAIL", "No product id returned")
            return
        report.add("m99.eu CREATE operator-review product", "PASS",
                   f"id={product_id}, ref={reference}; PRODUCT WILL BE KEPT FOR OPERATOR REVIEW")

        rr = _read_product(s, base_url, product_id)
        if rr.status_code != 200:
            report.add("m99.eu API readback", "FAIL", f"HTTP {rr.status_code}")
            return

        checks = _quality_checks(rr.content, reference)
        failed = [k for k,v in checks.items() if not v]
        if failed:
            report.add("m99.eu automated transport/content gate", "FAIL",
                       "Failed: " + ", ".join(failed), {"checks": checks})
            return
        report.add("m99.eu automated transport/content gate", "PASS",
                   "API persistence + inactive/hidden safety + required content fields confirmed",
                   {"checks": checks})

        state = {
            "schema": "m99.phase45.operator_product.v1",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "base_url": base_url,
            "product_id": str(product_id),
            "reference": reference,
            "test_category_id": str(category_id),
            "operator_status": "PENDING_REVIEW",
            "daily_sync_status": "NOT_AUTHORIZED",
            "delete_status": "OPERATOR_ONLY",
            "required_operator_checks": [
                "Product name / page H1",
                "Logical H2/H3/H4 hierarchy where content requires it",
                "Long and short descriptions",
                "Technical specifications and standards",
                "Price",
                "Category",
                "Manufacturer / brand",
                "Variants / sizes",
                "Images",
                "Image ALT text",
                "Meta Title",
                "Meta Description",
                "Slug / URL",
                "All active language versions",
                "Back Office rendering",
                "Front Office rendering when previewable"
            ]
        }
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        report.add("m99.eu operator quality gate", "PASS",
                   f"PENDING_REVIEW state written to {STATE_FILE}; no automatic DELETE",
                   {"product_id": str(product_id), "reference": reference})
        report.add("m99.eu daily sync authorization", "SKIP",
                   "Requires explicit operator APPROVE after visual/content review")

    except Exception as exc:
        report.add("m99.eu real operator-gate integration", "FAIL", repr(exc))
        if product_id:
            report.add("m99.eu retained failed test product", "SKIP",
                       f"Product id={product_id}, ref={reference} retained for diagnosis; operator decides FIX or DELETE")
