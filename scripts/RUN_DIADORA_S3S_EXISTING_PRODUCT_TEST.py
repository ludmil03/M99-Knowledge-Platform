from pathlib import Path
import json
from core.internal_existing_product_discovery import discover_existing_product, InternalDiscoveryDecision
from integrations.catalog_discovery import ReadOnlyAdapterConfig, PrestaShopReadOnlyAdapter

ROOT = Path(".")
CONFIG = ROOT / "config/channels/internal_discovery_v0.6.5.json"
PRODUCT = ROOT / "tests/fixtures/diadora_glove_abox_low_pro_s3s_real.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s3s_v0662_live_internal_discovery.json"

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
source = json.loads(PRODUCT.read_text(encoding="utf-8"))
facts = source["manufacturer_evidence"]["facts"]

identity = {
    "brand": source["productgroup"]["brand"],
    "model_name": facts["model_name"],
    "manufacturer_item": facts["manufacturer_item"],
    "ean": None,
    "legacy_identifiers": [],
    "protection_class": facts["protection_class"],
}

channel = "mela99.com"
c = cfg["channels"][channel]
adapter = PrestaShopReadOnlyAdapter(
    ReadOnlyAdapterConfig(channel=channel, base_url=c["base_url"], timeout_seconds=20),
    c["api_key_env"],
)

if not adapter.configured():
    result = {
        "channel": channel,
        "decision": InternalDiscoveryDecision.NOT_CONFIGURED.value,
        "action": "SET_READ_ONLY_CREDENTIAL_ENV_VARS",
        "publish_allowed": False,
    }
else:
    try:
        candidates = adapter.search(identity)
        result = discover_existing_product(channel, identity, candidates)
        result["read_only_candidates_found"] = len(candidates)
    except Exception as exc:
        result = {
            "channel": channel,
            "decision": InternalDiscoveryDecision.ERROR.value,
            "action": "OPERATOR_REVIEW_CONNECTION",
            "publish_allowed": False,
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }

data = {
    "schema_version": "0.6.6.2",
    "mode": "LIVE_READ_ONLY_INTERNAL_DISCOVERY",
    "http_policy": "GET_ONLY",
    "writes": {"channels": False, "dolibarr": False, "supplier": False},
    "canonical_identity": identity,
    "known_public_channel_evidence": source["known_channel_evidence"][channel],
    "supplier_evidence": source["supplier_candidates"],
    "result": result,
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

print("M99 v0.6.6.2 - Diadora S3S Existing Product Test")
print("=================================================")
print("HTTP policy: GET ONLY")
print("Product:", identity["model_name"])
print("Manufacturer item:", identity["manufacturer_item"])
print("Protection class:", identity["protection_class"])
print("mela99.com =>", result["decision"], "|", result["action"])
print("Candidates found:", result.get("read_only_candidates_found", 0))
print("Writes to websites: NO")
print("Writes to Dolibarr: NO")
print("Output:", OUTPUT)
if result["decision"] == "NEW":
    print("WARNING: NEW conflicts with known public channel evidence. DO NOT PUBLISH.")
