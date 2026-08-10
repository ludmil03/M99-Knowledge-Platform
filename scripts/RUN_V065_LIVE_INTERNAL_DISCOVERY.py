from pathlib import Path
import json

from core.internal_existing_product_discovery import (
    discover_existing_product,
    InternalDiscoveryDecision,
)
from integrations.catalog_discovery import (
    ReadOnlyAdapterConfig,
    PrestaShopReadOnlyAdapter,
    WooCommerceReadOnlyAdapter,
)


ROOT = Path(".")
CONFIG = ROOT / "config/channels/internal_discovery_v0.6.5.json"
PRODUCT = ROOT / "tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
OUTPUT = ROOT / "output/diadora_glove_abox_low_pro_s1ps_v065_live_internal_discovery.json"

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
source = json.loads(PRODUCT.read_text(encoding="utf-8"))
manufacturer = source["manufacturer_evidence"]["facts"]

identity = {
    "brand": source["brand"],
    "model_name": manufacturer["model_name"],
    "manufacturer_item": manufacturer["manufacturer_item"],
    "ean": None,
    "legacy_identifiers": [
        x["value"] for x in source.get("legacy_identifiers", [])
        if x.get("value")
    ],
    "protection_class": manufacturer["protection_class"],
}

results = {}

for channel, c in cfg["channels"].items():
    base = ReadOnlyAdapterConfig(
        channel=channel,
        base_url=c["base_url"],
        timeout_seconds=20,
    )

    if c["adapter"] == "prestashop":
        adapter = PrestaShopReadOnlyAdapter(base, c["api_key_env"])
    elif c["adapter"] == "woocommerce":
        adapter = WooCommerceReadOnlyAdapter(
            base,
            c["key_env"],
            c["secret_env"],
        )
    else:
        results[channel] = {
            "channel": channel,
            "decision": InternalDiscoveryDecision.ERROR.value,
            "action": "UNSUPPORTED_ADAPTER",
            "publish_allowed": False,
        }
        continue

    if not adapter.configured():
        results[channel] = {
            "channel": channel,
            "decision": InternalDiscoveryDecision.NOT_CONFIGURED.value,
            "action": "SET_READ_ONLY_CREDENTIAL_ENV_VARS",
            "publish_allowed": False,
        }
        continue

    try:
        candidates = adapter.search(identity)
        results[channel] = discover_existing_product(
            channel,
            identity,
            candidates,
        )
        results[channel]["read_only_candidates_found"] = len(candidates)
    except Exception as exc:
        results[channel] = {
            "channel": channel,
            "decision": InternalDiscoveryDecision.ERROR.value,
            "action": "OPERATOR_REVIEW_CONNECTION",
            "publish_allowed": False,
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }

payload = {
    "schema_version": "0.6.5",
    "mode": "LIVE_READ_ONLY_INTERNAL_DISCOVERY",
    "http_policy": "GET_ONLY",
    "writes": {
        "dolibarr": False,
        "channels": False,
        "supplier": False,
    },
    "canonical_identity": identity,
    "results": results,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print("M99 v0.6.5 LIVE Internal Discovery")
print("==================================")
print("HTTP policy: GET ONLY")
for channel, result in results.items():
    print(" -", channel, "=>", result["decision"], "|", result["action"])
print("Writes to websites: NO")
print("Writes to Dolibarr: NO")
print("Output:", OUTPUT)
