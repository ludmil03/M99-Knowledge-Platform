from __future__ import annotations
import argparse, json, time
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--decision", choices=["APPROVE","REJECT"], required=True)
    ap.add_argument("--notes", default="")
    args=ap.parse_args()

    p=Path(args.state)
    data=json.loads(p.read_text(encoding="utf-8"))
    if data.get("operator_status") != "PENDING_REVIEW":
        raise SystemExit(f"State is not PENDING_REVIEW: {data.get('operator_status')}")

    data["operator_reviewed_at"]=time.strftime("%Y-%m-%dT%H:%M:%S%z")
    data["operator_notes"]=args.notes
    if args.decision=="APPROVE":
        data["operator_status"]="APPROVED"
        data["daily_sync_status"]="READY_FOR_BASELINE"
        data["delete_status"]="KEEP_PRODUCT"
    else:
        data["operator_status"]="REJECTED"
        data["daily_sync_status"]="BLOCKED"
        data["delete_status"]="OPERATOR_DECISION_FIX_OR_DELETE"

    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
