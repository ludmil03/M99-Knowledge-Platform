from __future__ import annotations
import argparse, json, time
from pathlib import Path

DYNAMIC_FIELDS={"price","availability","variants"}
CONTENT_FIELDS={"name","description","description_short","features","images","meta_title","meta_description","slug"}

def diff(old, new):
    changes=[]
    for key in sorted(set(old)|set(new)):
        if old.get(key)!=new.get(key):
            policy="AUTO_SYNC_CANDIDATE" if key in DYNAMIC_FIELDS else "OPERATOR_REVIEW"
            changes.append({"field":key,"old":old.get(key),"new":new.get(key),"policy":policy})
    return changes

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--baseline", required=True)
    args=ap.parse_args()

    state=json.loads(Path(args.state).read_text(encoding="utf-8"))
    if state.get("operator_status")!="APPROVED":
        raise SystemExit("Daily sync blocked: product is not operator APPROVED")

    snap=json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    base=Path(args.baseline)
    if not base.exists():
        base.write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding="utf-8")
        print("DAILY SYNC BASELINE CREATED")
        return 0

    old=json.loads(base.read_text(encoding="utf-8"))
    changes=diff(old,snap)
    result={
        "generated_at":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "product_id":state["product_id"],
        "reference":state["reference"],
        "changes":changes,
        "automatic_write_performed":False,
        "rule":"price/availability/variants may become auto-sync; content/SEO/images require operator review"
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
