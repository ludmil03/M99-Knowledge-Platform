from __future__ import annotations
from pathlib import Path
import json, os, sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
import base64

REPO=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
ADMIN=REPO/"admin-platform"
REFERENCE="M99 100018"
M99EU_ID=2041

def load_dotenv_presence_only():
    # Load existing local .env values into process memory; never print values.
    loaded=[]
    for p in (REPO/".env", ADMIN/".env", REPO/"config/.env"):
        if not p.is_file(): continue
        for raw in p.read_text(encoding="utf-8",errors="replace").splitlines():
            s=raw.strip()
            if not s or s.startswith("#") or "=" not in s: continue
            k,v=s.split("=",1); k=k.strip(); v=v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k]=v
        loaded.append(str(p.relative_to(REPO)))
    return loaded

def present(name): return bool(os.environ.get(name,"").strip())

def norm_base(v):
    return v.strip().rstrip("/")

def ps_get(base,key,path,params=None):
    url=norm_base(base)+"/api/"+path.lstrip("/")
    if params: url+="?"+urlencode(params)
    auth=base64.b64encode((key+":").encode()).decode()
    req=Request(url,headers={"Authorization":"Basic "+auth,"Accept":"application/json","User-Agent":"M99-R730-R243"})
    try:
        with urlopen(req,timeout=20) as r:
            body=r.read().decode("utf-8","replace")
            return r.status, json.loads(body) if body.strip() else {}
    except HTTPError as e:
        return e.code, {"error":"HTTP_ERROR"}
    except (URLError,TimeoutError,OSError) as e:
        return None, {"error":type(e).__name__}

def extract_products(data):
    if isinstance(data,dict):
        p=data.get("products",[])
        if isinstance(p,list): return p
        if isinstance(p,dict): return [p]
        if "product" in data:
            q=data["product"]; return q if isinstance(q,list) else [q]
    return []

def m99eu_readback():
    need=["M99EU_API_KEY","M99EU_BASE_URL"]
    if not all(present(x) for x in need):
        return {"channel_id":"m99.eu","decision":"CREDENTIAL_SETUP_REQUIRED",
                "credentials_present":{x:present(x) for x in need},"write_allowed":False}
    base=os.environ["M99EU_BASE_URL"]; key=os.environ["M99EU_API_KEY"]
    status,byid=ps_get(base,key,f"products/{M99EU_ID}",{"output_format":"JSON"})
    products=extract_products(byid)
    p=products[0] if products else (byid.get("product") if isinstance(byid,dict) else None)
    if not isinstance(p,dict):
        return {"channel_id":"m99.eu","decision":"BLOCKED_EXISTING_2041_NOT_READABLE",
                "http_status":status,"write_allowed":False}
    ref=str(p.get("reference","")).strip()
    result={"channel_id":"m99.eu","http_status":status,"product_id":p.get("id"),
            "reference":ref,"active":p.get("active"),"visibility":p.get("visibility"),
            "id_category_default":p.get("id_category_default"),
            "id_tax_rules_group":p.get("id_tax_rules_group"),
            "cache_default_attribute":p.get("cache_default_attribute"),
            "write_allowed":False,"create_allowed":False}
    if str(p.get("id"))!=str(M99EU_ID):
        result["decision"]="BLOCKED_IDENTITY_CONFLICT"
    elif ref!=REFERENCE:
        result["decision"]="BLOCKED_REFERENCE_CONFLICT"
    else:
        # Independent duplicate lookup by canonical reference.
        s2,d2=ps_get(base,key,"products",{"filter[reference]":f"[{REFERENCE}]","display":"[id,reference,active]","output_format":"JSON"})
        hits=[x for x in extract_products(d2) if str(x.get("reference","")).strip()==REFERENCE]
        result["duplicate_lookup_http_status"]=s2
        result["exact_reference_hits"]=[{"id":x.get("id"),"reference":x.get("reference"),"active":x.get("active")} for x in hits]
        ids={str(x.get("id")) for x in hits}
        result["decision"]="UPDATE_EXISTING" if ids=={str(M99EU_ID)} else "BLOCKED_DUPLICATE_AMBIGUITY"
    return result

def generic_binding_matrix():
    # Binding proof only for channels whose exact credential names are already evidenced.
    return [
      {"channel_id":"mela99.com","bindings":{"M99_MELA99_API_KEY":present("M99_MELA99_API_KEY")},
       "decision":"BINDING_FOUND_NEEDS_BASE_URL_PROOF" if present("M99_MELA99_API_KEY") else "CREDENTIAL_SETUP_REQUIRED"},
      {"channel_id":"rabotni-drehi.com","bindings":{
       "M99_RABOTNI_DREHI_COM_USERNAME":present("M99_RABOTNI_DREHI_COM_USERNAME"),
       "M99_RABOTNI_DREHI_COM_APP_PASSWORD":present("M99_RABOTNI_DREHI_COM_APP_PASSWORD")},
       "decision":"BINDING_FOUND_NEEDS_BASE_URL_PROOF" if present("M99_RABOTNI_DREHI_COM_USERNAME") and present("M99_RABOTNI_DREHI_COM_APP_PASSWORD") else "CREDENTIAL_SETUP_REQUIRED"},
      *[{"channel_id":x,"bindings":{},"decision":"CREDENTIAL_PROVIDER_NOT_YET_PROVEN"}
        for x in ("medicinski-drehi.com","laviro.ro","alviro.ro","toplinka.com","dolibarr")]
    ]

def main():
    print("="*78)
    print("M99 R7.3.0 R2.4.3 REAL CREDENTIAL BINDING + LIVE API READBACK")
    print("GET ONLY / WRITE FALSE")
    print("="*78)
    loaded=load_dotenv_presence_only()
    print("Local config files loaded:",len(loaded),"(paths/values not printed)")
    print("M99EU_API_KEY:","PRESENT" if present("M99EU_API_KEY") else "NOT_PRESENT")
    print("M99EU_BASE_URL:","PRESENT" if present("M99EU_BASE_URL") else "NOT_PRESENT")
    m=m99eu_readback()
    print("\n[m99.eu]",m["decision"])
    for k in ("http_status","product_id","reference","active","visibility","id_category_default",
              "id_tax_rules_group","cache_default_attribute","duplicate_lookup_http_status","exact_reference_hits"):
        if k in m: print(" ",k,":",m[k])
    print(" CREATE_ALLOWED: FALSE")
    print("\nOTHER CHANNEL BINDINGS")
    matrix=generic_binding_matrix()
    for x in matrix: print(f"[{x['channel_id']}] {x['decision']} | presence={x['bindings']}")
    final={"version":"R7.3.0-R2.4.3","reference":REFERENCE,"write_allowed":False,
           "m99eu":m,"other_channels":matrix}
    out=Path.home()/"Desktop"/"M99_R730_R243_REAL_CREDENTIAL_BINDING_LIVE_READBACK.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(final,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print("\nWRITE_ALLOWED: FALSE")
    print("Report:",out)
    if m["decision"]=="UPDATE_EXISTING":
        print("[PASS] m99.eu Product 2041 identity + duplicate guard proven. READY FOR R2.5 BUILD.")
        return 0
    print("[BLOCKED] m99.eu not yet proven; no write attempted.")
    return 10

if __name__=="__main__": raise SystemExit(main())
