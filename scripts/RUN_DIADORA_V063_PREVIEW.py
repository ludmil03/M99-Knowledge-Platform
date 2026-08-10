from pathlib import Path
import json

from core.existing_product_discovery import (
    DiscoveryEvidence,
    evaluate_discovery,
)
from core.content_seo_preview import (
    build_diadora_content_preview,
)


ROOT = Path(".")
PRODUCT_FIXTURE = ROOT / "tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
DISCOVERY_SNAPSHOT = ROOT / "knowledge/evidence/diadora_glove_abox_s1ps_discovery_snapshot.json"
INPUT_PREVIEW = ROOT / "output/diadora_glove_abox_low_pro_s1ps_preview.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v063_preview.json"

product_data = json.loads(
    PRODUCT_FIXTURE.read_text(encoding="utf-8")
)
snapshot = json.loads(
    DISCOVERY_SNAPSHOT.read_text(encoding="utf-8")
)

manufacturer_facts = product_data["manufacturer_evidence"]["facts"]

records = [
    DiscoveryEvidence(
        channel=x["channel"],
        query_type=x["query_type"],
        query_value=x["query_value"],
        result=x["result"],
        notes=x.get("notes"),
    )
    for x in snapshot["channel_public_search"]
]

discovery = evaluate_discovery(records)
content = build_diadora_content_preview(
    manufacturer_facts
)

base_preview = {}
if INPUT_PREVIEW.exists():
    base_preview = json.loads(
        INPUT_PREVIEW.read_text(encoding="utf-8")
    )
else:
    base_preview = {
        "schema_version": "0.6.2.1",
        "productgroup": {
            "m99_id": product_data["m99_id"],
            "name": product_data["name"],
            "brand": product_data["brand"],
        },
        "review": {},
    }

base_preview["schema_version"] = "0.6.3"
base_preview["mode"] = "DISCOVERY_AND_CONTENT_SEO_PREVIEW"
base_preview["existing_product_discovery"] = discovery
base_preview["content_seo_preview"] = content

review = base_preview.setdefault("review", {})
review["existing_product_discovery_status"] = discovery["status"]
review["content_seo_status"] = "REVIEW"
review["publication_status"] = "BLOCKED_PENDING_EXISTING_PRODUCT_VERIFICATION"
review["operator_required"] = True

base_preview["writes"] = {
    "dolibarr": False,
    "channels": False,
    "supplier": False,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(
        base_preview,
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)

print("M99 Existing Product Discovery + Content/SEO Preview v0.6.3")
print("============================================================")
print("Product:", product_data["name"])
print("M99 ID:", product_data["m99_id"])
print("Discovery:", discovery["status"])
for channel, result in discovery["channels"].items():
    print(" -", channel, "=>", result["status"])
print("Content/SEO channels:", len(content))
for channel, languages in content.items():
    print(" -", channel, "languages:", ", ".join(languages.keys()))
print("Publication: BLOCKED pending operator existing-product verification")
print("Writes to Dolibarr: NO")
print("Writes to websites: NO")
print("Preview written to:", OUTPUT)
