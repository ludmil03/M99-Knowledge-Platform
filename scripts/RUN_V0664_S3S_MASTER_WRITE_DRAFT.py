from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

from core.review_category_policy import apply_review_category_policy, REVIEW_CATEGORY_ID
from core.s3s_master_content import build_s3s_content
from core.s3s_master_write_draft import mutate_master_to_review_draft
from integrations.channel_publish import (
    Mela99ClientConfig,
    ControlledMela99Publisher,
    write_audit_record,
    sha256_text,
)

ROOT = Path(".")
MASTER = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0663_master_selection.json"
FIXTURE = ROOT / "tests/fixtures/diadora_glove_abox_low_pro_s3s_real.json"
AUDIT_DIR = ROOT / "output/publish_audit"
ROLLBACK_DIR = ROOT / "output/publish_rollback"

TARGET_CHANNEL = "mela99.com"
TARGET_PRODUCT_ID = "2076"
TARGET_M99_ID = "M99 100017"

def _load(path):
    if not path.exists():
        raise RuntimeError(f"Required file missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

master_data = _load(MASTER)
resolution = master_data.get("resolution", {})
master = resolution.get("master") or {}

if resolution.get("decision") != "MASTER_SELECTED":
    raise RuntimeError("Master selection is not confirmed")
if master.get("identity_status") != "EXISTING_CONFIRMED":
    raise RuntimeError("Master identity is not EXISTING_CONFIRMED")
if str(master.get("product_id")) != TARGET_PRODUCT_ID:
    raise RuntimeError("WRITE_DRAFT hard-lock mismatch: expected product ID 2076")
if resolution.get("delete_allowed") is not False:
    raise RuntimeError("Unsafe duplicate delete policy")

fixture = _load(FIXTURE)
facts = fixture["manufacturer_evidence"]["facts"]
content = build_s3s_content(facts)

api_key = os.environ.get("M99_MELA99_API_KEY")
if not api_key:
    raise RuntimeError("M99_MELA99_API_KEY is not set")

operator = os.environ.get("M99_OPERATOR_APPROVED", "").strip().upper()
if operator != "YES":
    raise RuntimeError("Operator approval missing")

required = "WRITE_DRAFT UPDATE 2076 M99 100017 MELA99"
confirmation = os.environ.get("M99_WRITE_DRAFT_CONFIRMATION", "")
if confirmation != required:
    raise RuntimeError("Exact confirmation required: " + required)

name_change = (
    os.environ.get("M99_NAME_CHANGE_APPROVED", "").strip().upper() == "YES"
    and os.environ.get("M99_NAME_CHANGE_EVIDENCE", "").strip().upper() == "PROVEN_BETTER"
)

client = ControlledMela99Publisher(
    Mela99ClientConfig(
        base_url="https://mela99.com",
        api_key_env="M99_MELA99_API_KEY",
        timeout_seconds=30,
    )
)

# Full current XML snapshot immediately before write.
original_xml = client.get_product_xml(TARGET_PRODUCT_ID)

timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
rollback_path = ROLLBACK_DIR / f"{timestamp}_mela99_product_2076_before_v0664.xml"
rollback_path.write_text(original_xml, encoding="utf-8")

updated_xml, mutation = mutate_master_to_review_draft(
    original_xml,
    content=content,
    review_category_id=REVIEW_CATEGORY_ID,
    change_name=name_change,
)

category_policy = apply_review_category_policy(
    is_existing_product=True,
    existing_category_ids=mutation["protected_identity"]["original_category_ids"],
    review_category_id=REVIEW_CATEGORY_ID,
)

# Guard: original categories must be a subset of the outgoing categories.
before = set(mutation["protected_identity"]["original_category_ids"])
after = set(mutation["write_category_ids"])
if not before.issubset(after):
    raise RuntimeError("Category preservation guard failed")
if REVIEW_CATEGORY_ID not in after:
    raise RuntimeError("Central review category was not added")

# Guard: protected URL identity.
protected = mutation["protected_identity"]
if mutation["slug_changed"]:
    raise RuntimeError("Slug mutation detected")
if not name_change and mutation["name_changed"]:
    raise RuntimeError("Name protection guard failed")

audit_path = AUDIT_DIR / f"{timestamp}_M99_100017_mela99_WRITE_DRAFT_UPDATE.json"
audit = {
    "schema_version": "0.6.6.4",
    "timestamp_utc": timestamp,
    "mode": "WRITE_DRAFT",
    "channel": TARGET_CHANNEL,
    "action": "UPDATE",
    "product_id": TARGET_PRODUCT_ID,
    "m99_id": TARGET_M99_ID,
    "master_identity_status": master.get("identity_status"),
    "review_category_policy": category_policy,
    "mutation": mutation,
    "rollback_snapshot": str(rollback_path),
    "request_sha256": sha256_text(updated_xml),
    "write_attempted": True,
    "write_success": False,
    "duplicates_untouched": [
        x.get("product_id") for x in resolution.get("duplicates", [])
    ],
}

try:
    response = client.update_product_xml(TARGET_PRODUCT_ID, updated_xml)
    audit["write_success"] = True
    audit["response_sha256"] = sha256_text(response)

    # Read back immediately to verify the site accepted the draft state.
    verify_xml = client.get_product_xml(TARGET_PRODUCT_ID)
    verify_path = AUDIT_DIR / f"{timestamp}_mela99_product_2076_after_v0664.xml"
    verify_path.write_text(verify_xml, encoding="utf-8")
    audit["readback_snapshot"] = str(verify_path)

    write_audit_record(audit_path, audit)

    print("M99 v0.6.6.4 - Controlled S3S Master WRITE_DRAFT")
    print("==================================================")
    print("Channel: mela99.com")
    print("Product ID: 2076")
    print("M99 ID: M99 100017")
    print("Master identity: EXISTING_CONFIRMED")
    print("Write mode: WRITE_DRAFT")
    print("Active after write: NO")
    print("Name action:", "CHANGE_APPROVED" if name_change else "KEEP")
    print("Slug/URL action: KEEP")
    print("Original categories kept:", sorted(before))
    print("Central review category added:", REVIEW_CATEGORY_ID)
    print("Duplicates untouched:", audit["duplicates_untouched"])
    print("Write success: YES")
    print("Rollback snapshot:", rollback_path)
    print("Audit:", audit_path)
    print("Readback snapshot:", verify_path)
except Exception as exc:
    audit["error_type"] = type(exc).__name__
    audit["error"] = str(exc)[:1000]
    write_audit_record(audit_path, audit)
    print("WRITE_DRAFT FAILED")
    print("Rollback snapshot preserved:", rollback_path)
    print("Audit:", audit_path)
    raise
