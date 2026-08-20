from __future__ import annotations

import json

from integrations.m99eu import M99EUClient, load_m99eu_config


def main() -> int:
    config = load_m99eu_config()
    client = M99EUClient(config)
    result = client.preflight()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["authenticated"] or not result["products_endpoint_readable"]:
        return 2
    print("\nM99EU API PREFLIGHT: PASS")
    print("No product was created or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
