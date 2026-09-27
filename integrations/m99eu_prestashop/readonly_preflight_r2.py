from __future__ import annotations
from dataclasses import dataclass,asdict
import base64,http.client,ssl,xml.etree.ElementTree as ET
from urllib.parse import urlencode,urlparse

class ReadOnlyViolation(RuntimeError): pass
class PreflightViolation(RuntimeError): pass

@dataclass(frozen=True)
class Language:
 id:str
 iso_code:str

class OneShotBasicGetTransport:
 """Fresh HTTPS connection per request; GET only; no automatic retry."""
 def __init__(self,base_url,api_key,timeout=20):
  p=urlparse(base_url)
  if p.scheme!="https" or (p.hostname or "").lower() not in {"m99.eu","www.m99.eu"}:
   raise ReadOnlyViolation("m99.eu HTTPS only")
  if not api_key: raise ReadOnlyViolation("API key missing")
  self.host=p.hostname; self.api_key=api_key; self.timeout=timeout; self.calls=[]
 def get(self,path,params=None):
  if not path.startswith("/api"): raise ReadOnlyViolation("API path must start /api")
  query=urlencode(params or {},doseq=True,safe="[],")
  target=path+("?" + query if query else "")
  token=base64.b64encode((self.api_key+":").encode()).decode()
  headers={"Accept":"application/xml","Authorization":"Basic "+token,
           "User-Agent":"M99-Knowledge-Platform-ReadOnly-Preflight/2.0","Connection":"close"}
  conn=http.client.HTTPSConnection(self.host,443,timeout=self.timeout,context=ssl.create_default_context())
  self.calls.append(("GET",path))
  try:
   conn.request("GET",target,headers=headers)
   r=conn.getresponse(); body=r.read(2_000_000)
   if r.status<200 or r.status>=300: raise PreflightViolation(f"HTTP {r.status} for {path}")
   return body.decode("utf-8-sig",errors="strict")
  finally:
   conn.close()

def permissions(xml):
 root=ET.fromstring(xml); p=root.find(".//api/products")
 if p is None: raise PreflightViolation("products resource absent")
 out={k:p.attrib.get(k)=="true" for k in ("get","post","put","delete")}
 if not out["get"]: raise PreflightViolation("products GET permission absent")
 return out

def languages(xml):
 root=ET.fromstring(xml); out=[]
 for n in root.findall(".//language"):
  i=(n.findtext("id") or "").strip(); iso=(n.findtext("iso_code") or "").strip().lower()
  active=(n.findtext("active") or "1").strip()=="1"
  if i and iso and active:out.append(Language(i,iso))
 if not out:raise PreflightViolation("no active languages")
 ids=[x.id for x in out];isos=[x.iso_code for x in out]
 if len(ids)!=len(set(ids)) or len(isos)!=len(set(isos)):raise PreflightViolation("duplicate language id/iso")
 return out

def required_language_map(items):
 m={x.iso_code:x.id for x in items}; missing=[x for x in ("en","bg","ru") if x not in m]
 if missing:raise PreflightViolation("missing active languages: "+",".join(missing))
 return {x:m[x] for x in ("en","bg","ru")}

def category(xml,expected):
 root=ET.fromstring(xml); c=root.find(".//category")
 if c is None:raise PreflightViolation("test category absent")
 got=(c.findtext("id") or "").strip()
 if got!=str(expected):raise PreflightViolation("test category id mismatch")
 active=(c.findtext("active") or "").strip()
 name_nodes=c.findall("name/language")
 return {"id":got,"active":active,"localized_names":len(name_nodes)}

def blank_schema(xml):
 root=ET.fromstring(xml);p=root.find(".//product")
 if p is None:raise PreflightViolation("blank product schema absent")
 return {"product_node":True,"field_count":len(list(p))}

def run_preflight(cfg,transport):
 root=transport.get("/api")
 perms=permissions(root)
 lx=transport.get("/api/languages",{"display":"[id,iso_code,active]","filter[active]":"1"})
 langs=languages(lx); langmap=required_language_map(langs)
 cx=transport.get(f"/api/categories/{int(cfg.test_category_id)}")
 cat=category(cx,cfg.test_category_id)
 bx=transport.get("/api/products",{"schema":"blank"})
 schema=blank_schema(bx)
 if any(m!="GET" for m,_ in transport.calls):raise ReadOnlyViolation("non-GET detected")
 return {"api":"AUTHENTICATED_HTTP_OK","credential":"PRESENT_NOT_PRINTED",
 "languages":[asdict(x) for x in langs],"required_language_map":langmap,
 "products_permissions":perms,"test_category":cat,"blank_product_schema":schema,
 "requests":[{"method":m,"path":p} for m,p in transport.calls],
 "transport":"ONE_SHOT_FRESH_HTTPS_CONNECTION_PER_GET","retry":False,
 "write_performed":False,"write_allowed":False}
