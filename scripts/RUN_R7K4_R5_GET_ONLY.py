from __future__ import annotations
from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path: sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.controlled_live_supplier_get_r5 import LiveFetchRequest,controlled_get
def main():
    p=argparse.ArgumentParser(description="R7K.4 R5 operator-controlled GET-only probe")
    p.add_argument("--supplier",required=True); p.add_argument("--url",required=True)
    p.add_argument("--host",required=True); p.add_argument("--reference",required=True)
    p.add_argument("--confirm",default="")
    a=p.parse_args()
    if a.confirm != "GET SUPPLIER EVIDENCE":
        raise SystemExit("BLOCKED: exact --confirm 'GET SUPPLIER EVIDENCE' required")
    try: import requests
    except Exception as e: raise SystemExit("BLOCKED: requests unavailable")
    r=LiveFetchRequest(a.supplier,a.url,a.host,a.reference,True)
    out=controlled_get(r,lambda method,url,**kw: requests.request(method,url,**kw))
    safe={"status":out.status,"http_status":out.http_status,"final_url":out.final_url,
          "content_type":out.content_type,"failure_reason":out.failure_reason,
          "method":out.method,"writes_performed":out.writes_performed,
          "body_bytes":len((out.body or "").encode("utf-8"))}
    print(json.dumps(safe,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
