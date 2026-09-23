from __future__ import annotations
from pathlib import Path
import base64, importlib.util, json, os
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

REPO=Path(r"C:\Users\user\Documents\GitHub\M99-Knowledge-Platform")
ADMIN=REPO/"admin-platform"
REFERENCE="M99 100018"
PRODUCT_ID=2041
CHANNEL_ID="m99.eu"

def _domain_from_registry():
    candidates=[
        ADMIN/"app/services/v073_multichannel/channel_registry.py",
        REPO/"core/channels.py",
    ]
    # Preferred: additive R2.2 registry, if installed.
    p=candidates[0]
    if p.is_file():
        spec=importlib.util.spec_from_file_location("_m99_channel_registry",p)
        m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        channels=getattr(m,"CHANNELS",None)
        if isinstance(channels,dict):
            c=channels.get(CHANNEL_ID)
            if isinstance(c,dict):
                for k in ("domain","base_url","url"):
                    v=c.get(k)
                    if v: return str(v).strip().rstrip("/"),"R2.2_CHANNEL_REGISTRY"
        if isinstance(channels,(list,tuple)):
            for c in channels:
                if isinstance(c,dict) and c.get("channel_id")==CHANNEL_ID:
                    for k in ("domain","base_url","url"):
                        if c.get(k): return str(c[k]).strip().rstrip("/"),"R2.2_CHANNEL_REGISTRY"
    # Conservative fallback: domain is channel identity, not credential material.
    return "https://m99.eu","CHANNEL_ID_DOMAIN_FALLBACK"

def _get(base,key,path,params=None):
    url=base.rstrip("/")+"/api/"+path.lstrip("/")
    if params: url+="?"+urlencode(params)
    auth=base64.b64encode((key+":").encode()).decode()
    req=Request(url,headers={"Authorization":"Basic "+auth,"Accept":"application/json","User-Agent":"M99-R730-R244"},method="GET")
    try:
        with urlopen(req,timeout=20) as r:
            raw=r.read().decode("utf-8","replace")
            return r.status, json.loads(raw) if raw.strip() else {}
    except HTTPError as e: return e.code,{"error":"HTTP_ERROR"}
    except (URLError,TimeoutError,OSError) as e: return None,{"error":type(e).__name__}

def _products(d):
    if not isinstance(d,dict): return []
    x=d.get("products")
    if isinstance(x,list): return x
    if isinstance(x,dict): return [x]
    x=d.get("product")
    if isinstance(x,list): return x
    if isinstance(x,dict): return [x]
    return []

def readback():
    base,source=_domain_from_registry()
    key=os.environ.get("M99EU_API_KEY","").strip()
    if not key:
        return {"decision":"CREDENTIAL_SETUP_REQUIRED","base_url_source":source,
                "api_key_present":False,"create_allowed":False,"write_allowed":False}
    s1,d1=_get(base,key,f"products/{PRODUCT_ID}",{"output_format":"JSON"})
    ps=_products(d1)
    p=ps[0] if ps else None
    out={"channel_id":CHANNEL_ID,"base_url_source":source,"api_key_present":True,
         "product_get_http_status":s1,"create_allowed":False,"write_allowed":False}
    if not isinstance(p,dict):
        out["decision"]="BLOCKED_PRODUCT_2041_NOT_READABLE"; return out
    out.update({"product_id":p.get("id"),"reference":str(p.get("reference","")).strip(),
                "active":p.get("active"),"visibility":p.get("visibility"),
                "id_category_default":p.get("id_category_default"),
                "id_tax_rules_group":p.get("id_tax_rules_group"),
                "cache_default_attribute":p.get("cache_default_attribute")})
    if str(p.get("id"))!=str(PRODUCT_ID):
        out["decision"]="BLOCKED_IDENTITY_CONFLICT"; return out
    if out["reference"]!=REFERENCE:
        out["decision"]="BLOCKED_REFERENCE_CONFLICT"; return out
    s2,d2=_get(base,key,"products",{"filter[reference]":f"[{REFERENCE}]",
             "display":"[id,reference,active]","output_format":"JSON"})
    hits=[x for x in _products(d2) if str(x.get("reference","")).strip()==REFERENCE]
    out["duplicate_lookup_http_status"]=s2
    out["exact_reference_hits"]=[{"id":x.get("id"),"reference":x.get("reference"),"active":x.get("active")} for x in hits]
    ids=[str(x.get("id")) for x in hits]
    out["decision"]="UPDATE_EXISTING" if ids==[str(PRODUCT_ID)] else "BLOCKED_DUPLICATE_AMBIGUITY"
    return out

def main():
    print("="*78); print("M99 R7.3.0 R2.4.4 REGISTRY BASE URL + LIVE PRODUCT 2041 READBACK")
    print("GET ONLY / WRITE FALSE"); print("="*78)
    r=readback()
    print("Base URL source:",r.get("base_url_source"))
    print("M99EU_API_KEY:","PRESENT" if r.get("api_key_present") else "NOT_PRESENT")
    print("\n[m99.eu]",r["decision"])
    for k in ("product_get_http_status","product_id","reference","active","visibility",
              "id_category_default","id_tax_rules_group","cache_default_attribute",
              "duplicate_lookup_http_status","exact_reference_hits"):
        if k in r: print(" ",k,":",r[k])
    print(" CREATE_ALLOWED: FALSE"); print(" WRITE_ALLOWED: FALSE")
    out=Path.home()/"Desktop"/"M99_R730_R244_LIVE_PRODUCT2041_READBACK.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"version":"R7.3.0-R2.4.4","result":r},ensure_ascii=False,indent=2),encoding="utf-8")
    print("Report:",out)
    if r["decision"]=="UPDATE_EXISTING":
        print("[PASS] Product 2041 == M99 100018 and duplicate lookup is unique.")
        print("[PASS] READY TO BUILD R2.5 CONTROLLED HIDDEN UPDATE.")
        return 0
    print("[BLOCKED] Identity/readback gate not proven; NO WRITE.")
    return 10
if __name__=="__main__": raise SystemExit(main())
