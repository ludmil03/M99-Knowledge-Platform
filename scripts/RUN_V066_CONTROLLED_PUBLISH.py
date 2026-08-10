from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from core.controlled_publish_policy import (
    PublishAction,
    PublishMode,
    ExistingChannelIdentity,
    NameChangeProposal,
    decide_name_action,
    build_identity_lock,
    required_confirmation,
    validate_publish_gates,
)
from core.mela99_publish_payload import (
    PublishDocument,
    build_product_xml,
    build_create_product_xml,
    mutate_existing_product_xml,
)
from integrations.channel_publish import (
    Mela99ClientConfig,
    ControlledMela99Publisher,
    write_audit_record,
    sha256_text,
)


ROOT = Path(".")
V0641 = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v0641_preview.json"
V065 = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v065_live_internal_discovery.json"
FALLBACK_V065 = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v065_preview.json"
AUDIT_DIR = ROOT / "output/publish_audit"
ROLLBACK_DIR = ROOT / "output/publish_rollback"

TARGET_CHANNEL = "mela99.com"
M99_ID = "M99 100002"
REFERENCE = "701.183121_80013"
TEST_CATEGORY_ID = 938


def _slugify(value: str) -> str:
    value = value.casefold()
    replacements = {
        "ă":"a","â":"a","î":"i","ș":"s","ş":"s","ț":"t","ţ":"t",
        "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ж":"zh","з":"z",
        "и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p",
        "р":"r","с":"s","т":"t","у":"u","ф":"f","х":"h","ц":"ts","ч":"ch",
        "ш":"sh","щ":"sht","ъ":"a","ь":"","ю":"yu","я":"ya",
    }
    value = "".join(replacements.get(ch, ch) for ch in value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _xml_text_by_lang(root, tag, lang_id):
    node = root.find(f".//{tag}")
    if node is None:
        return None
    for lang in node.findall(".//language"):
        if str(lang.attrib.get("id")) == str(lang_id):
            return lang.text or ""
    return None


def _extract_existing_identity(product_xml: str, product_id: str, url: str | None):
    root = ET.fromstring(product_xml)
    name_bg = _xml_text_by_lang(root, "name", 1)
    name_en = _xml_text_by_lang(root, "name", 2)
    slug_bg = _xml_text_by_lang(root, "link_rewrite", 1)
    slug_en = _xml_text_by_lang(root, "link_rewrite", 2)
    reference_node = root.find(".//reference")
    reference = reference_node.text.strip() if reference_node is not None and reference_node.text else None

    return {
        "identity": ExistingChannelIdentity(
            product_id=product_id,
            product_name=name_bg or name_en,
            slug=slug_bg or slug_en,
            url=url,
            legacy_identifiers=[reference] if reference else [],
        ),
        "name_bg": name_bg,
        "name_en": name_en,
        "slug_bg": slug_bg,
        "slug_en": slug_en,
        "reference": reference,
    }


def _load_json(path: Path):
    if not path.exists():
        raise RuntimeError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    mode_text = os.environ.get("M99_PUBLISH_MODE", "DRY_RUN").strip().upper()
    try:
        mode = PublishMode(mode_text)
    except ValueError:
        raise RuntimeError(
            "M99_PUBLISH_MODE must be DRY_RUN, WRITE_DRAFT, or PUBLISH_LIVE"
        )

    content_preview = _load_json(V0641)
    discovery_path = V065 if V065.exists() else FALLBACK_V065
    discovery = _load_json(discovery_path)

    # LIVE write is forbidden unless discovery was the real GET-only live run.
    live_discovery = discovery.get("mode") == "LIVE_READ_ONLY_INTERNAL_DISCOVERY"

    content_quality = content_preview.get("content_quality", {})
    content_ready = content_quality.get("status") == "CONTENT_READY"

    if live_discovery:
        channel_result = discovery["results"].get(TARGET_CHANNEL, {})
    else:
        channel_result = (
            discovery.get("internal_existing_product_discovery", {})
            .get("results", {})
            .get(TARGET_CHANNEL, {})
        )

    decision = channel_result.get("decision")
    if decision == "EXISTING":
        action = PublishAction.UPDATE
    elif decision == "NEW":
        action = PublishAction.CREATE
    else:
        action = PublishAction.BLOCK

    if action == PublishAction.BLOCK:
        raise RuntimeError(
            f"Publish blocked: internal discovery decision for {TARGET_CHANNEL} is {decision}"
        )

    operator_approved = (
        os.environ.get("M99_OPERATOR_APPROVED", "").strip().upper() == "YES"
    )
    pricing_approved = (
        os.environ.get("M99_PRICING_APPROVED", "").strip().upper() == "YES"
    )
    availability_approved = (
        os.environ.get("M99_AVAILABILITY_APPROVED", "").strip().upper() == "YES"
    )

    gates = {
        "single_product_scope": True,
        "target_channel_is_mela99": True,
        "content_ready": content_ready,
        "internal_discovery_complete": decision in ("EXISTING", "NEW"),
        "operator_approved": operator_approved,
        "audit_enabled": True,
        "rollback_enabled": True,
        "pricing_approved": pricing_approved,
        "availability_approved": availability_approved,
        "publish_mode": mode.value,
    }

    failures = validate_publish_gates(gates)

    # DRY_RUN is allowed without the real live discovery or operator approval.
    if mode != PublishMode.DRY_RUN:
        if not live_discovery:
            failures.append("GATE_FAILED:live_internal_discovery_required")
        if not operator_approved:
            failures.append("GATE_FAILED:operator_approved")

    # WRITE_DRAFT writes inactive product content into the site, but does not write
    # a sale price when pricing is unapproved.
    if mode == PublishMode.WRITE_DRAFT:
        failures = [
            x for x in failures
            if x != "GATE_FAILED:pricing_approved"
            and x != "GATE_FAILED:availability_approved"
        ]

    if failures:
        raise RuntimeError("Publish gates failed: " + ", ".join(sorted(set(failures))))

    expected = required_confirmation(mode, action)
    supplied = os.environ.get("M99_PUBLISH_CONFIRMATION", "")

    if mode != PublishMode.DRY_RUN and supplied != expected:
        raise RuntimeError(
            "Confirmation mismatch. Required exact value: " + expected
        )

    mela_content = content_preview["content_seo_preview"]["mela99.com"]
    bg = mela_content["bg"]
    en = mela_content["en"]

    client = ControlledMela99Publisher(
        Mela99ClientConfig(
            base_url="https://mela99.com",
            api_key_env="M99_MELA99_API_KEY",
        )
    )

    existing_snapshot = None
    existing_info = None
    product_id = channel_result.get("selected_product_id")
    product_url = channel_result.get("selected_url")

    # Determine names and identity lock.
    proposed_bg = bg["h1"].replace("Работни обувки ", "", 1).strip()
    proposed_en = en["h1"].replace(" Safety Shoes", "").strip()

    name_change_approved = (
        os.environ.get("M99_NAME_CHANGE_APPROVED", "").strip().upper() == "YES"
    )
    name_evidence_status = os.environ.get(
        "M99_NAME_CHANGE_EVIDENCE", "NOT_PROVEN"
    ).strip().upper()

    if action == PublishAction.UPDATE:
        if mode == PublishMode.DRY_RUN:
            # In dry-run, do not call the live site. Use discovery data only.
            existing_name = channel_result.get("selected_name")
            existing_identity = ExistingChannelIdentity(
                product_id=str(product_id) if product_id else None,
                product_name=existing_name,
                slug=channel_result.get("selected_slug"),
                url=product_url,
                legacy_identifiers=[],
            )
            existing_info = {
                "identity": existing_identity,
                "name_bg": existing_name,
                "name_en": existing_name,
                "slug_bg": channel_result.get("selected_slug"),
                "slug_en": channel_result.get("selected_slug"),
            }
        else:
            existing_snapshot = client.get_product_xml(str(product_id))
            existing_info = _extract_existing_identity(
                existing_snapshot,
                str(product_id),
                product_url,
            )

        proposal = NameChangeProposal(
            current_name=existing_info["name_bg"] or existing_info["name_en"],
            proposed_name=proposed_bg,
            evidence_status=name_evidence_status,
            operator_approved=name_change_approved,
        )
        name_decision = decide_name_action(
            existing_info["identity"],
            proposal,
        )
        identity_lock = build_identity_lock(
            existing_info["identity"],
            name_decision,
        )

        # Existing product names stay unchanged unless separately approved.
        if name_decision["action"] == "CHANGE_APPROVED":
            name_bg = proposed_bg
            name_en = proposed_en
        else:
            name_bg = existing_info["name_bg"] or proposed_bg
            name_en = existing_info["name_en"] or proposed_en

        doc = PublishDocument(
            name_bg=name_bg,
            name_en=name_en,
            short_bg=bg["short_description"],
            short_en=en["short_description"],
            long_bg=bg["long_description"],
            long_en=en["long_description"],
            meta_title_bg=bg["seo_title"],
            meta_title_en=en["seo_title"],
            meta_description_bg=bg["meta_description"],
            meta_description_en=en["meta_description"],
            reference=existing_info.get("reference") or REFERENCE,
            category_id=TEST_CATEGORY_ID,
            active=(mode == PublishMode.PUBLISH_LIVE),
            price_ex_vat=None,
        )

        # Never regenerate URL/slug on UPDATE.
        if mode == PublishMode.DRY_RUN:
            payload_xml = None
            payload_status = "WAITING_FOR_LIVE_EXISTING_FULL_XML_SNAPSHOT"
        else:
            payload_xml = mutate_existing_product_xml(
                existing_snapshot,
                doc,
                change_name=(name_decision["action"] == "CHANGE_APPROVED"),
            )
            payload_status = "READY_FULL_SNAPSHOT_MUTATION"

    else:
        name_decision = {
            "action": "GENERATE_FOR_NEW_PRODUCT",
            "name_to_write": proposed_bg,
        }
        identity_lock = build_identity_lock(None, name_decision)

        slug_bg = _slugify(bg["h1"])
        slug_en = _slugify(en["h1"])

        sale_price = None
        if pricing_approved:
            value = os.environ.get("M99_APPROVED_PRICE_EX_VAT")
            if value:
                sale_price = float(value)

        if mode == PublishMode.PUBLISH_LIVE and sale_price is None:
            raise RuntimeError(
                "PUBLISH_LIVE requires M99_APPROVED_PRICE_EX_VAT"
            )

        doc = PublishDocument(
            name_bg=bg["h1"],
            name_en=en["h1"],
            short_bg=bg["short_description"],
            short_en=en["short_description"],
            long_bg=bg["long_description"],
            long_en=en["long_description"],
            meta_title_bg=bg["seo_title"],
            meta_title_en=en["seo_title"],
            meta_description_bg=bg["meta_description"],
            meta_description_en=en["meta_description"],
            reference=REFERENCE,
            category_id=TEST_CATEGORY_ID,
            active=(mode == PublishMode.PUBLISH_LIVE),
            price_ex_vat=sale_price,
        )
        payload_xml = build_create_product_xml(
            doc,
            slug_bg=slug_bg,
            slug_en=slug_en,
        )
        payload_status = "READY"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_path = AUDIT_DIR / f"{timestamp}_{M99_ID.replace(' ','_')}_{TARGET_CHANNEL}_{mode.value}.json"

    audit = {
        "timestamp_utc": timestamp,
        "schema_version": "0.6.6",
        "mode": mode.value,
        "action": action.value,
        "channel": TARGET_CHANNEL,
        "m99_id": M99_ID,
        "reference": REFERENCE,
        "discovery_source": str(discovery_path),
        "discovery_decision": decision,
        "gates": gates,
        "identity_lock": identity_lock,
        "name_decision": name_decision,
        "payload_status": payload_status,
        "payload_sha256": sha256_text(payload_xml) if payload_xml else None,
        "write_attempted": False,
        "write_success": False,
        "response_sha256": None,
        "rollback_snapshot": None,
    }

    if mode == PublishMode.DRY_RUN:
        write_audit_record(audit_path, audit)
        print("M99 Controlled Single Product Publish v0.6.6")
        print("============================================")
        print("Mode: DRY_RUN")
        print("Channel:", TARGET_CHANNEL)
        print("Action:", action.value)
        print("Discovery:", decision)
        print("Content:", "CONTENT_READY" if content_ready else "REVIEW")
        print("Name action:", name_decision["action"])
        print("URL/slug update:", "LOCKED / KEEP" if action == PublishAction.UPDATE else "GENERATE_ON_CREATE")
        print("Payload:", payload_status)
        print("Write attempted: NO")
        print("Audit:", audit_path)
        return 0

    # Actual controlled write.
    audit["write_attempted"] = True

    try:
        if action == PublishAction.UPDATE:
            ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
            rollback_path = ROLLBACK_DIR / f"{timestamp}_product_{product_id}.xml"
            rollback_path.write_text(existing_snapshot, encoding="utf-8")
            audit["rollback_snapshot"] = str(rollback_path)

            response_text = client.update_product_xml(
                str(product_id),
                payload_xml,
            )
        else:
            response_text = client.create_product_xml(payload_xml)

        audit["write_success"] = True
        audit["response_sha256"] = sha256_text(response_text)
        write_audit_record(audit_path, audit)

        print("M99 Controlled Single Product Publish v0.6.6")
        print("============================================")
        print("Mode:", mode.value)
        print("Channel:", TARGET_CHANNEL)
        print("Action:", action.value)
        print("Write success: YES")
        print("Product active:", "YES" if mode == PublishMode.PUBLISH_LIVE else "NO / DRAFT")
        print("Name action:", name_decision["action"])
        print("URL/slug on UPDATE: PRESERVED")
        print("Audit:", audit_path)
        if audit["rollback_snapshot"]:
            print("Rollback snapshot:", audit["rollback_snapshot"])
        return 0

    except Exception as exc:
        audit["error_type"] = type(exc).__name__
        audit["error"] = str(exc)[:1000]
        write_audit_record(audit_path, audit)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
