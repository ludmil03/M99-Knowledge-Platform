from __future__ import annotations
import base64, json, requests, xml.etree.ElementTree as ET
from urllib.parse import urljoin

UA={"User-Agent":"M99-Knowledge-Platform/0.6.7.4.5"}

def ps_get(site,key,path,params=None):
    url=f"https://{site}/api/{path.lstrip('/')}"
    r=requests.get(url,params=params or {},auth=(key,""),headers=UA,timeout=30)
    return r

def prestashop_probe(site,key,target_ref):
    out={"site":site,"family":"prestashop_webservice","ready":False,"checks":{}}
    r=ps_get(site,key,"")
    out["checks"]["api_root"]={"status":r.status_code,"ok":r.ok}
    if not r.ok:
        out["error"]=f"API root HTTP {r.status_code}"
        return out
    r=ps_get(site,key,"languages",{"display":"full"})
    out["checks"]["languages_http"]={"status":r.status_code,"ok":r.ok}
    langs={}
    if r.ok:
        try:
            root=ET.fromstring(r.content)
            for x in root.findall(".//language"):
                lid=x.findtext("id"); iso=(x.findtext("iso_code") or "").lower()
                active=x.findtext("active")
                if lid and iso: langs[iso]={"id":lid,"active":active}
        except Exception as e:
            out["checks"]["languages_parse"]={"ok":False,"error":str(e)}
    out["languages_discovered"]=langs
    r=ps_get(site,key,"categories",{"display":"[id,name,active]","limit":"100"})
    out["checks"]["categories"]={"status":r.status_code,"ok":r.ok}
    r=ps_get(site,key,"products",{"filter[reference]":f"[{target_ref}]","display":"[id,reference,active,name]"})
    out["checks"]["target_lookup"]={"status":r.status_code,"ok":r.ok}
    existing=[]
    if r.ok:
        try:
            rr=ET.fromstring(r.content)
            for p in rr.findall(".//product"):
                existing.append({"id":p.findtext("id"),"reference":p.findtext("reference"),"active":p.findtext("active")})
        except Exception: pass
    out["target_existing"]=existing
    r=ps_get(site,key,"products",{"schema":"blank"})
    out["checks"]["product_blank_schema"]={"status":r.status_code,"ok":r.ok}
    out["write_capability_inferred"]=bool(r.ok)  # schema accessible; NO write request is sent
    out["ready"]=all(v.get("ok") for k,v in out["checks"].items() if k in ("api_root","languages_http","categories","target_lookup","product_blank_schema"))
    return out

def wp_headers(user,password):
    token=base64.b64encode(f"{user}:{password}".encode()).decode()
    return {**UA,"Authorization":"Basic "+token}

def wordpress_probe(site,user,password,target_ref):
    out={"site":site,"family":"wordpress_rest","ready":False,"checks":{}}
    h=wp_headers(user,password)
    root=f"https://{site}/wp-json/"
    r=requests.get(root,headers=h,timeout=30)
    out["checks"]["rest_root"]={"status":r.status_code,"ok":r.ok}
    if not r.ok:
        out["error"]=f"REST root HTTP {r.status_code}"
        return out
    try:
        index=r.json()
        routes=index.get("routes",{})
    except Exception:
        routes={}
    candidates=[]
    for ep in ("/wp/v2/product","/wp/v2/products","/wc/v3/products"):
        if ep in routes: candidates.append(ep)
    out["product_routes_discovered"]=candidates
    # authenticated identity is a GET-only credential check
    r=requests.get(f"https://{site}/wp-json/wp/v2/users/me",headers=h,params={"context":"edit"},timeout=30)
    out["checks"]["authenticated_user"]={"status":r.status_code,"ok":r.ok}
    # discover languages/plugins without assuming a specific multilingual plugin
    namespaces=[]
    try: namespaces=index.get("namespaces",[])
    except Exception: pass
    out["namespaces"]=namespaces
    out["multilingual_hints"]=[n for n in namespaces if any(x in n.lower() for x in ("wpml","polylang","pll","translatepress"))]
    endpoint=None
    for ep in ("/wp/v2/product","/wp/v2/products"):
        if ep in routes:
            endpoint=ep; break
    if endpoint:
        r=requests.get(f"https://{site}/wp-json{endpoint}",headers=h,params={"search":target_ref,"per_page":20,"context":"edit"},timeout=30)
        out["checks"]["target_lookup"]={"status":r.status_code,"ok":r.ok}
        out["target_existing_count"]=len(r.json()) if r.ok and isinstance(r.json(),list) else None
    else:
        out["checks"]["target_lookup"]={"status":None,"ok":False,"reason":"No WP product post-type REST route discovered"}
    out["write_capability_inferred"]=out["checks"]["authenticated_user"]["ok"] and bool(endpoint)
    out["ready"]=out["checks"]["rest_root"]["ok"] and out["checks"]["authenticated_user"]["ok"] and out["checks"]["target_lookup"]["ok"]
    return out
