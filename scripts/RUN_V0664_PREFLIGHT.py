from pathlib import Path
import json
from core.review_category_policy import apply_review_category_policy

MASTER = Path("output/diadora_glove_abox_low_pro_s3s_v0663_master_selection.json")
if not MASTER.exists():
    raise RuntimeError("Confirmed master selection JSON is missing")
data=json.loads(MASTER.read_text(encoding="utf-8"))
r=data["resolution"]
m=r["master"]
if r["decision"]!="MASTER_SELECTED" or m["product_id"]!="2076":
    raise RuntimeError("Expected confirmed master 2076")

policy=apply_review_category_policy(
    is_existing_product=True,
    existing_category_ids=["<READ_FROM_LIVE_XML>"],
    review_category_id="938",
)
print("M99 v0.6.6.4 WRITE_DRAFT preflight")
print("==================================")
print("Master: 2076 / EXISTING_CONFIRMED")
print("Name: KEEP by default")
print("URL/slug: KEEP")
print("Existing categories: KEEP")
print("Central review category: ADD 938")
print("Active after real WRITE_DRAFT: NO")
print("Duplicates 2100/2147: UNTOUCHED")
print("Website write in this preflight: NO")
