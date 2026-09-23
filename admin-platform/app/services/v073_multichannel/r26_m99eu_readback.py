from __future__ import annotations
import base64,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
REF="M99 100018";PID=2041
def getj(url,key):
 h={"Authorization":"Basic "+base64.b64encode((key+":").encode()).decode(),"Accept":"application/json","User-Agent":"M99-R730-R26"}
 try:
  with urlopen(Request(url,headers=h,method="GET"),timeout=20) as r:return r.status,json.loads(r.read().decode("utf-8","replace") or "{}")
 except HTTPError as e:return e.code,{"error":"HTTP_ERROR"}
 except Exception as e:return None,{"error":type(e).__name__}
def ps(d):
 if not isinstance(d,dict):return []
 x=d.get("products",d.get("product",[]));return x if isinstance(x,list) else ([x] if isinstance(x,dict) else [])
def main():
 print("="*78);print("M99 R7.3.0 R2.6 M99.EU PROVEN-ENV READBACK");print("GET ONLY / NO WRITE");print("="*78)
 key=os.environ.get("M99EU_API_KEY","").strip();base=os.environ.get("M99EU_BASE_URL","https://m99.eu").strip().rstrip("/")
 print("M99EU_API_KEY:","PRESENT" if key else "NOT_PRESENT");print("Base URL:",base)
 if not key: print("[BLOCKED] Credential not present in this process.");return 10
 s,d=getj(base+f"/api/products/{PID}?output_format=JSON",key);p=(ps(d) or [None])[0]
 print("Product GET HTTP:",s)
 if not isinstance(p,dict):print("[BLOCKED] Product 2041 not readable.");return 11
 ref=str(p.get("reference","")).strip()
 print("Product ID:",p.get("id"));print("Reference:",ref);print("Active:",p.get("active"));print("Visibility:",p.get("visibility"))
 if str(p.get("id"))!=str(PID) or ref!=REF:print("[BLOCKED] Identity mismatch.");return 12
 q=urlencode({"filter[reference]":f"[{REF}]","display":"[id,reference,active]","output_format":"JSON"})
 s2,d2=getj(base+"/api/products?"+q,key);hits=[x for x in ps(d2) if str(x.get("reference","")).strip()==REF]
 ids=[x.get("id") for x in hits];print("Duplicate GET HTTP:",s2);print("Exact IDs:",ids)
 if [str(x) for x in ids]!=[str(PID)]:print("[BLOCKED] Duplicate/ambiguity gate.");return 13
 out=Path.home()/"Desktop"/"M99_R730_R26_M99EU_READBACK.json"
 out.write_text(json.dumps({"decision":"UPDATE_EXISTING","product_id":PID,"reference":REF,"http":s,"duplicate_http":s2,"exact_ids":ids,"write_allowed":False},indent=2),encoding="utf-8")
 print("[PASS] UPDATE_EXISTING identity/readback proven.")
 print("CREATE_ALLOWED: FALSE");print("WRITE_ALLOWED: FALSE");print("Report:",out);return 0
if __name__=="__main__":raise SystemExit(main())
