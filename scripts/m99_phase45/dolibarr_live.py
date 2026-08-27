from __future__ import annotations
from .common import Report, require_requests, test_ref, safe_text

def _api(base, resource):
    base = base.rstrip("/")
    if base.endswith("/api/index.php"):
        return base + "/" + resource.lstrip("/")
    return base + "/api/index.php/" + resource.lstrip("/")

def run(report: Report, base_url: str, api_key: str):
    if not base_url or not api_key:
        report.add("Dolibarr test credentials", "SKIP", "DOLIBARR_BASE_URL or DOLIBARR_API_KEY not supplied")
        return

    requests = require_requests()
    headers = {"DOLAPIKEY": api_key, "Content-Type": "application/json", "Accept": "application/json"}
    ref = test_ref("M99-P45-DOL")
    product_id = None

    try:
        sr = requests.get(_api(base_url, "status"), headers=headers, timeout=30)
        if sr.status_code not in (200, 401, 403, 404):
            report.add("Dolibarr real status probe", "FAIL", f"HTTP {sr.status_code}", {"body": safe_text(sr)})
            return
        # Some installations do not expose status, so authenticate through products endpoint too.
        pr = requests.get(_api(base_url, "products?limit=1"), headers=headers, timeout=30)
        if pr.status_code != 200:
            report.add("Dolibarr authenticated read", "FAIL", f"HTTP {pr.status_code}", {"body": safe_text(pr)})
            return
        report.add("Dolibarr authenticated read", "PASS", "GET products?limit=1 = HTTP 200")

        payload = {
            "ref": ref,
            "label": f"M99 Phase 4.5 Disposable Test {ref}",
            "description": "Disposable real integration test. Safe to delete.",
            "type": 0,
            "price": 1.0,
            "price_ttc": 1.2,
            "status": 0,
            "status_buy": 0,
        }
        cr = requests.post(_api(base_url, "products"), headers=headers, json=payload, timeout=30)
        if cr.status_code not in (200, 201):
            report.add("Dolibarr CREATE test product", "FAIL", f"HTTP {cr.status_code}", {"body": safe_text(cr)})
            return
        try:
            product_id = int(cr.json())
        except Exception:
            try:
                product_id = int(cr.json().get("id"))
            except Exception:
                product_id = None
        if not product_id:
            report.add("Dolibarr CREATE test product", "FAIL", "No product id returned", {"body": safe_text(cr)})
            return
        report.add("Dolibarr CREATE test product", "PASS", f"id={product_id}, ref={ref}")

        rr = requests.get(_api(base_url, f"products/{product_id}"), headers=headers, timeout=30)
        if rr.status_code != 200:
            report.add("Dolibarr CREATE readback", "FAIL", f"HTTP {rr.status_code}")
            return
        data = rr.json()
        if str(data.get("ref")) != ref:
            report.add("Dolibarr CREATE readback", "FAIL", f"Reference mismatch: {data.get('ref')}")
            return
        report.add("Dolibarr CREATE readback", "PASS", "reference confirmed")

        ur = requests.put(
            _api(base_url, f"products/{product_id}"),
            headers=headers,
            json={"label": f"M99 Phase 4.5 UPDATED {ref}"},
            timeout=30,
        )
        if ur.status_code not in (200, 201):
            report.add("Dolibarr UPDATE test product", "FAIL", f"HTTP {ur.status_code}", {"body": safe_text(ur)})
            return
        report.add("Dolibarr UPDATE test product", "PASS", "PUT accepted")

        rr2 = requests.get(_api(base_url, f"products/{product_id}"), headers=headers, timeout=30)
        if rr2.status_code != 200 or "UPDATED" not in str(rr2.json().get("label", "")):
            report.add("Dolibarr UPDATE readback", "FAIL", f"HTTP {rr2.status_code}", {"body": safe_text(rr2)})
            return
        report.add("Dolibarr UPDATE readback", "PASS", "updated label confirmed")

    except Exception as exc:
        report.add("Dolibarr real integration", "FAIL", repr(exc))
    finally:
        if product_id:
            try:
                dr = requests.delete(_api(base_url, f"products/{product_id}"), headers=headers, timeout=30)
                if dr.status_code in (200, 204):
                    report.add("Dolibarr DELETE cleanup", "PASS", f"Deleted product id={product_id}")
                    vr = requests.get(_api(base_url, f"products/{product_id}"), headers=headers, timeout=30)
                    if vr.status_code in (404, 410):
                        report.add("Dolibarr DELETE readback", "PASS", f"HTTP {vr.status_code}")
                    else:
                        report.add("Dolibarr DELETE readback", "FAIL", f"Expected 404/410, got {vr.status_code}")
                else:
                    report.add("Dolibarr DELETE cleanup", "FAIL", f"HTTP {dr.status_code}", {"body": safe_text(dr)})
            except Exception as exc:
                report.add("Dolibarr DELETE cleanup", "FAIL", repr(exc))
