from pathlib import Path
import json

from core.acquisition_preview import build_preview_from_file
from core.product_evidence import EvidenceRecord, evidence_bundle


SOURCE = Path(
    "tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
)
CHANNELS = Path(
    "config/channels/channel_rules_v0.6.0.json"
)
OUTPUT = Path(
    "output/diadora_glove_abox_low_pro_s1ps_preview.json"
)

data = json.loads(
    SOURCE.read_text(encoding="utf-8")
)

manufacturer = EvidenceRecord(
    **data["manufacturer_evidence"]
)
supplier_candidates = [
    EvidenceRecord(**x)
    for x in data.get("supplier_candidates", [])
]

preview = build_preview_from_file(
    SOURCE, CHANNELS
)
preview["evidence"] = evidence_bundle(
    manufacturer, supplier_candidates
)

preview["source_product"] = {
    "manufacturer_item": manufacturer.facts.get(
        "manufacturer_item"
    ),
    "protection_class": manufacturer.facts.get(
        "protection_class"
    ),
    "colour": manufacturer.facts.get("colour"),
    "eu_sizes": manufacturer.facts.get(
        "eu_sizes", []
    ),
}

supplier_flags = []
all_supplier_matches = True

for candidate in preview["evidence"]["supplier_candidates"]:
    cmp = candidate["comparison"]
    if cmp["decision"] == "REVIEW":
        all_supplier_matches = False
        supplier_flags.extend(cmp["reasons"])

preview["review"].update(
    {
        "product_identity_status": "VERIFIED",
        "manufacturer_content_status": "VERIFIED",
        "supplier_mapping_status": (
            "VERIFIED"
            if all_supplier_matches
            else "REVIEW"
        ),
        "pricing_status": (
            "READY"
            if all_supplier_matches
            else "BLOCKED"
        ),
        "availability_status": (
            "READY"
            if all_supplier_matches
            else "BLOCKED"
        ),
        "publication_status": "REVIEW",
        "blocking_flags": [],
        "supplier_mapping_flags": sorted(
            set(supplier_flags)
        ),
    }
)

preview["pricing_evidence"] = {
    "status": preview["review"]["pricing_status"],
    "usable_supplier_price": None,
    "reason": (
        None
        if all_supplier_matches
        else "SUPPLIER_IDENTITY_NOT_VERIFIED"
    ),
}

preview["availability_evidence"] = {
    "status": preview["review"]["availability_status"],
    "usable_supplier_stock": None,
    "reason": (
        None
        if all_supplier_matches
        else "SUPPLIER_IDENTITY_NOT_VERIFIED"
    ),
}

OUTPUT.parent.mkdir(
    parents=True, exist_ok=True
)
OUTPUT.write_text(
    json.dumps(
        preview,
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)

print("M99 Identity & Review Scope Preview v0.6.2.1")
print("============================================")
print("Schema:", preview["schema_version"])
print("Product:", preview["productgroup"]["name"])
print("ProductGroup:", preview["productgroup"]["m99_id"])
print(
    "Variants:",
    len(preview["variants"]),
    "(numeric M99 IDs)",
)
print(
    "Product identity:",
    preview["review"]["product_identity_status"],
)
print(
    "Supplier mapping:",
    preview["review"]["supplier_mapping_status"],
)
print(
    "Pricing:",
    preview["review"]["pricing_status"],
)
print(
    "Availability:",
    preview["review"]["availability_status"],
)
print(
    "Product blocking flags:",
    preview["review"]["blocking_flags"],
)
print(
    "Supplier mapping flags:",
    preview["review"]["supplier_mapping_flags"],
)
print("Writes to Dolibarr: NO")
print("Writes to websites: NO")
print("Preview written to:", OUTPUT)
