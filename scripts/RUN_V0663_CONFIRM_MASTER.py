from pathlib import Path
import json
import os

from core.duplicate_resolution import resolve_duplicates

ROOT = Path(".")
SOURCE = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0662_live_internal_discovery.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0663_master_selection.json"

data = json.loads(SOURCE.read_text(encoding="utf-8"))
comparisons = data["result"].get("comparisons", [])

master_id = os.environ.get("M99_MASTER_PRODUCT_ID", "").strip()
confirmation = os.environ.get("M99_MASTER_CONFIRMATION", "")

if not master_id:
    raise RuntimeError("M99_MASTER_PRODUCT_ID is required")

result = resolve_duplicates(
    comparisons,
    operator_master_product_id=master_id,
    operator_confirmation=confirmation,
)

payload = {
    "schema_version": "0.6.6.3",
    "mode": "OPERATOR_MASTER_SELECTION",
    "writes": {
        "channels": False,
        "dolibarr": False,
        "supplier": False,
    },
    "resolution": result,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print("Master selected:", result["master"]["product_id"])
print("Identity status:", result["master"]["identity_status"])
print("URL action:", result["master"]["url_action"])
print("Name action:", result["master"]["product_name_action"])
print("Duplicates:", [x["product_id"] for x in result["duplicates"]])
print("Automatic delete: NO")
print("Website write: NO")
print("Output:", OUTPUT)
