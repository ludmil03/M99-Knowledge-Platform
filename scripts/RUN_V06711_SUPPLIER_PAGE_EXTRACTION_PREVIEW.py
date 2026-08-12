from pathlib import Path
from datetime import datetime, timezone
import json

from core.supplier_page_extraction_v06711 import (
    discover_candidates, parse_supplier_page, classify_candidates, merge_evidence
)

OUT = Path("output") / "v06711_supplier_page_extraction"
OUT.mkdir(parents=True, exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def run_supplier(name, domain):
    discovery = discover_candidates(domain)
    parsed = []
    errors = []
    for url in discovery["candidate_urls"]:
        try:
            parsed.append(parse_supplier_page(name, url))
        except Exception as e:
            errors.append({
                "url": url,
                "error_type": type(e).__name__,
                "error": str(e)[:500]
            })
    classified = classify_candidates(parsed)
    return {
        "supplier": name,
        "domain": domain,
        "discovery": discovery,
        "candidates": classified,
        "errors": errors
    }

stenso = run_supplier("Stenso", "stenso.net")
palltex = run_supplier("Palltex", "palltex.bg")

merge = merge_evidence(stenso["candidates"], palltex["candidates"])

report = {
    "schema_version": "0.6.7.1.1",
    "mode": "LIVE_GET_ONLY_SUPPLIER_PAGE_EXTRACTION_EVIDENCE_MERGE",
    "generated_at_utc": ts,
    "http_policy": "GET_ONLY",
    "writes": {"channels": False, "dolibarr": False, "suppliers": False},
    "product": {
        "brand": "Cherokee",
        "requested_code": "WWE601",
        "canonical_family_under_review": "WW601"
    },
    "suppliers": {
        "Stenso": stenso,
        "Palltex": palltex
    },
    "evidence_merge": merge,
    "gates": {
        "manufacturer_identity_still_required": True,
        "commercial_values_can_be_used_only_from_exact_or_very_strong": True,
        "m99_selling_price_approved": False,
        "content_generation_ready": False,
        "write_allowed": False
    }
}

path = OUT / f"{ts}_CHEROKEE_WW601_SUPPLIER_PAGE_EXTRACTION.json"
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("M99 v0.6.7.1.1 - SUPPLIER PRODUCT PAGE EXTRACTION & EVIDENCE MERGE")
print("=" * 74)
print("HTTP policy: GET ONLY")
for supplier in (stenso, palltex):
    print("")
    print(supplier["supplier"])
    print(" discovered:", len(supplier["discovery"]["candidate_urls"]))
    print(" fetched:", len(supplier["candidates"]))
    for i, c in enumerate(supplier["candidates"], 1):
        ident = c["identity"]
        print(
            f"  {i}. {ident['class']} | score {ident['score']} | "
            f"ref={c.get('supplier_reference')} | "
            f"price={c.get('price')} {c.get('currency') or ''} | "
            f"stock={c.get('availability')} | sizes={len(c.get('size_availability') or [])}"
        )
        print("     title:", c.get("title"))
        print("     url:", c.get("source_url"))
    if supplier["errors"]:
        print(" fetch errors:", len(supplier["errors"]))

print("")
print("Commercial data from NEAR_MATCH/REJECT: QUARANTINED")
print("Supplier prices: PRESERVED SEPARATELY")
print("Supplier stock: PRESERVED SEPARATELY")
print("M99 selling price: NOT SELECTED")
print("Manufacturer identity: STILL REQUIRED BEFORE CANONICAL MERGE")
print("CONTENT GENERATION READY: NO")
print("WRITE ALLOWED: NO")
print("Output:", path)
