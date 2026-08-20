from __future__ import annotations

import json

from integrations.m99eu import build_test_draft_payload


def main() -> int:
    payload = build_test_draft_payload()
    print("M99EU SANDBOX DRY RUN")
    print("The following JSON WOULD be sent to WooCommerce.")
    print("Nothing is sent by this command.\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
