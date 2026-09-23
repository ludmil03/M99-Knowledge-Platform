import base64,hashlib,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
def info(v):
 s=v or ""; t=s.strip()
 return {"present":bool(s),"length":len(s),"stripped_length":len(t),"outer_ws":s!=t,"any_ws":any(c.isspace() for c in t),"fingerprint":hashlib.sha256(t.encode()).hexdigest()[:12] if t else None}
def get(url,key):
 h={"Authorization":"Basic "+base64.b64encode((key+":").encode()).decode(),"Accept":"application/json","User-Agent":"M99-R730-R261"}
 try:
  with urlopen(Request(url,headers=h,method="GET"),timeout=20) as r:return r.status
 except HTTPError as e:return e.code
 except Exception:return None
def main():
 print("="*78);print("M99 R7.3.0 R2.6.1 AUTH DIAGNOSTIC - GET ONLY");print("="*78)
 k=os.environ.get("M99EU_API_KEY",""); b=os.environ.get("M99EU_BASE_URL","https://m99.eu").strip().rstrip("/"); i=info(k)
 print("Key present:",i["present"]);print("Length:",i["length"]);print("Outer whitespace:",i["outer_ws"]);print("Any whitespace:",i["any_ws"]);print("Fingerprint SHA256/12:",i["fingerprint"])
 if not i["present"]: print("[BLOCKED] No key.");return 10
 if i["outer_ws"] or i["any_ws"]: print("[BLOCKED] Suspicious key formatting.");return 11
 a=get(b+"/api/?output_format=JSON",k); p=get(b+"/api/products/2041?output_format=JSON",k)
 print("API root GET HTTP:",a);print("Product 2041 GET HTTP:",p)
 if a in (401,403): d,rc="KEY_OR_WEBSERVICE_AUTH_REJECTED",12
 elif a==200 and p in (401,403): d,rc="KEY_ACCEPTED_PRODUCTS_PERMISSION_REJECTED",13
 elif p==200: d,rc="AUTH_AND_PRODUCT_GET_ACCEPTED",0
 else: d,rc="INCONCLUSIVE_HTTP_RESULT",14
 out=Path.home()/"Desktop"/"M99_R730_R261_AUTH_DIAGNOSTIC.json"
 out.write_text(json.dumps({"key_info":i,"api_root_http":a,"product_http":p,"decision":d,"write_allowed":False},indent=2),encoding="utf-8")
 print("Decision:",d);print("WRITE_ALLOWED: FALSE");print("Report:",out);return rc
if __name__=="__main__":raise SystemExit(main())
