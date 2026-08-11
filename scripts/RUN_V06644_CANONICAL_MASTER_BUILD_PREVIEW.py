from pathlib import Path
from datetime import datetime, timezone
import json

from integrations.channel_publish import Mela99ClientConfig, ControlledMela99Publisher
from core.live_channel_metadata import parse_languages_xml, parse_categories_xml
from core.live_full_parameter_audit_v06643 import parse_product_xml
from core.canonical_master_build_v06644 import build_master_preview

ROOT=Path(".")
OUT=ROOT/"output"/"v06644_canonical_master_preview"
OUT.mkdir(parents=True,exist_ok=True)

client=ControlledMela99Publisher(
    Mela99ClientConfig(
        base_url="https://mela99.com",
        api_key_env="M99_MELA99_API_KEY",
        timeout_seconds=30,
    )
)

ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# Fresh live reads
langs=parse_languages_xml(client.get_resource_xml("languages",{"display":"full"}))
cats=parse_categories_xml(
    client.get_resource_xml("categories",{"display":"full"}),
    "Test",
    allow_inactive_review_category=True,
)
if not langs.get("ready"):
    raise RuntimeError("Live language mapping is not ready")
if not cats.get("ready"):
    raise RuntimeError("Live Test category discovery is not ready")

x2076=client.get_product_xml("2076")
x2100=client.get_product_xml("2100")
p2076=parse_product_xml(x2076)
p2100=parse_product_xml(x2100)

live_meta={
    "languages":{
        "bg_id":str(langs["bg_id"]),
        "en_id":str(langs["en_id"]),
    },
    "review_category":{
        "id":str(cats["selected_category_id"]),
        "active":cats["selected_category_active"],
        "name":"Test",
    },
}

preview=build_master_preview(p2076,p2100,live_meta)
preview["generated_at_utc"]=ts
preview["freshness"]={
    "product_2076_fetched_live_this_run":True,
    "product_2100_fetched_live_this_run":True,
    "uses_old_snapshot_for_product_values":False,
}

jp=OUT/f"{ts}_CANONICAL_MASTER_BUILD_PREVIEW.json"
jp.write_text(json.dumps(preview,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

pm=preview["proposed_master"]
print("M99 v0.6.6.4.4 - CANONICAL MASTER BUILD PREVIEW")
print("="*64)
print("HTTP policy: GET ONLY")
print("Fresh live products: 2076, 2100")
print("Canonical M99 ID:",pm["identity"]["m99_productgroup_id"])
print("Canonical model:",pm["identity"]["model_name"])
print("Manufacturer item:",pm["identity"]["manufacturer_item"])
print("BG language ID:",pm["languages"]["bg_id"])
print("EN language ID:",pm["languages"]["en_id"])
print("Review category:",pm["review_category"]["id"],"| active:",pm["review_category"]["active"])
print("")
print("2076 image count:",pm["assets"]["images"]["2076_count"])
print("2100 image count:",pm["assets"]["images"]["2100_count"])
print("2076 combination count:",pm["assets"]["combinations"]["2076_count"])
print("2100 combination count:",pm["assets"]["combinations"]["2100_count"])
print("")
print("2076 price:",pm["commercial"]["price"]["2076"])
print("2100 price:",pm["commercial"]["price"]["2100"])
print("Proposed price: OPERATOR REVIEW")
print("")
print("Proposed reference:",pm["reference"]["proposed"],"| approval required:",pm["reference"]["operator_approval_required"])
print("Legacy references:",pm["reference"]["legacy_candidates"])
print("")
print("BG content: NEW M99 CANONICAL PREVIEW")
print("EN content: NEW M99 CANONICAL PREVIEW")
print("Container product ID: NOT SELECTED")
print("WRITE ALLOWED: NO")
print("Output:",jp)
