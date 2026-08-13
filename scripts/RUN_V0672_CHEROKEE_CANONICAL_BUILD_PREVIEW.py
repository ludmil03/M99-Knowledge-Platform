from pathlib import Path
from datetime import datetime,timezone
import json
from core.cherokee_canonical_merge_v0672 import parse_manufacturer,parse_stenso,build_canonical

OUT=Path("output/v0672_cherokee_canonical_build");OUT.mkdir(parents=True,exist_ok=True)
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
manufacturer=parse_manufacturer()
stenso=parse_stenso()

# Palltex remains intentionally absent unless an exact current product page is independently proven.
palltex=None
canonical=build_canonical(manufacturer,stenso,palltex)

report={
 "schema_version":"0.6.7.2",
 "mode":"LIVE_GET_ONLY_MANUFACTURER_SUPPLIER_EVIDENCE_MERGE_CANONICAL_BUILD",
 "generated_at_utc":ts,
 "http_policy":"GET_ONLY",
 "writes":{"channels":False,"dolibarr":False,"suppliers":False},
 "manufacturer_evidence":manufacturer,
 "supplier_evidence":{"Stenso":stenso,"Palltex":{"status":"UNRESOLVED_NO_EXACT_PRODUCT_EVIDENCE"}},
 "canonical_product":canonical
}
f=OUT/f"{ts}_CHEROKEE_WW601_CANONICAL_PRODUCT_BUILD.json"
f.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

ci=canonical["canonical_identity"]
print("M99 v0.6.7.2 - MANUFACTURER + SUPPLIER EVIDENCE MERGE & CANONICAL PRODUCT BUILD")
print("="*82)
print("HTTP policy: GET ONLY")
print("")
print("CANONICAL IDENTITY")
print("Brand:",ci["brand"])
print("Collection:",ci["collection"])
print("Canonical style:",ci["canonical_style"])
print("Supplier aliases:",ci["supplier_style_aliases"])
print("Manufacturer item:",ci["manufacturer_item"])
print("Target colour:",ci["target_colour"])
print("Official name:",ci["official_name"])
print("Identity status:",canonical["identity_status"])
print("")
print("MANUFACTURER FACTS")
for x in canonical["fact_merge"]:
    print("-",x["field"],"=>",x["status"],"|",x.get("selected"))
print("")
print("STENSO")
print("Reference:",canonical["supplier_identity"]["Stenso"]["reference"])
print("Visible sizes:",canonical["sizes"]["stenso_visible_sizes"])
print("Raw price observations:",canonical["commercial"]["Stenso"]["raw_price_observations"][:10])
print("Availability:",canonical["commercial"]["Stenso"]["availability"])
print("")
print("PALLTEX: UNRESOLVED - NO EXACT PRODUCT EVIDENCE")
print("Content evidence ready:",canonical["content_evidence"]["ready"])
print("Allowed claim fields:",canonical["content_evidence"]["allowed_claim_fields"])
print("M99 ProductGroup ID: NOT ASSIGNED")
print("M99 Reference: NOT ASSIGNED")
print("M99 selling price: NOT SELECTED")
print("OPERATOR REVIEW REQUIRED: YES")
print("WRITE ALLOWED: NO")
print("Output:",f)
