from pathlib import Path
import base64,json,os
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
SEC=Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"M99"/"secure"/"channels.credentials.json"
REF="M99 100018";PID=2041
def creds():
 try:return json.loads(SEC.read_text(encoding="utf-8")).get("channels",{})
 except:return {}
def getj(url,h):
 try:
  with urlopen(Request(url,headers=h,method="GET"),timeout=20) as r:return r.status,json.loads(r.read().decode() or "{}")
 except HTTPError as e:return e.code,{"error":"HTTP_ERROR"}
 except Exception as e:return None,{"error":type(e).__name__}
def products(d):
 if not isinstance(d,dict):return []
 x=d.get("products",d.get("product",[]));return x if isinstance(x,list) else ([x] if isinstance(x,dict) else [])
def check_m99eu(c):
 x=c.get("m99.eu")
 if not x:return {"decision":"CREDENTIAL_SETUP_REQUIRED","create_allowed":False,"write_allowed":False}
 b=x["base_url"].rstrip("/");k=x["api_key"];h={"Authorization":"Basic "+base64.b64encode((k+":").encode()).decode(),"Accept":"application/json"}
 s,d=getj(b+f"/api/products/{PID}?output_format=JSON",h);p=(products(d) or [None])[0]
 r={"http":s,"create_allowed":False,"write_allowed":False}
 if not isinstance(p,dict):r["decision"]="BLOCKED_READBACK";return r
 r.update(product_id=p.get("id"),reference=str(p.get("reference","")).strip(),active=p.get("active"),visibility=p.get("visibility"),tax_group=p.get("id_tax_rules_group"),default_attribute=p.get("cache_default_attribute"))
 if str(p.get("id"))!=str(PID) or r["reference"]!=REF:r["decision"]="BLOCKED_IDENTITY";return r
 q=urlencode({"filter[reference]":f"[{REF}]","display":"[id,reference,active]","output_format":"JSON"})
 s2,d2=getj(b+"/api/products?"+q,h);hits=[z for z in products(d2) if str(z.get("reference","")).strip()==REF]
 r["duplicate_http"]=s2;r["exact_ids"]=[z.get("id") for z in hits]
 r["decision"]="UPDATE_EXISTING" if [str(z.get("id")) for z in hits]==[str(PID)] else "BLOCKED_DUPLICATE"
 return r
def main():
 c=creds();r=check_m99eu(c)
 print("="*78);print("M99 R7.3.0 R2.5 AUTH + IDENTITY PREFLIGHT — GET ONLY");print("="*78)
 print("[m99.eu]",r["decision"],"| HTTP",r.get("http"),"| ID",r.get("product_id"),"| REF",r.get("reference"),"| exact",r.get("exact_ids"))
 for cid in ("mela99.com","medicinski-drehi.com","rabotni-drehi.com","laviro.ro","alviro.ro","toplinka.com","dolibarr"):
  print("["+cid+"]","CREDENTIAL_CONFIGURED" if cid in c else "CREDENTIAL_SETUP_REQUIRED")
 out=Path.home()/"Desktop"/"M99_R730_R25_MULTICHANNEL_PREFLIGHT.json";out.write_text(json.dumps({"m99eu":r,"configured_channels":sorted(c),"write_allowed":False},indent=2),encoding="utf-8")
 print("CREATE_ALLOWED: FALSE\nWRITE_ALLOWED: FALSE\nReport:",out)
 return 0 if r["decision"]=="UPDATE_EXISTING" else 10
if __name__=="__main__":raise SystemExit(main())
