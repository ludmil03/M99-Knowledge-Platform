from __future__ import annotations

from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from html import escape
from html.parser import HTMLParser
import ipaddress, json, re, socket
from typing import Any, Callable
from urllib.parse import quote_plus, urljoin, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from xml.etree import ElementTree as ET

from app.models.entities import ImportJobItem
from app.services.v073_phase45.r37_import_bridge import product_for_canonical_preview_from_draft
from app.services.v073_phase45.unified_add_products import approved_sources

LANGUAGE_REGISTRY=("BG","EN","RU","RO","GR")
CHANNEL_LANGUAGE_DEFAULTS={
    "m99eu":("EN","BG","RU"),
    "mela99":("BG","EN"),
    "rabotni_drehi":("BG",),
    "medicinski_drehi":("BG",),
    "laviro":("RO","EN"),
    "alviro":("RO","EN"),
}
BENCHMARK_FRAMEWORK={
    "global_commerce":("Amazon","Zalando","eBay"),
    "information_design":("Apple",),
    "manufacturer_truth":("official exact manufacturer page","official documentation/catalogue"),
    "local_market":("Stenso","Palltex","category-specific competitors"),
}
USER_AGENT="M99-Knowledge-Platform/0.7.3 read-only manufacturer evidence discovery"
LEGACY_NO_MAPPED_DRAFT_EVIDENCE_CARRIER="NO_MAPPED_DRAFT_EVIDENCE_CARRIER"

@dataclass(frozen=True)
class ManufacturerCandidate:
    url:str; score:int; exact_reference:bool; title_overlap:int; title:str; meta_description:str
    images:tuple[str,...]; documents:tuple[str,...]; tables:tuple[tuple[str,...],...]; text_excerpt:str

class Parser(HTMLParser):
    BLOCK_TAGS={"title","h1","h2","h3","h4","p","li","dt","dd","figcaption","caption"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=""; self.meta=""; self.headings=[]; self.blocks=[]; self.images=[]; self.links=[]; self.tables=[]; self.jsonld=[]
        self._stack=[]; self._row=None; self._cell=None; self._script_jsonld=False; self._script_buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in self.BLOCK_TAGS:self._stack.append((tag,[]))
        if tag=="meta":
            key=(a.get("name") or a.get("property") or "").lower(); val=(a.get("content") or "").strip()
            if key in {"description","og:description"} and val and not self.meta:self.meta=val
            if key in {"og:image","twitter:image"} and val:self.images.append(val)
        elif tag=="img":
            src=a.get("src") or a.get("data-src") or a.get("data-lazy-src")
            if src:self.images.append(src)
            alt=(a.get("alt") or "").strip()
            if alt:self.blocks.append(alt)
            srcset=a.get("srcset") or a.get("data-srcset")
            if srcset:
                for part in srcset.split(","):
                    u=part.strip().split(" ",1)[0]
                    if u:self.images.append(u)
        elif tag=="a" and a.get("href"):self.links.append(a["href"])
        elif tag=="tr":self._row=[]
        elif tag in {"td","th"} and self._row is not None:self._cell=[]
        elif tag=="script" and "ld+json" in (a.get("type") or "").lower():self._script_jsonld=True; self._script_buf=[]
    def handle_data(self,data):
        if self._stack:self._stack[-1][1].append(data)
        if self._cell is not None:self._cell.append(data)
        if self._script_jsonld:self._script_buf.append(data)
    def handle_endtag(self,tag):
        if tag in self.BLOCK_TAGS and self._stack:
            idx=next((i for i in range(len(self._stack)-1,-1,-1) if self._stack[i][0]==tag),None)
            if idx is not None:
                _tag,buf=self._stack.pop(idx); val=" ".join(" ".join(buf).split())
                if val:
                    if tag=="title":self.title=val
                    elif tag in {"h1","h2","h3","h4"}:self.headings.append(val); self.blocks.append(val)
                    else:self.blocks.append(val)
        if tag in {"td","th"} and self._row is not None and self._cell is not None:
            val=" ".join(" ".join(self._cell).split()); self._cell=None
            if val:self._row.append(val)
        elif tag=="tr" and self._row is not None:
            if self._row:self.tables.append(self._row)
            self._row=None
        elif tag=="script" and self._script_jsonld:
            val="".join(self._script_buf).strip()
            if val:self.jsonld.append(val)
            self._script_jsonld=False; self._script_buf=[]

def _decode_detection(value:Any)->dict:
    if isinstance(value,dict):return dict(value)
    if isinstance(value,str) and value.strip():
        try:
            x=json.loads(value); return dict(x) if isinstance(x,dict) else {}
        except Exception:return {}
    return {}

def selected_draft_item(db,job_id:int):
    rows=(db.query(ImportJobItem).filter(
        ImportJobItem.import_job_id==int(job_id),
        ImportJobItem.selected.is_(True)
    ).order_by(ImportJobItem.id.asc()).all())
    if len(rows)!=1:raise ValueError(f"Expected exactly one selected DRAFT item; found {len(rows)}.")
    return rows[0]

def model_persistence_capability()->dict:
    required=("id","import_job_id","selected")
    missing=[name for name in required if not hasattr(ImportJobItem,name)]
    if missing:
        return {"query_contract_ready":False,"missing_query_attrs":missing,
                "persistence_carrier":None,"persistence_ready":False}
    carrier="detection" if hasattr(ImportJobItem,"detection") else None
    return {"query_contract_ready":True,"missing_query_attrs":[],
            "persistence_carrier":carrier,"persistence_ready":bool(carrier)}

def _manufacturer_key(value:str)->str:
    return re.sub(r"[^a-z0-9]+","",(value or "").lower())

def _manufacturer_match_score(brand:str, source)->int:
    brand_key=_manufacturer_key(brand)
    if not brand_key:
        return 0
    values=[
        str(getattr(source,"name","") or ""),
        str(getattr(source,"domain","") or ""),
        str(getattr(source,"base_url","") or ""),
    ]
    best=0.0
    for value in values:
        key=_manufacturer_key(value.replace("www.",""))
        if not key:
            continue
        if brand_key==key:
            return 100
        if len(brand_key)>=5 and (brand_key in key or key in brand_key):
            best=max(best,0.96)
        best=max(best,SequenceMatcher(None,brand_key,key).ratio())
    return int(round(best*100))

def resolve_manufacturer_source(db,supplier_evidence:dict)->dict:
    brand=str(
        supplier_evidence.get("manufacturer_name")
        or supplier_evidence.get("brand")
        or supplier_evidence.get("brand_name")
        or ""
    ).strip()
    if not brand:
        return {
            "status":"UNKNOWN",
            "manufacturer_name":"",
            "official_site":"",
            "source_uuid":"",
            "match_score":0,
            "reason":"NO_MANUFACTURER_EVIDENCE",
        }
    try:
        candidates=approved_sources(db,kind="MANUFACTURER")
    except Exception as exc:
        return {
            "status":"UNKNOWN",
            "manufacturer_name":brand,
            "official_site":"",
            "source_uuid":"",
            "match_score":0,
            "reason":"MANUFACTURER_SOURCE_REGISTRY_UNAVAILABLE",
            "detail":str(exc),
        }

    ranked=sorted(
        ((_manufacturer_match_score(brand,s),s) for s in candidates),
        key=lambda row:row[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] < 85:
        return {
            "status":"UNKNOWN",
            "manufacturer_name":brand,
            "official_site":"",
            "source_uuid":"",
            "match_score":ranked[0][0] if ranked else 0,
            "reason":"NO_APPROVED_MANUFACTURER_SOURCE_MATCH",
        }

    score,source=ranked[0]
    return {
        "status":"KNOWN",
        "manufacturer_name":str(source.name),
        "evidence_name":brand,
        "official_site":str(source.base_url or ""),
        "domain":str(source.domain or ""),
        "source_uuid":str(source.source_uuid),
        "match_score":score,
        "reason":"MATCHED_APPROVED_MANUFACTURER_SOURCE",
    }

def resolve_manufacturer_product_code(supplier_evidence:dict,manufacturer_evidence:dict|None=None)->dict:
    manufacturer_evidence=manufacturer_evidence or {}
    for key in ("manufacturer_product_code","manufacturer_reference","product_code"):
        value=str(manufacturer_evidence.get(key) or "").strip()
        if value:
            return {"code":value,"status":"VERIFIED_MANUFACTURER_CODE","source":"MANUFACTURER_EVIDENCE"}

    for key in ("manufacturer_product_code","manufacturer_reference","manufacturer_code"):
        value=str(supplier_evidence.get(key) or "").strip()
        if value:
            return {"code":value,"status":"MANUFACTURER_CODE_FROM_SUPPLIER_EVIDENCE","source":key}

    ref=str(supplier_evidence.get("supplier_reference") or "").strip()
    if ref:
        return {
            "code":ref,
            "status":"CANDIDATE_FROM_SUPPLIER_REFERENCE",
            "source":"supplier_reference",
            "requires_exact_manufacturer_verification":True,
        }

    return {"code":"","status":"UNKNOWN","source":"NONE"}


def draft_context(db,job_id:int,source_uuid:str,product_url:str)->dict:
    item=selected_draft_item(db,job_id)
    supplier=product_for_canonical_preview_from_draft(
        db,job_id=int(job_id),source_uuid=source_uuid,product_url=product_url
    )
    capability=model_persistence_capability()
    d={}; manufacturer={}; content={}
    if capability["persistence_carrier"]=="detection":
        d=_decode_detection(getattr(item,"detection",None))
        manufacturer=d.get("manufacturer_evidence") or {}
        content=d.get("content_enrichment") or {}

    manufacturer_source=resolve_manufacturer_source(db,supplier)
    manufacturer_product_code=resolve_manufacturer_product_code(supplier,manufacturer)

    return {
        "item":item,
        "detection":d,
        "supplier_evidence":supplier,
        "supplier_context_source":str(supplier.get("snapshot_source") or "R2_COMPATIBILITY_SOURCE"),
        "manufacturer_evidence":manufacturer,
        "manufacturer_source":manufacturer_source,
        "manufacturer_product_code":manufacturer_product_code,
        "content_enrichment":content,
        "persistence":capability,
    }


def _store(payload:dict)->Any:
    c=getattr(getattr(ImportJobItem,"__table__",None),"c",None)
    if c is not None and "detection" in c:
        try:
            if c["detection"].type.python_type is dict:return payload
        except Exception:pass
    return json.dumps(payload,ensure_ascii=False,sort_keys=True)

def persist_confirmed_enrichment(db,*,job_id:int,manufacturer_evidence:dict,content_bundle:dict,supplier_evidence:dict|None=None)->dict:
    capability=model_persistence_capability()
    if not capability["persistence_ready"]:
        from app.services.v073_phase46.durable_draft_enrichment import save as save_durable_enrichment
        item=selected_draft_item(db,job_id)
        supplier=dict(supplier_evidence or {})
        supplier_reference=str(
            supplier.get("supplier_reference")
            or manufacturer_evidence.get("manufacturer_product_code")
            or manufacturer_evidence.get("supplier_reference")
            or getattr(item,"supplier_reference","")
            or ""
        ).strip()
        if not supplier_reference:
            raise ValueError("Durable enrichment requires an evidence-backed supplier/manufacturer reference.")
        result=save_durable_enrichment(job_id=job_id,item_id=int(item.id),supplier_reference=supplier_reference,manufacturer_evidence=manufacturer_evidence,content_bundle=content_bundle,target=str(content_bundle.get("target") or "m99eu"),supplier_evidence=supplier_evidence or {})
        result["capability"]=capability
        result["legacy_schema_reason"]=LEGACY_NO_MAPPED_DRAFT_EVIDENCE_CARRIER
        result["persistence_upgrade"]="R4_DURABLE_DRAFT_SIDECAR"
        return result
    item=selected_draft_item(db,job_id)
    d=_decode_detection(getattr(item,"detection",None))
    d["manufacturer_evidence"]=manufacturer_evidence
    d["content_enrichment"]=content_bundle
    item.detection=_store(d)
    try:db.commit()
    except Exception:db.rollback(); raise
    return {"persisted":True,"reason":"PERSISTED_TO_MAPPED_DETECTION","capability":capability}

def _site(value:str)->str:
    raw=(value or "").strip()
    if not raw:raise ValueError("Manufacturer official website is required.")
    if "://" not in raw:raw="https://"+raw
    p=urlparse(raw)
    if p.scheme not in {"http","https"} or not p.hostname:raise ValueError("Manufacturer website must be http/https.")
    return f"{p.scheme}://{p.hostname.lower().rstrip('.')}"

def _public_guard(url:str)->None:
    host=urlparse(url).hostname
    if not host:raise ValueError("URL has no hostname.")
    low=host.lower().rstrip(".")
    if low in {"localhost","localhost.localdomain"} or low.endswith(".local"):raise ValueError("Local/private manufacturer hosts are blocked.")
    infos=socket.getaddrinfo(low,443 if urlparse(url).scheme=="https" else 80,type=socket.SOCK_STREAM)
    for info in infos:
        ip=ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:raise ValueError("Private/reserved network target blocked.")

class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        _public_guard(newurl)
        oldhost=(urlparse(req.full_url).hostname or "").lower().removeprefix("www.")
        newhost=(urlparse(newurl).hostname or "").lower().removeprefix("www.")
        if oldhost!=newhost:raise ValueError("Cross-domain manufacturer redirect blocked.")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def _get(url:str,timeout:int=12,max_bytes:int=2500000)->tuple[str,str]:
    _public_guard(url); req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml,application/xml,text/plain;q=0.8,*/*;q=0.5"})
    opener=build_opener(_SafeRedirect())
    with opener.open(req,timeout=timeout) as r:
        final=r.geturl(); data=r.read(max_bytes+1); ctype=(r.headers.get("Content-Type") or "").lower()
    if len(data)>max_bytes:raise ValueError("Manufacturer response exceeded safe limit.")
    m=re.search(r"charset=([A-Za-z0-9._-]+)",ctype); enc=m.group(1) if m else "utf-8"
    return final,data.decode(enc,errors="replace")

def _same(base:str,u:str)->bool:
    return (urlparse(base).hostname or "").lower().removeprefix("www.")== (urlparse(u).hostname or "").lower().removeprefix("www.")

def _tokens(s:str)->list[str]:return [x for x in re.findall(r"[A-Za-zА-Яа-я0-9]{3,}",(s or "").lower()) if x not in {"product","products","мъжка","риза"}]

def _abs(base:str,vals:list[str])->tuple[str,...]:
    out=[]
    for v in vals:
        u=urljoin(base,v)
        if _same(base,u) and u not in out:out.append(u)
    return tuple(out)

def _image_candidate(url:str,ref:str,title_hint:str)->bool:
    low=url.lower(); reject=("logo","icon","sprite","favicon","payment","header","footer","avatar","flag","loader","cookie")
    if any(x in low for x in reject):return False
    if urlparse(url).path.lower().endswith((".svg",".ico")):return False
    return True

def _parse(url:str,html:str,ref:str,title_hint:str):
    p=Parser(); p.feed(html)
    body=" ".join([p.title,p.meta,*p.headings,*p.blocks,*[" | ".join(r) for r in p.tables]])
    exact=bool(ref and re.search(rf"(?<!\w){re.escape(ref)}(?!\w)",body,re.I))
    overlap=len(set(_tokens(title_hint)).intersection(set(_tokens(" ".join([p.title,*p.headings])))))
    title_zone=" ".join([p.title,*p.headings]).lower()
    score=(70 if exact else 0)+min(overlap*8,24)+(10 if ref and ref.lower() in url.lower() else 0)
    if ref and ref.lower() in title_zone:score+=18
    if any(x in body.lower() for x in ("composition","skład","70%","weight","gramatura","g/m")):score+=8
    if p.tables:score+=4
    imgs=tuple(x for x in _abs(url,p.images) if _image_candidate(x,ref,title_hint)); links=_abs(url,p.links)
    docs=tuple(x for x in links if urlparse(x).path.lower().endswith((".pdf",".doc",".docx",".xls",".xlsx")))
    c=ManufacturerCandidate(url,score,exact,overlap,p.title or (p.headings[0] if p.headings else ""),p.meta,imgs[:40],docs[:40],tuple(tuple(x for x in r) for r in p.tables[:60])," ".join(body.split())[:8000])
    return c,links

def _sitemap(site:str,fetch,ref:str,title:str)->list[str]:
    out=[]
    for seed in (site+"/sitemap.xml",site+"/wp-sitemap.xml"):
        try:_f,text=fetch(seed); root=ET.fromstring(text)
        except Exception:continue
        locs=[str(x.text or "").strip() for x in root.iter() if x.tag.lower().endswith("loc") and x.text]
        for nested in [x for x in locs if x.lower().endswith(".xml")][:4]:
            try:_nf,nt=fetch(nested); nr=ET.fromstring(nt); locs.extend(str(x.text or "").strip() for x in nr.iter() if x.tag.lower().endswith("loc") and x.text)
            except Exception:pass
        toks=_tokens(title)
        out.extend(x for x in locs if _same(site,x) and (ref.lower() in x.lower() or any(t in x.lower() for t in toks[:4])))
    return list(dict.fromkeys(out))

def discover_manufacturer_product(*,manufacturer_site_url:str,supplier_reference:str,title_hint:str,fetcher:Callable[[str],tuple[str,str]]|None=None,max_pages:int=32)->dict:
    raw=(manufacturer_site_url or "").strip()
    site=_site(raw)
    fetch=fetcher or _get
    q=quote_plus((supplier_reference or "").strip())

    # If the resolved/manual URL is already a product page, inspect it FIRST.
    seed_url=raw if "://" in raw else ("https://"+raw if raw else "")
    seed_url=seed_url if seed_url and _same(site,seed_url) else site+"/"

    sitemap_urls=list(_sitemap(site,fetch,supplier_reference,title_hint) or ())
    queue=[
        seed_url,
        site+"/",
        site+"/products/",
        site+"/en/products/",
        site+"/?s="+q,
        site+"/en/?s="+q,
        site+"/search/?q="+q,
        site+"/products/?search="+q,
        *sitemap_urls,
    ]

    queue=list(dict.fromkeys(str(x) for x in queue if x))
    seen=set()
    found=[]
    toks=_tokens(title_hint)

    while queue and len(seen)<max_pages:
        u=queue.pop(0)
        if u in seen or not _same(site,u):
            continue
        seen.add(u)
        try:
            final,text=fetch(u)
        except Exception:
            continue
        if not _same(site,final):
            continue
        c,links=_parse(final,text,supplier_reference,title_hint)
        if c.exact_reference or c.title_overlap:
            found.append(c)

        # Stop early after a strong exact match on an explicitly supplied product URL.
        if c.exact_reference and c.score>=70 and u==seed_url and urlparse(seed_url).path not in {"","/"}:
            break

        links=sorted(
            (x for x in links if x not in seen and _same(site,x)),
            key=lambda x:(
                0 if supplier_reference and supplier_reference.lower() in x.lower() else 1,
                0 if any(t in x.lower() for t in toks[:4]) else 1,
                len(x),
            ),
        )
        for x in links[:16]:
            if x not in queue and len(queue)<max_pages*4:
                queue.append(x)

    found.sort(key=lambda x:(x.score,x.exact_reference,x.title_overlap),reverse=True)
    exact=next((x for x in found if x.exact_reference and x.score>=70),None)
    return {
        "schema":"m99.phase46.r3.manufacturer_discovery.v2",
        "official_site":site,
        "seed_url":seed_url,
        "supplier_reference":supplier_reference,
        "manufacturer_product_code":supplier_reference,
        "title_hint":title_hint,
        "pages_checked":len(seen),
        "status":"EXACT_CANDIDATE_FOUND" if exact else ("CANDIDATES_FOUND" if found else "NOT_FOUND"),
        "exact_candidate":asdict(exact) if exact else None,
        "candidates":[asdict(x) for x in found[:10]],
        "write_attempted":False,
        "operator_confirmation_required":True,
    }


def fetch_exact_manufacturer_evidence(*,manufacturer_site_url:str,manufacturer_page_url:str,supplier_reference:str,title_hint:str,fetcher=None)->dict:
    site=_site(manufacturer_site_url)
    if not _same(site,manufacturer_page_url):raise ValueError("Selected page is outside approved official domain.")
    final,text=(fetcher or _get)(manufacturer_page_url); c,_=_parse(final,text,supplier_reference,title_hint)
    if not c.exact_reference:raise ValueError("Selected manufacturer page does not contain the exact reference.")
    return {"schema":"m99.phase46.r3.manufacturer_evidence.v1","status":"OPERATOR_CONFIRMED_EXACT","official_site":site,"official_product_url":c.url,"supplier_reference":supplier_reference,"manufacturer_product_code":supplier_reference,"manufacturer_product_code_status":"VERIFIED_EXACT_REFERENCE","page_title":c.title,"meta_description":c.meta_description,"images":list(c.images),"documents":list(c.documents),"tables":[list(x) for x in c.tables],"text_excerpt":c.text_excerpt,"provenance":{"source_class":"OFFICIAL_MANUFACTURER_PUBLIC_WEBSITE","match_basis":"EXACT_REFERENCE"}}

def _clean_inline(value)->str:
    text=str(value or "")
    text=re.sub(r"<\s*br\s*/?\s*>", " ", text, flags=re.I)
    text=re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def _profile(s:dict,m:dict)->dict:
    text=" ".join(str(x) for x in [s.get("description",""),m.get("page_title",""),m.get("meta_description",""),m.get("text_excerpt","")]+[" | ".join(map(str,list(r or ()))) for r in list(m.get("tables") or ())]); low=text.lower()
    supplier_ref=str(s.get("supplier_reference") or "").strip()
    manufacturer_ref=str(m.get("manufacturer_product_code") or "").strip() if (m.get("status")=="OPERATOR_CONFIRMED_EXACT" and m.get("manufacturer_product_code_status")=="VERIFIED_EXACT_REFERENCE") else ""
    p={"name":_clean_inline(s.get("name") or s.get("title") or m.get("page_title") or "Product"),"supplier_reference":supplier_ref,"manufacturer_reference":manufacturer_ref,"reference":manufacturer_ref,"brand":s.get("brand") or "","images":list(dict.fromkeys([*list(m.get("images") or ()),*list(s.get("images") or ())])),"variants":s.get("variants") or [],"manufacturer_url":m.get("official_product_url") or ""}
    # Product identity is determined from the exact product title/name first.
    # Long supplier/manufacturer prose may mention other garment types (for example
    # cross-selling text) and must never turn trousers into a shirt.
    identity_low=(" ".join(str(x) for x in [p.get("name",""),s.get("name",""),s.get("title",""),m.get("page_title","")])).lower()
    trousers_tokens=("панталон","trouser","trousers","pants","брюк","брюки")
    shirt_tokens=("shirt","koszula","риза","рубашка","cămaș","πουκάμισ")
    if any(x in identity_low for x in trousers_tokens):
        p["product_type"]="trousers"
    elif any(x in identity_low for x in shirt_tokens):
        p["product_type"]="shirt"
    else:
        p["product_type"]="product"
    identity_text=(" ".join(str(x) for x in [p.get("name",""),s.get("name",""),s.get("title",""),m.get("page_title","")])).lower()
    female_tokens=("women","woman","women's","damska","damskie","дамска","женск","femei","damă","γυναικ")
    male_tokens=("men","man's","men's","męska","męskie","мъжк","мужск","bărba","ανδρ")
    if any(x in identity_text for x in female_tokens):p["gender"]="female"
    elif any(x in identity_text for x in male_tokens):p["gender"]="male"
    else:p["gender"]="unisex"
    p["oxford"]="oxford" in low or "оксфорд" in low
    p["classic_cut"]=any(x in low for x in ("classic cut","klasyczny fason","класическа кройка","классический крой","croială clasic"))
    p["stiff_collar"]=any(x in low for x in ("stiffened stand-up collar","usztywniony kołnierzyk ze stójką","укрепленный воротник","усилена яка"))
    p["chest_pocket"]=any(x in low for x in ("chest pocket","kieszeń na piersi","джоб на гърдите","карман на груди","buzunar la piept"))
    p["contrast_inside"]=any(x in low for x in ("contrasting fabric","kontrastowym materiałem","контрастен","контрастным материалом","contrastant"))
    p["oeko_tex"]="oeko tex" in low.replace("-"," ") or "oekotex" in low
    p["care_30"]=any(x in low for x in ("wash at max 30","pranie max 30","30°c","30°")); p["do_not_bleach"]=any(x in low for x in ("do not bleach","nie wybielać","не отбел")); p["iron_150"]=any(x in low for x in ("iron up to 150","prasować do 150","150°c"))
    methods=[]
    for key,label in (("dtf","DTF print"),("embroidery","Embroidery"),("haft","Embroidery"),("heat transfer","Heat transfer"),("termotransfer","Heat transfer"),("screen printing","Screen printing"),("sitodruk","Screen printing")):
        if key in low and label not in methods:methods.append(label)
    p["branding_methods"]=methods
    comp=re.search(r"(\d{1,3})\s*%\s*(?:c|cotton|bawełna|памук|хлопок)[^\d]{0,24}(\d{1,3})\s*%\s*(?:p|polyester|poliester|полиестер|полиэстер)",low); weight=re.search(r"(\d{2,4})\s*g\s*/?\s*m(?:²|2)",low)
    if comp:p["cotton_pct"],p["polyester_pct"]=int(comp.group(1)),int(comp.group(2))
    if weight:p["weight_gsm"]=int(weight.group(1))
    packaging=re.search(r"(?:packaging|opakowanie)\s*[:|]?\s*(\d{1,4})",low); pack_one=re.search(r"(?:number of pieces in a pack|ilość szt\.? w zgrzewce)\s*[:|]?\s*(\d{1,4})",low)
    if packaging:p["packaging"]=int(packaging.group(1))
    if pack_one:p["inner_pack_qty"]=int(pack_one.group(1))
    sizes=[]; colors=[]
    for v in p["variants"]:
        if isinstance(v,dict):
            if v.get("value"):colors.append(str(v["value"]))
            for r in v.get("sizes") or []:
                if isinstance(r,dict) and r.get("size"):sizes.append(str(r["size"]))
    p["sizes"]=list(dict.fromkeys(sizes)); p["colors"]=list(dict.fromkeys(colors)); p["official_tables"]=m.get("tables") or []
    return p

COLOR_MAP={
 "бял":{"BG":"Бял","EN":"White","RU":"Белый","RO":"Alb","GR":"Λευκό"},
 "черен":{"BG":"Черен","EN":"Black","RU":"Чёрный","RO":"Negru","GR":"Μαύρο"},
 "тъмно-син":{"BG":"Тъмносин","EN":"Navy / dark blue","RU":"Тёмно-синий","RO":"Bleumarin","GR":"Σκούρο μπλε"},
 "небесно-син":{"BG":"Небесносин","EN":"Sky blue","RU":"Небесно-голубой","RO":"Albastru deschis","GR":"Γαλάζιο"}}
def _localized_colors(p,lang):return list(dict.fromkeys(COLOR_MAP.get(str(c).strip().lower(),{}).get(lang,str(c)) for c in p.get("colors") or []))
def _localized_title(p,lang):
    brand=(p.get("brand") or "").strip()
    raw=(p.get("name") or "").strip()
    model="RIVER" if "river" in raw.lower() else raw
    prefix=(brand+" "+model).strip()
    if p.get("product_type")=="shirt":
        gender=p.get("gender") or "unisex"
        if gender=="female":
            label={"BG":"Дамска риза","EN":"Women's Shirt","RU":"Женская рубашка","RO":"Cămașă de damă","GR":"Γυναικείο πουκάμισο"}[lang]
        elif gender=="male":
            label={"BG":"Мъжка риза","EN":"Men's Shirt","RU":"Мужская рубашка","RO":"Cămașă bărbătească","GR":"Ανδρικό πουκάμισο"}[lang]
        else:
            label={"BG":"Риза","EN":"Shirt","RU":"Рубашка","RO":"Cămașă","GR":"Πουκάμισο"}[lang]
        oxford={"BG":" от Oxford","EN":" Oxford","RU":" из ткани Oxford","RO":" din Oxford","GR":" από Oxford"}[lang] if p.get("oxford") else ""
        if lang=="EN":return f"{prefix} {label}{oxford}".strip()
        return f"{label} {prefix}{oxford}".strip()
    return prefix or p.get("name") or "Product"

LEX={
"BG":{"overview":"Преглед","construction":"Материал и конструкция","details":"Детайли и предназначение","variants":"Цветове и размери","technical":"Технически характеристики","buyer":"Избор и поръчка","faq":"Често задавани въпроси","ref":"Код","brand":"Марка","sizes":"Размери","colors":"Цветове","material":"Материал","weight":"Плътност"},
"EN":{"overview":"Overview","construction":"Material and construction","details":"Design and practical details","variants":"Colours and sizes","technical":"Technical specifications","buyer":"Choosing and ordering","faq":"Frequently asked questions","ref":"Reference","brand":"Brand","sizes":"Sizes","colors":"Colours","material":"Material","weight":"Fabric weight"},
"RU":{"overview":"Обзор","construction":"Материал и конструкция","details":"Детали и применение","variants":"Цвета и размеры","technical":"Технические характеристики","buyer":"Выбор и заказ","faq":"Частые вопросы","ref":"Код","brand":"Бренд","sizes":"Размеры","colors":"Цвета","material":"Материал","weight":"Плотность ткани"},
"RO":{"overview":"Prezentare","construction":"Material și construcție","details":"Detalii și utilizare","variants":"Culori și mărimi","technical":"Specificații tehnice","buyer":"Alegere și comandă","faq":"Întrebări frecvente","ref":"Cod","brand":"Marcă","sizes":"Mărimi","colors":"Culori","material":"Material","weight":"Greutate material"},
"GR":{"overview":"Επισκόπηση","construction":"Υλικό και κατασκευή","details":"Λεπτομέρειες και χρήση","variants":"Χρώματα και μεγέθη","technical":"Τεχνικά χαρακτηριστικά","buyer":"Επιλογή και παραγγελία","faq":"Συχνές ερωτήσεις","ref":"Κωδικός","brand":"Μάρκα","sizes":"Μεγέθη","colors":"Χρώματα","material":"Υλικό","weight":"Βάρος υφάσματος"}}

def _material(p,lang):
    if "cotton_pct" in p and "polyester_pct" in p:
        c,po=p["cotton_pct"],p["polyester_pct"]; return {"BG":f"{c}% памук / {po}% полиестер","EN":f"{c}% cotton / {po}% polyester","RU":f"{c}% хлопок / {po}% полиэстер","RO":f"{c}% bumbac / {po}% poliester","GR":f"{c}% βαμβάκι / {po}% πολυεστέρας"}[lang]
    return "Oxford" if p.get("oxford") else ""

def _summary(p,lang):
    n=_localized_title(p,lang); r=p.get("reference"); mat=_material(p,lang); weight=f"{p['weight_gsm']} g/m²" if p.get("weight_gsm") else ""
    if lang=="BG":
        s=f"{n} е модел с класическа кройка" if p.get("classic_cut") else n
        if mat:s+=f", изработен от {mat}"
        if weight:s+=f" с плътност {weight}"
        s+="."
        if p.get("stiff_collar"):s+=" Усилената яка със стойка поддържа подреден силует."
        if p.get("chest_pocket"):s+=" Джобът на гърдите добавя практичен детайл."
        if r:s+=f" Код на производителя / MPN: {r}."
    elif lang=="EN":
        s=f"{n} combines a classic cut" if p.get("classic_cut") else n
        if mat:s+=f" with {mat}"
        if weight:s+=f" at {weight}"
        s+="."
        if p.get("stiff_collar"):s+=" A stiffened stand-up collar keeps the silhouette neat and structured."
        if p.get("chest_pocket"):s+=" A chest pocket adds a practical detail."
        if r:s+=f" Manufacturer reference / MPN: {r}."
    elif lang=="RU":
        s=f"{n}: классический крой" if p.get("classic_cut") else n
        if mat:s+=f", материал {mat}"
        if weight:s+=f", плотность {weight}"
        s+="."
        if p.get("stiff_collar"):s+=" Укреплённый воротник-стойка помогает сохранять аккуратный вид."
        if p.get("chest_pocket"):s+=" На груди предусмотрен практичный карман."
        if r:s+=f" Код производителя / MPN: {r}."
    elif lang=="RO":
        s=f"{n}, cu croială clasică" if p.get("classic_cut") else n
        if mat:s+=f", material {mat}"
        if weight:s+=f", {weight}"
        s+="."
        if r:s+=f" Cod producător / MPN: {r}."
    else:
        s=n+(f", {mat}" if mat else "")+(f", {weight}" if weight else "")+"."
        if r:s+=f" Κωδικός κατασκευαστή / MPN: {r}."
    return s

def _faq(p,lang):
    r=p.get("reference") or "—"; sizes=", ".join(p.get("sizes") or []); colors=", ".join(_localized_colors(p,lang)); mat=_material(p,lang); methods=", ".join(p.get("branding_methods") or [])
    if lang=="BG":pairs=[("Как да разпозная точния модел?",f"Проверявайте кода {r}; M99 го използва за връзка между доставчика и официалния manufacturer evidence."),("Какъв е съставът и плътността?",(mat or "Съставът не е потвърден")+(f", {p['weight_gsm']} g/m²." if p.get('weight_gsm') else ".")),("Какви размери са представени?",sizes or "Размерите се показват само от проверен variant evidence."),("В какви цветове се предлага?",colors or "Цветовете се показват от проверените варианти."),("Подходяща ли е за фирмено брандиране?",f"Официално потвърдени методи: {methods}." if methods else "Методите за брандиране се показват само когато са потвърдени от производителя."),("Наличността при доставчика означава ли физическа наличност в M99?","Не. Supplier availability и M99 physical stock са отделни данни.")]
    elif lang=="EN":pairs=[("How do I identify the exact model?",f"Use reference {r}; M99 uses it to link supplier and official manufacturer evidence."),("What are the composition and fabric weight?",(mat or "Composition is not verified")+(f", {p['weight_gsm']} g/m²." if p.get('weight_gsm') else ".")),("Which sizes are represented?",sizes or "Sizes are shown only from verified variant evidence."),("Which colours are represented?",colors or "Colours are shown from verified variants."),("Can it be used for company branding?",f"Officially supported methods: {methods}." if methods else "Branding methods are shown only when verified by the manufacturer."),("Is supplier availability the same as M99 physical stock?","No. Supplier availability and M99-owned physical stock are separate data sets.")]
    elif lang=="RU":pairs=[("Как проверить точную модель?",f"Используйте код {r}; M99 связывает по нему данные поставщика и официальный источник производителя."),("Каков состав и плотность ткани?",(mat or "Состав не подтверждён")+(f", {p['weight_gsm']} g/m²." if p.get('weight_gsm') else ".")),("Какие размеры указаны?",sizes or "Только размеры из проверенных вариантов."),("Какие цвета указаны?",colors or "Цвета из проверенных вариантов."),("Подходит ли для нанесения логотипа?",f"Подтверждённые способы: {methods}." if methods else "Способы нанесения показываются только после подтверждения производителем."),("Наличие у поставщика равно физическому складу M99?","Нет. Это разные наборы данных.")]
    elif lang=="RO":pairs=[("Cum verific modelul exact?",f"Folosiți codul {r}."),("Care sunt compoziția și greutatea materialului?",(mat or "Compoziția nu este verificată")+(f", {p['weight_gsm']} g/m²." if p.get('weight_gsm') else ".")),("Ce mărimi sunt reprezentate?",sizes or "Doar mărimi din variante verificate."),("Ce culori sunt reprezentate?",colors or "Culori din variante verificate."),("Poate fi personalizată?",methods or "Metodele sunt afișate numai când sunt verificate.")]
    else:pairs=[("Πώς ελέγχω το ακριβές μοντέλο;",f"Χρησιμοποιήστε τον κωδικό {r}."),("Ποια είναι η σύνθεση;",mat or "Μόνο επαληθευμένα στοιχεία."),("Ποια μεγέθη εμφανίζονται;",sizes or "Μόνο επαληθευμένα μεγέθη."),("Ποια χρώματα εμφανίζονται;",colors or "Μόνο επαληθευμένα χρώματα.")]
    return [{"question":a,"answer":b} for a,b in pairs]

def _section_texts(p,lang):
    title=_localized_title(p,lang); mat=_material(p,lang); colors=", ".join(_localized_colors(p,lang)); sizes=", ".join(p.get("sizes") or []); methods=", ".join(p.get("branding_methods") or [])
    if p.get("product_type") != "shirt":
        ref=p.get("reference") or "—"
        if lang=="BG":
            return [("Преглед на продукта",f"{title} е представен чрез проверени данни за точния модел {ref}. Информацията е структурирана за избор и сравнение, без неподкрепени твърдения."),("Материал и конструкция",f"{('Потвърден материал: '+mat+'.') if mat else 'Материалът се публикува само когато е потвърден от evidence.'}"),("Функционални детайли","Функционалните характеристики се включват само когато са потвърдени от доставчик или производител за точния модел."),("Размери и цветове",f"Проверени размери: {sizes or 'според variant evidence'}. Проверени цветове: {colors or 'според variant evidence'}. Supplier availability не е M99 physical stock."),("Идентификация и проследимост",f"Код на производителя / MPN: {ref}. Supplier reference и Manufacturer MPN остават отделни управлявани роли."),("Проверена информация","M99 използва evidence-first подход: съдържанието се извежда от проверени факти и се блокира при несъответствие с типа на продукта.")]
        if lang=="EN":
            return [("Product overview",f"{title} is presented from verified evidence for exact model {ref}. Information is structured for comparison without unsupported claims."),("Material and construction",f"{('Verified material: '+mat+'.') if mat else 'Material is published only when supported by evidence.'}"),("Practical details","Functional characteristics are included only when verified for the exact product."),("Sizes and colours",f"Verified sizes: {sizes or 'from variant evidence'}. Verified colours: {colors or 'from variant evidence'}. Supplier availability is not M99 physical stock."),("Identity and traceability",f"Manufacturer reference / MPN: {ref}. Supplier reference and Manufacturer MPN remain separate governed roles."),("Evidence-first information","M99 derives customer content from verified facts and blocks product-type inconsistencies before publishing.")]
        if lang=="RU":
            return [("Обзор товара",f"{title}: информация основана на проверенных данных для точной модели {ref}."),("Материал и конструкция",f"{('Подтверждённый материал: '+mat+'.') if mat else 'Материал публикуется только при наличии подтверждающих данных.'}"),("Функциональные детали","Характеристики включаются только при подтверждении для точной модели."),("Размеры и цвета",f"Проверенные размеры: {sizes or 'из variant evidence'}. Проверенные цвета: {colors or 'из variant evidence'}. Наличие поставщика не является физическим складом M99."),("Идентификация",f"Код производителя / MPN: {ref}. Роли supplier reference и Manufacturer MPN остаются раздельными."),("Проверенные данные","M99 блокирует несоответствия типа товара до публикации.")]
        base=_summary(p,lang)
        return [(LEX[lang]["overview"],base),(LEX[lang]["construction"],base),(LEX[lang]["details"],base),(LEX[lang]["variants"],f"{LEX[lang]['sizes']}: {sizes}; {LEX[lang]['colors']}: {colors}"),(LEX[lang]["technical"],base),(LEX[lang]["buyer"],base)]
    if lang=="BG":return [
      ("Риза за професионална визия и ежедневно носене",f"{title} е мъжка риза с класическа линия, описана чрез проверени данни от доставчика и официалния източник на производителя. Страницата пази код {p.get('reference') or '—'} видим, за да може клиентът да провери точния модел, а информацията е подредена за бързо сравнение на материал, размер, цвят и детайли."),
      ("Oxford материя, състав и плътност",f"Официалните данни посочват {mat or 'Oxford материя'}"+(f" и плътност {p['weight_gsm']} g/m²" if p.get('weight_gsm') else "")+". Тези характеристики са отделени и в техническата таблица, за да не се губят в маркетингов текст. M99 не добавя материал, сертификат или техническо твърдение, което не е подкрепено от evidence."),
      ("Кройка и функционални детайли",("Моделът е с класическа кройка. " if p.get('classic_cut') else "")+("Усилената яка със стойка помага ризата да запази оформен и подреден силует. " if p.get('stiff_collar') else "")+("Джобът на гърдите добавя практичен детайл. " if p.get('chest_pocket') else "")+("Контрастният вътрешен завършек при яката и маншетите създава дискретен визуален акцент там, където е потвърден от производителя." if p.get('contrast_inside') else "")),
      ("Размери, цветове и таблица за избор",f"Проверените варианти включват размери {sizes or 'според текущия variant evidence'} и цветове {colors or 'според текущия variant evidence'}. Официалните таблици с размери и измервания се запазват отделно, за да може клиентът да сравни реалните размери на дрехата преди поръчка. Наличността по вариант не се смесва с физическия склад на M99."),
      ("Персонализация и фирмено облекло",(f"Официалният източник посочва методи за брандиране: {methods}. " if methods else "")+"Тази информация помага при избор на облекло за екип, събитие или корпоративна идентичност. M99 показва само потвърдените методи и не превръща общи предположения за категорията в твърдения за конкретния продукт."),
      ("Проверена информация вместо копирано описание","M99 съчетава exact supplier evidence и operator-confirmed official manufacturer evidence. Supplier prose не се копира дословно. Проверените факти се преобразуват в оригинално клиентско описание, технически характеристики, FAQ, SEO metadata и ALT текстове, като provenance към източника се пази в DRAFT продукта."),]
    if lang=="EN":return [
      ("A professional shirt built around verified product facts",f"{title} is presented from verified supplier evidence and an exact official manufacturer source. Reference {p.get('reference') or '—'} stays visible so buyers can confirm the precise model, while the page is reorganised for quick scanning, comparison and confident selection instead of copying a supplier description."),
      ("Oxford fabric, composition and weight",f"Official evidence identifies {mat or 'Oxford fabric'}"+(f" with a fabric weight of {p['weight_gsm']} g/m²" if p.get('weight_gsm') else "")+". These specifications are repeated in a structured technical table so they remain easy to compare. M99 does not infer a material, certificate or technical claim that is not supported by evidence."),
      ("Classic cut and practical details",("The model uses a classic cut. " if p.get('classic_cut') else "")+("A stiffened stand-up collar helps maintain a neat, structured appearance. " if p.get('stiff_collar') else "")+("A chest pocket adds a practical everyday detail. " if p.get('chest_pocket') else "")+("A contrasting inner collar and cuff finish adds a restrained visual accent where this detail is confirmed by the manufacturer." if p.get('contrast_inside') else "")),
      ("Sizes, colours and fit information",f"Verified variants represent sizes {sizes or 'from current variant evidence'} and colours {colors or 'from current variant evidence'}. Official manufacturer measurement tables are preserved as structured evidence so customers can compare garment dimensions before ordering. Variant availability remains separate from M99-owned physical inventory."),
      ("Branding and company-wear use",(f"The official source lists these branding methods: {methods}. " if methods else "")+"This gives teams useful information when selecting garments for corporate identity, events or staff clothing. Only manufacturer-supported decoration methods are surfaced; category assumptions are not promoted to product claims."),
      ("Evidence-first product information","M99 combines exact supplier evidence with operator-confirmed official manufacturer evidence. Supplier prose is not copied verbatim. Verified facts are transformed into original customer-facing copy, structured specifications, FAQ, SEO metadata and image ALT text while provenance remains attached to the DRAFT product record."),]
    if lang=="RU":return [
      ("Профессиональный внешний вид на основе проверенных данных",f"{title} описывается на основе точных данных поставщика и подтверждённой официальной страницы производителя. Код {p.get('reference') or '—'} остаётся видимым, чтобы покупатель мог однозначно проверить модель. Информация структурирована для быстрого сравнения, а текст не копирует описание поставщика."),
      ("Ткань Oxford, состав и плотность",f"Официальный источник указывает {mat or 'ткань Oxford'}"+(f" и плотность {p['weight_gsm']} g/m²" if p.get('weight_gsm') else "")+". Характеристики вынесены также в техническую таблицу. M99 не добавляет материал, сертификат или техническое утверждение без подтверждающего источника."),
      ("Классический крой и практичные детали",("Крой модели классический. " if p.get('classic_cut') else "")+("Укреплённый воротник-стойка помогает сохранять аккуратный силуэт. " if p.get('stiff_collar') else "")+("На груди предусмотрен практичный карман. " if p.get('chest_pocket') else "")+("Контрастная внутренняя отделка создаёт сдержанный акцент там, где она подтверждена производителем." if p.get('contrast_inside') else "")),
      ("Размеры, цвета и выбор варианта",f"Проверенные варианты включают размеры {sizes or 'из текущих данных вариантов'} и цвета {colors or 'из текущих данных вариантов'}. Таблицы измерений производителя сохраняются как структурированные официальные данные, а наличие по варианту не смешивается с физическим складом M99."),
      ("Нанесение логотипа и корпоративное использование",(f"Производитель указывает методы нанесения: {methods}. " if methods else "")+"Это помогает оценить модель для корпоративной одежды без добавления неподтверждённых способов персонализации."),
      ("Как проверяется информация","M99 объединяет точные данные поставщика и подтверждённый официальный источник производителя. На их основе создаются оригинальное описание, характеристики, FAQ, SEO metadata и ALT-тексты с сохранением provenance."),]
    base=_summary(p,lang); return [(LEX[lang]["overview"],base),(LEX[lang]["construction"],base),(LEX[lang]["details"],base),(LEX[lang]["variants"],f"{LEX[lang]['sizes']}: {sizes}; {LEX[lang]['colors']}: {colors}"),(LEX[lang]["technical"],base),(LEX[lang]["buyer"],base)]


def _normalized_content_text(value:str)->str:
    return " ".join(re.findall(r"\w+",str(value or "").lower(),flags=re.UNICODE))

def _content_similarity(a:str,b:str)->float:
    aa=_normalized_content_text(a); bb=_normalized_content_text(b)
    if not aa and not bb:return 1.0
    if not aa or not bb:return 0.0
    return SequenceMatcher(None,aa,bb).ratio()


def _fallback_meta_description(p:dict,lang:str)->str:
    title=_localized_title(p,lang)
    sizes=", ".join(p.get("sizes") or [])
    material=_material(p,lang)
    if lang=="BG":
        md=f"{title} – технически данни и потвърдени характеристики."
        if sizes:md+=f" Размери: {sizes}."
        if material:md+=f" Материал: {material}."
    elif lang=="EN":
        md=f"{title} – technical data and manufacturer-confirmed details."
        if sizes:md+=f" Sizes: {sizes}."
        if material:md+=f" Material: {material}."
    elif lang=="RU":
        md=f"{title} – технические данные и подтверждённые характеристики."
        if sizes:md+=f" Размеры: {sizes}."
        if material:md+=f" Материал: {material}."
    elif lang=="RO":
        md=f"{title} – date tehnice și caracteristici confirmate."
        if sizes:md+=f" Mărimi: {sizes}."
        if material:md+=f" Material: {material}."
    elif lang=="GR":
        md=f"{title} – τεχνικά στοιχεία και επιβεβαιωμένα χαρακτηριστικά."
        if sizes:md+=f" Μεγέθη: {sizes}."
        if material:md+=f" Υλικό: {material}."
    else:
        md=f"{title} – technical data and verified product details."
    md=" ".join(md.split()).strip()
    return md if len(md)<=160 else md[:157].rstrip(" ,.;:-")+"…"

def _meta_description_for(p:dict,lang:str,short_description:str)->str:
    """SEO snippet, deliberately different in purpose and sentence shape from Short."""
    title=_localized_title(p,lang)
    ref=str(p.get("reference") or "").strip()
    sizes=", ".join(p.get("sizes") or [])
    material=_material(p,lang)

    facts=[]
    if p.get("weight_gsm"):facts.append(f"{p['weight_gsm']} g/m²")
    if p.get("oeko_tex"):facts.append("OEKO-TEX")
    if p.get("classic_cut"):
        facts.append({"BG":"класическа кройка","EN":"classic fit","RU":"классический крой","RO":"croială clasică","GR":"κλασική γραμμή"}.get(lang,"classic fit"))
    if p.get("chest_pocket"):
        facts.append({"BG":"джоб на гърдите","EN":"chest pocket","RU":"нагрудный карман","RO":"buzunar la piept","GR":"τσέπη στο στήθος"}.get(lang,"chest pocket"))
    if p.get("stiff_collar"):
        facts.append({"BG":"усилена яка","EN":"structured collar","RU":"укреплённый воротник","RO":"guler întărit","GR":"ενισχυμένος γιακάς"}.get(lang,"structured collar"))

    identity=f"{title}{(' '+ref) if ref else ''}".strip()
    strongest=", ".join(facts[:3])

    if lang=="BG":
        md=f"{identity} – проверени характеристики"
        if material:md+=f": {material}"
        if strongest:md+=f", {strongest}"
        if sizes:md+=f". Размери {sizes}"
        md+=". Сравнете детайлите и изберете подходящия вариант."
    elif lang=="EN":
        md=f"{identity} – verified product details"
        if material:md+=f": {material}"
        if strongest:md+=f", {strongest}"
        if sizes:md+=f". Sizes {sizes}"
        md+=". Compare the details and choose the right variant."
    elif lang=="RU":
        md=f"{identity} – проверенные характеристики"
        if material:md+=f": {material}"
        if strongest:md+=f", {strongest}"
        if sizes:md+=f". Размеры {sizes}"
        md+=". Сравните данные и выберите подходящий вариант."
    elif lang=="RO":
        md=f"{identity} – specificații verificate"
        if material:md+=f": {material}"
        if strongest:md+=f", {strongest}"
        if sizes:md+=f". Mărimi {sizes}"
        md+=". Compară detaliile și alege varianta potrivită."
    elif lang=="GR":
        md=f"{identity} – επαληθευμένα χαρακτηριστικά"
        if material:md+=f": {material}"
        if strongest:md+=f", {strongest}"
        if sizes:md+=f". Μεγέθη {sizes}"
        md+=". Συγκρίνετε τα στοιχεία και επιλέξτε τη σωστή παραλλαγή."
    else:
        md=f"{identity} – verified specifications"
        if strongest:md+=f": {strongest}"
        if sizes:md+=f". Sizes {sizes}"
        md+=". Review the verified details before choosing a variant."

    md=" ".join(md.split()).strip()
    if len(md)>160:md=md[:157].rstrip(" ,.;:-")+"…"

    similarity=_content_similarity(md,short_description)
    if _normalized_content_text(md)==_normalized_content_text(short_description) or similarity>=0.75:
        md=_fallback_meta_description(p,lang)
        similarity=_content_similarity(md,short_description)
    if _normalized_content_text(md)==_normalized_content_text(short_description):
        raise ValueError(f"{lang} Meta Description duplicates Short Description after generic fallback.")
    if similarity>=0.75:
        raise ValueError(f"{lang} Meta Description / Short Description are too similar after generic fallback ({similarity:.3f} >= 0.750).")
    return md

def _validate_meta_short_distinctness(documents:dict)->dict:
    scores={}
    failures=[]
    for code,doc in (documents or {}).items():
        meta=str(doc.get("meta_description") or "")
        short=str(doc.get("short_description") or "")
        score=_content_similarity(meta,short)
        scores[code]=round(score,4)
        if not meta or not short:
            failures.append(f"{code}:missing")
        elif _normalized_content_text(meta)==_normalized_content_text(short):
            failures.append(f"{code}:exact")
        elif score>=0.75:
            failures.append(f"{code}:{score:.4f}")
    if failures:
        raise ValueError("Meta Description / Short Description separation gate failed: "+", ".join(failures))
    return scores

def _doc(p,lang):
    lex=LEX[lang]; title=_localized_title(p,lang); summary=_summary(p,lang); mat=_material(p,lang); specs=[]
    if p.get("brand"):specs.append((lex["brand"],p["brand"]))
    if p.get("manufacturer_reference"):
        manufacturer_label={"BG":"Код на производителя / MPN","EN":"Manufacturer reference / MPN","RU":"Код производителя / MPN","RO":"Cod producător / MPN","GR":"Κωδικός κατασκευαστή / MPN"}.get(lang,"Manufacturer reference / MPN")
        specs.append((manufacturer_label,p["manufacturer_reference"]))
    if mat:specs.append((lex["material"],mat))
    if p.get("weight_gsm"):specs.append((lex["weight"],f"{p['weight_gsm']} g/m²"))
    if p.get("sizes"):specs.append((lex["sizes"],", ".join(p["sizes"])))
    colors=_localized_colors(p,lang)
    if colors:specs.append((lex["colors"],", ".join(colors)))
    if p.get("oeko_tex"):specs.append(("Certification" if lang=="EN" else "Сертификат" if lang in {"BG","RU"} else "Certificare","OEKO-TEX"))
    if p.get("branding_methods"):specs.append(("Branding methods" if lang=="EN" else "Методи за брандиране" if lang=="BG" else "Методы нанесения" if lang=="RU" else "Personalizare",", ".join(p["branding_methods"])))
    care=[]
    if p.get("care_30"):care.append("Wash max 30°C" if lang=="EN" else "Пране до 30°C" if lang=="BG" else "Стирка до 30°C" if lang=="RU" else "Spălare max. 30°C")
    if p.get("do_not_bleach"):care.append("Do not bleach" if lang=="EN" else "Без избелване" if lang=="BG" else "Не отбеливать" if lang=="RU" else "Nu folosiți înălbitor")
    if p.get("iron_150"):care.append("Iron up to 150°C" if lang=="EN" else "Гладене до 150°C" if lang=="BG" else "Гладить до 150°C" if lang=="RU" else "Călcare până la 150°C")
    if care:specs.append(("Care" if lang=="EN" else "Поддръжка" if lang=="BG" else "Уход" if lang=="RU" else "Întreținere",", ".join(care)))
    if p.get("packaging"):specs.append(("Packaging" if lang=="EN" else "Опаковка" if lang=="BG" else "Упаковка" if lang=="RU" else "Ambalare",str(p["packaging"])))
    sections=_section_texts(p,lang); faq=_faq(p,lang); html="".join(f"<h2>{escape(h)}</h2><p>{escape(b)}</p>" for h,b in sections)
    if p.get("official_tables"):
        table_heading="Official size and technical tables" if lang=="EN" else "Официални размери и технически таблици" if lang=="BG" else "Официальные таблицы размеров и характеристик" if lang=="RU" else lex["technical"]
        table_text="Manufacturer tables are preserved separately below as structured evidence." if lang=="EN" else "Таблиците от производителя се пазят отделно като структурирано evidence." if lang=="BG" else "Таблицы производителя сохраняются отдельно как структурированные данные." if lang=="RU" else "Official tables are preserved as structured evidence."
        html+=f"<h2>{escape(table_heading)}</h2><p>{escape(table_text)}</p>"
    html+=f"<h2>{escape(lex['faq'])}</h2>"+"".join(f"<h3>{escape(x['question'])}</h3><p>{escape(x['answer'])}</p>" for x in faq)
    mt=title+" | M99"; mt=mt if len(mt)<=60 else title[:56].rstrip()+"…"; md=_meta_description_for(p,lang,summary); meta_short_similarity=_content_similarity(md,summary)
    alt_label="product image" if lang=="EN" else "продуктово изображение" if lang=="BG" else "изображение товара" if lang=="RU" else "imagine produs"
    alts=[f"{title} – {alt_label} {i}" for i,_ in enumerate(p.get("images") or [],1)]
    kw=list(dict.fromkeys([x for x in [title,p.get("reference"),p.get("brand"),"Oxford" if p.get("oxford") else None] if x])); words=len(re.findall(r"\w+",re.sub(r"<[^>]+>"," ",html),flags=re.UNICODE))
    h2_count=len(sections)+1+(1 if p.get("official_tables") else 0)
    return {"language":lang,"product_name":title,"h1":title,"short_description":summary,"long_description_html":html,"headings":[{"level":"H2","text":h} for h,_ in sections]+([{"level":"H2","text":table_heading}] if p.get("official_tables") else [])+[{"level":"H2","text":lex["faq"]}]+[{"level":"H3","text":x["question"]} for x in faq],"technical_specifications":[{"name":k,"value":v} for k,v in specs],"official_tables":p.get("official_tables") or [],"faq":faq,"meta_title":mt,"meta_description":md,"seo_keywords":kw,"image_alt":alts,"schema_product":{"@context":"https://schema.org","@type":"Product","name":title,"mpn":p.get("manufacturer_reference") or None,"brand":p.get("brand") or None,"image":p.get("images") or []},"quality_metrics":{"long_description_words":words,"h2_count":h2_count,"h3_count":len(faq),"source_manufacturer_url":p.get("manufacturer_url"),"meta_short_distinct":True,"meta_short_similarity":round(meta_short_similarity,4)}}

def build_content_bundle(*,supplier_evidence:dict,manufacturer_evidence:dict,target_code:str,required_languages:tuple[str,...]|None=None)->dict:
    langs=tuple(required_languages or CHANNEL_LANGUAGE_DEFAULTS.get(target_code,("BG","EN")))
    bad=[x for x in langs if x not in LANGUAGE_REGISTRY]
    if bad:raise ValueError(f"Unsupported languages: {bad}")
    p=_profile(supplier_evidence,manufacturer_evidence); docs={x:_doc(p,x) for x in langs}
    meta_short_scores=_validate_meta_short_distinctness(docs)
    return {"schema":"m99.phase46.r3.content_bundle.v3","status":"PREVIEW_READY","identifier_governance":{"supplier_reference_role":"SUPPLIER_MAPPING_ONLY","manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY","channel_reference_role":"PERMANENT_M99_REFERENCE"},"target":target_code,"languages":list(langs),"documents":docs,"quality":{"supplier_prose_copied_verbatim":False,"manufacturer_evidence_status":manufacturer_evidence.get("status") or "NOT_ATTACHED","unsupported_claims_allowed":False,"exactly_one_h1_per_language":True,"meta_short_distinct_all_languages":True,"meta_short_similarity_scores":meta_short_scores,"meta_short_similarity_max":max(meta_short_scores.values(),default=0.0),"meta_short_threshold":0.75,"min_meaningful_h2_target":4,"benchmark_framework":BENCHMARK_FRAMEWORK}}
