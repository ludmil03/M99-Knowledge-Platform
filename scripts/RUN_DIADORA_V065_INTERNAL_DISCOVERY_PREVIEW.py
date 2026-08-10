from pathlib import Path
import json

from core.internal_existing_product_discovery import discover_existing_product
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from core.content_seo_preview import build_diadora_content_preview
from core.content_quality_guard import evaluate_all_content


ROOT = Path(".")
FIXTURE = ROOT / "tests/fixtures/internal_discovery_v065_sample.json"
REAL_PRODUCT = ROOT / "tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v065_preview.json"

sample = json.loads(FIXTURE.read_text(encoding="utf-8"))
source = json.loads(REAL_PRODUCT.read_text(encoding="utf-8"))

# Keep content QA in the v0.6.5 preview so the remaining QA notes are verified.
manufacturer = source["manufacturer_evidence"]
canonical = build_canonical_product_facts(
    manufacturer["source_name"],
    manufacturer["source_url"],
    manufacturer["facts"],
)
facts = canonical_values(canonical)
content = build_diadora_content_preview(facts)
quality = evaluate_all_content(content, facts)

results = {}
for channel, candidates in sample["channels"].items():
    results[channel] = discover_existing_product(
        channel,
        sample["canonical_product"],
        candidates,
    )

preview = {
    "schema_version": "0.6.5",
    "mode": "INTERNAL_EXISTING_PRODUCT_DISCOVERY",
    "writes": {
        "dolibarr": False,
        "channels": False,
        "supplier": False,
    },
    "productgroup": {
        "m99_id": source["m99_id"],
        "name": source["name"],
        "brand": source["brand"],
    },
    "internal_existing_product_discovery": {
        "status": "REVIEW",
        "authoritative_scope": "OWN_CHANNEL_CATALOGS",
        "public_search_role": "SECONDARY_EVIDENCE_ONLY",
        "results": results,
    },
    "content_qa_refinement": {
        "status": quality["status"],
        "all_content_ready": quality["all_content_ready"],
        "meta_descriptions": {
            channel: {
                language: document["meta_description"]
                for language, document in languages.items()
            }
            for channel, languages in content.items()
        },
        "faq_questions": {
            channel: {
                language: [x["q"] for x in document["faq"]]
                for language, document in languages.items()
            }
            for channel, languages in content.items()
        },
    },
    "next_version_gate": {
        "controlled_publish_version": "0.6.6",
        "publish_enabled_now": False,
        "requires_live_internal_discovery": True,
        "requires_operator_approval": True,
        "requires_pricing_gate": True,
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(preview, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print("M99 Internal Existing Product Discovery v0.6.5")
print("================================================")
print("Product:", source["name"])
print("M99 ID:", source["m99_id"])
print("Content QA:", quality["status"])
print("Internal discovery decisions:")
for channel, result in results.items():
    print(" -", channel, "=>", result["decision"], "|", result["action"])
print("Public search role: SECONDARY_EVIDENCE_ONLY")
print("Publication enabled: NO")
print("Writes to Dolibarr: NO")
print("Writes to websites: NO")
print("Next controlled publish version: v0.6.6")
print("Preview written to:", OUTPUT)
