from __future__ import annotations
import xml.etree.ElementTree as ET
from decimal import Decimal
from urllib.parse import urljoin
from .common import Report, require_requests, test_ref, safe_text

def _session(base_url: str, api_key: str):
    requests = require_requests()
    s = requests.Session()
    s.auth = (api_key, "")
    s.headers.update({"Accept": "application/xml", "User-Agent": "M99-Phase45/1.0"})
    return s

def _api(base, resource):
    return base.rstrip("/") + "/api/" + resource.lstrip("/")

def _langs(s, base):
    r = s.get(_api(base, "languages?display=[id,iso_code,name]&filter[active]=1"), timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    out = []
    for lang in root.findall(".//language"):
        lid = lang.get("id") or (lang.findtext("id") or "").strip()
        iso = (lang.findtext("iso_code") or "").strip().lower()
        name = (lang.findtext("name") or "").strip()
        if lid:
            out.append({"id": lid, "iso": iso, "name": name})
    return out

def _blank_product(s, base):
    r = s.get(_api(base, "products?schema=blank"), timeout=30)
    r.raise_for_status()
    return ET.fromstring(r.content)

def _set_text(parent, name, value):
    el = parent.find(name)
    if el is None:
        el = ET.SubElement(parent, name)
    el.text = str(value)
    return el

def _set_multi(parent, name, values):
    el = parent.find(name)
    if el is None:
        el = ET.SubElement(parent, name)
    for c in list(el):
        el.remove(c)
    for lang_id, value in values.items():
        x = ET.SubElement(el, "language", {"id": str(lang_id)})
        x.text = value

def _product_xml(root, reference, category_id, languages, price):
    product = root.find("product")
    if product is None:
        product = ET.SubElement(root, "product")

    for name, value in {
        "id_category_default": category_id,
        "reference": reference,
        "price": price,
        "active": "0",
        "state": "1",
        "available_for_order": "0",
        "show_price": "1",
        "visibility": "none",
        "product_type": "standard",
        "minimal_quantity": "1",
    }.items():
        _set_text(product, name, value)

    names, slugs, desc, short, meta_title, meta_desc = {}, {}, {}, {}, {}, {}
    for lang in languages:
        lid, iso = lang["id"], lang["iso"] or "xx"
        label = f"M99 Phase 4.5 Real Test {reference}"
        names[lid] = label
        slugs[lid] = f"{reference.lower()}-{iso}"
        short[lid] = "<p>M99 controlled Phase 4.5 real integration test.</p>"
        desc[lid] = "<p>Inactive disposable product for real CREATE/READBACK/UPDATE/DELETE validation.</p>"
        meta_title[lid] = label[:128]
        meta_desc[lid] = "Disposable inactive M99 Phase 4.5 integration validation product."

    _set_multi(product, "name", names)
    _set_multi(product, "link_rewrite", slugs)
    _set_multi(product, "description_short", short)
    _set_multi(product, "description", desc)
    _set_multi(product, "meta_title", meta_title)
    _set_multi(product, "meta_description", meta_desc)

    associations = product.find("associations")
    if associations is None:
        associations = ET.SubElement(product, "associations")
    cats = associations.find("categories")
    if cats is None:
        cats = ET.SubElement(associations, "categories")
    for c in list(cats):
        cats.remove(c)
    cat = ET.SubElement(cats, "category")
    ET.SubElement(cat, "id").text = str(category_id)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def _extract_id(content):
    root = ET.fromstring(content)
    for path in [".//product/id", ".//product"]:
        el = root.find(path)
        if el is not None:
            if path.endswith("/id") and el.text:
                return el.text.strip()
            if el.get("id"):
                return el.get("id")
    return None

def run(report: Report, base_url: str, api_key: str, category_id: str):
    if not base_url or not api_key:
        report.add("m99.eu credentials", "SKIP", "M99EU_BASE_URL or M99EU_API_KEY not supplied")
        return

    s = _session(base_url, api_key)
    product_id = None
    reference = test_ref()
    try:
        langs = _langs(s, base_url)
        if not langs:
            report.add("m99.eu dynamic language discovery", "FAIL", "No active languages returned")
            return
        report.add("m99.eu dynamic language discovery", "PASS", f"{len(langs)} active languages", {"languages": langs})

        blank = _blank_product(s, base_url)
        payload = _product_xml(blank, reference, category_id, langs, "1.00")
        r = s.post(_api(base_url, "products"), data=payload, headers={"Content-Type":"application/xml"}, timeout=30)
        if r.status_code not in (200, 201):
            report.add("m99.eu CREATE inactive test product", "FAIL", f"HTTP {r.status_code}", {"body": safe_text(r)})
            return
        product_id = _extract_id(r.content)
        if not product_id:
            report.add("m99.eu CREATE inactive test product", "FAIL", "Create response contained no product id")
            return
        report.add("m99.eu CREATE inactive test product", "PASS", f"id={product_id}, ref={reference}")

        r = s.get(_api(base_url, f"products/{product_id}"), timeout=30)
        if r.status_code != 200:
            report.add("m99.eu CREATE readback", "FAIL", f"HTTP {r.status_code}")
            return
        body = r.text
        required = [reference, "<active><![CDATA[0]]></active>", "<visibility><![CDATA[none]]></visibility>"]
        # PrestaShop may serialize without CDATA. Validate flexibly.
        active_ok = "<active>0</active>" in body or "<active><![CDATA[0]]></active>" in body
        visibility_ok = "<visibility>none</visibility>" in body or "<visibility><![CDATA[none]]></visibility>" in body
        if reference not in body or not active_ok or not visibility_ok:
            report.add("m99.eu CREATE readback", "FAIL", "Reference/active/visibility mismatch", {"body": body[:2500]})
            return
        report.add("m99.eu CREATE readback", "PASS", "reference + inactive + visibility none confirmed")

        # Update using fresh full resource to satisfy PS PUT contract.
        root = ET.fromstring(r.content)
        product = root.find("product")
        _set_text(product, "price", "1.11")
        update_payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        ur = s.put(_api(base_url, f"products/{product_id}"), data=update_payload, headers={"Content-Type":"application/xml"}, timeout=30)
        if ur.status_code not in (200, 201):
            report.add("m99.eu UPDATE test price", "FAIL", f"HTTP {ur.status_code}", {"body": safe_text(ur)})
            return
        report.add("m99.eu UPDATE test price", "PASS", "PUT accepted")

        rr = s.get(_api(base_url, f"products/{product_id}"), timeout=30)
        if rr.status_code != 200:
            report.add("m99.eu UPDATE readback", "FAIL", f"HTTP {rr.status_code}")
            return
        txt = rr.text
        if "<price>1.11</price>" not in txt and "<price><![CDATA[1.11]]></price>" not in txt:
            # Some APIs normalize decimal scale, parse XML instead.
            rt = ET.fromstring(rr.content)
            p = rt.find(".//product/price")
            try:
                ok = p is not None and Decimal((p.text or "0").strip()) == Decimal("1.11")
            except Exception:
                ok = False
            if not ok:
                report.add("m99.eu UPDATE readback", "FAIL", "Updated price 1.11 not confirmed")
                return
        report.add("m99.eu UPDATE readback", "PASS", "price=1.11 confirmed")

    except Exception as exc:
        report.add("m99.eu real integration", "FAIL", repr(exc))
    finally:
        if product_id:
            try:
                dr = s.delete(_api(base_url, f"products/{product_id}"), timeout=30)
                if dr.status_code in (200, 204):
                    report.add("m99.eu DELETE cleanup", "PASS", f"Deleted product id={product_id}")
                    vr = s.get(_api(base_url, f"products/{product_id}"), timeout=30)
                    if vr.status_code in (404, 410):
                        report.add("m99.eu DELETE readback", "PASS", f"HTTP {vr.status_code}")
                    else:
                        report.add("m99.eu DELETE readback", "FAIL", f"Expected 404/410, got {vr.status_code}")
                else:
                    report.add("m99.eu DELETE cleanup", "FAIL", f"HTTP {dr.status_code}", {"body": safe_text(dr)})
            except Exception as exc:
                report.add("m99.eu DELETE cleanup", "FAIL", repr(exc))
