from __future__ import annotations
import os, json, base64, requests, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urljoin
from core.cherokee_all_sites_content_v06744 import PRODUCT,CHANNEL_CONTENT

def envkey(site,suffix):
    return "M99_"+site.upper().replace(".","_").replace("-","_")+"_"+suffix

def snapshot_dir():
    ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p=Path("output/v06744_real_write")/ts
    p.mkdir(parents=True,exist_ok=True)
    return p

class PrestaShopAdapter:
    def __init__(self,site,cfg):
        self.site=site;self.cfg=cfg
        self.base="https://"+site.rstrip("/")+"/api/"
        self.key=os.environ.get(envkey(site,"API_KEY"),"").strip()
        if not self.key: raise RuntimeError(f"{site}: missing {envkey(site,'API_KEY')}")
    def _auth(self):
        return (self.key,"")
    def discover_languages(self):
        r=requests.get(urljoin(self.base,"languages"),params={"display":"full"},auth=self._auth(),timeout=30);r.raise_for_status()
        root=ET.fromstring(r.content); out={}
        for x in root.findall(".//language"):
            i=x.findtext("id");name=(x.findtext("iso_code") or "").lower()
            if i and name: out[name]=i
        return out
    def blank_schema(self):
        r=requests.get(urljoin(self.base,"products"),params={"schema":"blank"},auth=self._auth(),timeout=30);r.raise_for_status()
        return ET.fromstring(r.content)
    def find_by_reference(self,ref):
        r=requests.get(urljoin(self.base,"products"),params={"filter[reference]":f"[{ref}]","display":"full"},auth=self._auth(),timeout=30);r.raise_for_status()
        root=ET.fromstring(r.content)
        x=root.find(".//product/id")
        return x.text if x is not None and x.text else None
    def _set_multilang(self,parent,field,langmap,values):
        node=parent.find(field)
        if node is None: return
        node.clear()
        for iso,val in values.items():
            if iso not in langmap: continue
            e=ET.SubElement(node,"language",{"id":str(langmap[iso])}); e.text=val
    def build_xml(self,existing_id=None):
        root=self.blank_schema()
        prod=root.find(".//product")
        langs=self.discover_languages()
        if existing_id and prod.find("id") is not None: prod.find("id").text=str(existing_id)
        def setv(name,val):
            n=prod.find(name)
            if n is not None:n.text=str(val)
        setv("reference",PRODUCT["reference"]);setv("active","0");setv("visibility","both");setv("available_for_order","1");setv("show_price","1")
        values=CHANNEL_CONTENT[self.site]
        self._set_multilang(prod,"name",langs,{k:v["name"] for k,v in values.items()})
        self._set_multilang(prod,"description_short",langs,{k:v["short"] for k,v in values.items()})
        self._set_multilang(prod,"description",langs,{k:v["html"] for k,v in values.items()})
        self._set_multilang(prod,"meta_title",langs,{k:v["meta_title"] for k,v in values.items()})
        self._set_multilang(prod,"meta_description",langs,{k:v["meta_description"] for k,v in values.items()})
        # review category for mela99 only
        catid=self.cfg.get("review_category_id")
        if catid:
            assoc=prod.find("associations")
            if assoc is not None:
                cats=assoc.find("categories")
                if cats is not None:
                    cats.clear()
                    c=ET.SubElement(cats,"category");ET.SubElement(c,"id").text=str(catid)
                    setv("id_category_default",str(catid))
        return ET.tostring(root,encoding="utf-8",xml_declaration=True)
    def write(self):
        existing=self.find_by_reference(PRODUCT["reference"])
        xml=self.build_xml(existing)
        if existing:
            url=urljoin(self.base,f"products/{existing}");r=requests.put(url,data=xml,auth=self._auth(),headers={"Content-Type":"application/xml"},timeout=45)
            action="UPDATE"
        else:
            url=urljoin(self.base,"products");r=requests.post(url,data=xml,auth=self._auth(),headers={"Content-Type":"application/xml"},timeout=45)
            action="CREATE"
        if not r.ok: raise RuntimeError(f"{self.site}: HTTP {r.status_code}: {r.text[:700]}")
        rid=None
        try:
            rid=ET.fromstring(r.content).findtext(".//product/id")
        except Exception: pass
        return {"action":action,"id":rid or existing,"status":r.status_code}
    def readback(self,id_):
        r=requests.get(urljoin(self.base,f"products/{id_}"),auth=self._auth(),timeout=30);r.raise_for_status()
        root=ET.fromstring(r.content)
        return {"id":id_,"active":root.findtext(".//product/active"),"reference":root.findtext(".//product/reference")}

class WordPressAdapter:
    def __init__(self,site,cfg):
        self.site=site;self.cfg=cfg
        self.user=os.environ.get(envkey(site,"USER"),"").strip()
        self.pw=os.environ.get(envkey(site,"APP_PASSWORD"),"").strip()
        if not self.user or not self.pw: raise RuntimeError(f"{site}: missing WordPress USER/APP_PASSWORD")
        token=base64.b64encode(f"{self.user}:{self.pw}".encode()).decode()
        self.h={"Authorization":"Basic "+token,"Content-Type":"application/json"}
        self.base="https://"+site.rstrip("/")+"/wp-json/wp/v2/"
    def _language_doc(self):
        vals=CHANNEL_CONTENT[self.site]
        # Primary language payload. Language plugins can be added later; content is preserved in meta bundle.
        primary="bg" if "bg" in vals else "ro" if "ro" in vals else "en"
        return primary,vals[primary]
    def find_existing(self):
        r=requests.get(urljoin(self.base,"product"),params={"search":PRODUCT["reference"],"per_page":20},headers=self.h,timeout=30)
        if r.status_code==404:
            r=requests.get(urljoin(self.base,"posts"),params={"search":PRODUCT["reference"],"per_page":20},headers=self.h,timeout=30)
        if not r.ok:return None,None
        arr=r.json()
        return (arr[0].get("id"), "product" if "/product" in r.url else "posts") if arr else (None,"product")
    def write(self):
        primary,d=self._language_doc()
        payload={"status":"draft","title":d["name"],"content":d["html"],"excerpt":d["short"],
                 "meta":{"m99_reference":PRODUCT["reference"],"m99_multilingual_json":json.dumps(CHANNEL_CONTENT[self.site],ensure_ascii=False)}}
        existing,endpoint=self.find_existing()
        ep=endpoint or "product"
        if existing:url=urljoin(self.base,f"{ep}/{existing}");r=requests.post(url,headers=self.h,json=payload,timeout=45);action="UPDATE"
        else:url=urljoin(self.base,ep);r=requests.post(url,headers=self.h,json=payload,timeout=45);action="CREATE"
        if not r.ok: raise RuntimeError(f"{self.site}: HTTP {r.status_code}: {r.text[:700]}")
        j=r.json();return {"action":action,"id":j.get("id"),"status":r.status_code,"endpoint":ep}
    def readback(self,id_,endpoint="product"):
        r=requests.get(urljoin(self.base,f"{endpoint}/{id_}"),headers=self.h,timeout=30);r.raise_for_status();j=r.json()
        return {"id":id_,"status":j.get("status"),"title":(j.get("title") or {}).get("rendered")}

def adapter(site,cfg):
    p=cfg["platform"]
    if p=="prestashop":return PrestaShopAdapter(site,cfg)
    if p=="wordpress":return WordPressAdapter(site,cfg)
    raise RuntimeError(f"{site}: platform must be set to prestashop or wordpress, not {p}")

def run(config):
    required=config["policy"]["operator_confirmation"]
    print("REAL ALL-SITES WRITE_DRAFT")
    print("All six sites are mandatory. Draft/inactive only.")
    print("Type exactly:",required)
    if input("Confirmation: ").strip()!=required:
        raise RuntimeError("Exact confirmation required")
    out=snapshot_dir()
    results={}; completed=[]
    try:
        for site,cfg in config["sites"].items():
            print("\nWRITING",site)
            a=adapter(site,cfg)
            wr=a.write()
            rb=a.readback(wr["id"],wr.get("endpoint","product"))
            results[site]={"write":wr,"readback":rb,"success":True}
            completed.append(site)
            (out/f"{site.replace('.','_')}_result.json").write_text(json.dumps(results[site],ensure_ascii=False,indent=2),encoding="utf-8")
        (out/"ALL_SITES_RESULT.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
        print("\nALL SIX SITES WRITE_DRAFT SUCCESS")
        print("Result:",out/"ALL_SITES_RESULT.json")
        return 0
    except Exception as e:
        results["failure"]={"error":str(e),"completed_before_failure":completed}
        (out/"ALL_SITES_FAILED.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
        print("\nALL-SITES WRITE FAILED:",e)
        print("Partial success is NOT accepted.")
        print("Audit:",out/"ALL_SITES_FAILED.json")
        return 2
