from pathlib import Path
import json

from integrations.catalog_discovery import (
    ReadOnlyAdapterConfig,
    PrestaShopReadOnlyAdapter,
)
from core.duplicate_resolution import resolve_duplicates
from core.product_snapshot_analysis import (
    summarize_product_xml,
    add_snapshot_quality,
)
from integrations.channel_publish.mela99_controlled import (
    Mela99ClientConfig,
    ControlledMela99Publisher,
)

ROOT = Path(".")
DISCOVERY = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0662_live_internal_discovery.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0663_duplicate_resolution.json"
CONFIG = ROOT / "config/channels/internal_discovery_v0.6.5.json"

if not DISCOVERY.exists():
    raise RuntimeError(
        "v0.6.6.2 S3S live discovery output is missing. "
        "Run the GET-only S3S discovery first."
    )

discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
comparisons = discovery["result"].get("comparisons", [])

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
channel_cfg = cfg["channels"]["mela99.com"]

publisher = ControlledMela99Publisher(
    Mela99ClientConfig(
        base_url=channel_cfg["base_url"],
        api_key_env=channel_cfg["api_key_env"],
        timeout_seconds=20,
    )
)

snapshots = {}
snapshot_errors = {}

for comparison in comparisons:
    pid = str(comparison["candidate"]["product_id"])
    try:
        xml = publisher.get_product_xml(pid)
        snapshots[pid] = add_snapshot_quality(
            summarize_product_xml(xml)
        )
    except Exception as exc:
        snapshot_errors[pid] = {
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }

resolution = resolve_duplicates(comparisons)

# Enrich ranking with snapshot quality, but do not auto-select master.
for item in resolution.get("ranked_candidates", []):
    snap = snapshots.get(item["product_id"])
    if snap:
        item["snapshot_quality_score"] = snap["snapshot_quality_score"]
        item["snapshot_quality_reasons"] = snap["snapshot_quality_reasons"]
        item["combined_review_score"] = (
            item["score"] + snap["snapshot_quality_score"]
        )
    else:
        item["snapshot_quality_score"] = None
        item["snapshot_quality_reasons"] = []
        item["combined_review_score"] = item["score"]

if resolution.get("ranked_candidates"):
    resolution["ranked_candidates"] = sorted(
        resolution["ranked_candidates"],
        key=lambda x: (
            x["protection_conflict"],
            -x["combined_review_score"],
            x["product_id"],
        )
    )
    resolution["recommended_master"] = resolution["ranked_candidates"][0]

data = {
    "schema_version": "0.6.6.3",
    "mode": "GET_ONLY_DUPLICATE_RESOLUTION",
    "http_policy": "GET_ONLY",
    "writes": {
        "channels": False,
        "dolibarr": False,
        "supplier": False,
    },
    "source_discovery": str(DISCOVERY),
    "candidate_count": len(comparisons),
    "snapshots": snapshots,
    "snapshot_errors": snapshot_errors,
    "resolution": resolution,
    "master_selection_policy": {
        "automatic_master_selection": False,
        "operator_confirmation_required": True,
        "delete_duplicates_automatically": False,
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print("M99 v0.6.6.3 - Duplicate Resolution & Existing Master Selection")
print("===============================================================")
print("HTTP policy: GET ONLY")
print("Candidates:", len(comparisons))
for item in resolution.get("ranked_candidates", []):
    print(
        " - ID", item["product_id"],
        "| score", item.get("combined_review_score"),
        "| name", item.get("name"),
        "| URL clean", item.get("has_clean_url"),
    )
print("Decision:", resolution["decision"])
if resolution.get("recommended_master"):
    print(
        "Recommended master:",
        resolution["recommended_master"]["product_id"]
    )
print("Automatic master selection: NO")
print("Automatic delete: NO")
print("Writes to websites: NO")
print("Output:", OUTPUT)
