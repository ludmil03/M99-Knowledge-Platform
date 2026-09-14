from __future__ import annotations
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.request import Request, urlopen
import json

BASE_URL="https://palltex.bg"
MAX_HTML_BYTES=4_000_000
USER_AGENT="M99-Knowledge-Platform/Rev31-Phase4.3-R2"
class PalltexConnectorError(RuntimeError): pass
@dataclass(frozen=True)
class SupplierCategory:
    key:str; label:str; url:str; parent_key:str|None=None
@dataclass(frozen=True)
class ProductSummary:
    source_key:str; name:str; url:str; price_text:str|None=None; availability_text:str|None=None; image_url:str|None=None
@dataclass(frozen=True)
class ProductHydration:
    source_key:str; name:str; url:str; supplier_reference:str|None; brand:str|None; price_text:str|None; currency:str|None; availability_text:str|None; description:str|None; images:tuple[str,...]; variants:tuple[dict,...]; hydration_pass:bool; warnings:tuple[str,...]
def _host(url):
    h=(urlparse(url).hostname or '').lower(); return h[4:] if h.startswith('www.') else h
def _safe(url):
    if _host(url)!='palltex.bg': raise PalltexConnectorError('URL is outside approved palltex.bg domain.')
    return url
def _fetch(url,timeout=25):
    _safe(url); req=Request(url,headers={'User-Agent':USER_AGENT,'Accept':'text/html,application/xhtml+xml','Accept-Language':'bg-BG,bg;q=0.9,en;q=0.7'})
    try:
        with urlopen(req,timeout=timeout) as r:
            final=r.geturl(); _safe(final); status=int(getattr(r,'status',200)); c=(r.headers.get('Content-Type') or '').lower()
            if 'html' not in c: raise PalltexConnectorError(f'Expected HTML, got {c or "unknown"}')
            raw=r.read(MAX_HTML_BYTES+1)
    except PalltexConnectorError: raise
    except Exception as e: raise PalltexConnectorError(f'Palltex read-only request failed: {e}') from e
    if len(raw)>MAX_HTML_BYTES: raise PalltexConnectorError('Palltex page exceeds safe HTML size.')
    return status,final,raw.decode('utf-8',errors='replace')
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.href=None; self.txt=[]; self.meta={}; self.scripts=[]; self.st=''; self.sd=[]; self.tp=[]; self.it=False
    def handle_starttag(self,t,a):
        d=dict(a); t=t.lower()
        if t=='a': self.href=d.get('href'); self.txt=[]
        elif t=='meta':
            k=(d.get('property') or d.get('name') or '').lower(); v=d.get('content') or ''
            if k and v:self.meta[k]=v
        elif t=='script': self.st=(d.get('type') or '').lower(); self.sd=[]
        elif t=='title': self.it=True
    def handle_endtag(self,t):
        t=t.lower()
        if t=='a':
            if self.href:self.links.append((self.href,' '.join(''.join(self.txt).split())))
            self.href=None; self.txt=[]
        elif t=='script':
            if self.st:self.scripts.append((self.st,''.join(self.sd)))
            self.st=''; self.sd=[]
        elif t=='title': self.it=False
    def handle_data(self,d):
        if self.href is not None:self.txt.append(d)
        if self.st:self.sd.append(d)
        if self.it:self.tp.append(d)
    @property
    def title(self):return ' '.join(''.join(self.tp).split())
def _parse(h): p=P(); p.feed(h); return p
def _is_category(u): return _host(u)=='palltex.bg' and urlparse(u).path.startswith('/bg/cat/')
def _is_product(u): return _host(u)=='palltex.bg' and urlparse(u).path.startswith('/bg/p/')
def _catkey(u):
    q=parse_qs(urlparse(u).query)
    for k,v in q.items():
        if k.startswith('categories[') and v:return urlparse(u).path.strip('/')+'?category='+v[0]
    return urlparse(u).path.strip('/')
def _dedupe(xs,key):
    out=[]; seen=set()
    for x in xs:
        k=key(x)
        if k not in seen:seen.add(k);out.append(x)
    return out
def _jsonld(p):
    out=[]
    for typ,raw in p.scripts:
        if 'ld+json' not in typ: continue
        try:d=json.loads(raw)
        except Exception:continue
        nodes=d if isinstance(d,list) else [d]
        for n in list(nodes):
            if isinstance(n,dict) and isinstance(n.get('@graph'),list):nodes+=n['@graph']
        for n in nodes:
            if isinstance(n,dict) and str(n.get('@type','')).lower()=='product':out.append(n)
    return out
def _offer(n):
    o=n.get('offers')
    if isinstance(o,list):o=o[0] if o else {}
    if not isinstance(o,dict):return None,None,None
    a=o.get('availability'); a=str(a).rsplit('/',1)[-1].upper() if a else None
    p=o.get('price') or o.get('lowPrice'); c=o.get('priceCurrency')
    return str(p) if p is not None else None,str(c) if c else None,a
class PalltexPublicConnector:
    def __init__(self,base_url=BASE_URL): self.base_url=_safe(base_url.rstrip('/')+'/')
    def health_check(self):
        s,u,h=_fetch(self.base_url); return {'ok':s==200,'status':s,'url':u}
    def list_categories(self):
        s,u,h=_fetch(self.base_url)
        if s!=200:raise PalltexConnectorError(f'HTTP {s}')
        p=_parse(h); out=[]
        for href,text in p.links:
            a=urljoin(u,href)
            if not _is_category(a):continue
            label=text.strip()
            if not label or label.lower() in {'виж повече','виж всички'}: label=urlparse(a).path.rstrip('/').split('/')[-1].replace('-',' ').title()
            out.append(SupplierCategory(_catkey(a),label,a))
        out=_dedupe(out,lambda x:x.url); out.sort(key=lambda x:(urlparse(x.url).path.count('/'),x.label.lower(),x.url)); return out
    def list_products(self,category):
        url=category.url if isinstance(category,SupplierCategory) else category
        s,u,h=_fetch(url)
        if s!=200:raise PalltexConnectorError(f'HTTP {s}')
        p=_parse(h); out=[]
        for href,text in p.links:
            a=urljoin(u,href)
            if _is_product(a) and text.strip():out.append(ProductSummary(a,' '.join(text.split()),a))
        return _dedupe(out,lambda x:x.url)
    def get_product(self,url):
        if not _is_product(url):raise PalltexConnectorError('Not a Palltex /bg/p/ product URL.')
        s,u,h=_fetch(url); p=_parse(h); nodes=_jsonld(p); n=nodes[0] if nodes else {}
        name=str(n.get('name') or p.meta.get('og:title') or p.title or '').strip(); sku=str(n.get('sku') or n.get('mpn') or '').strip() or None
        b=n.get('brand'); brand=(str(b.get('name') or '').strip() if isinstance(b,dict) else str(b).strip() if b else None)
        price,curr,av=_offer(n); desc=str(n.get('description') or p.meta.get('description') or '').strip() or None
        imgs=n.get('image') or []; imgs=[imgs] if isinstance(imgs,str) else list(imgs) if isinstance(imgs,list) else []
        og=p.meta.get('og:image'); imgs += [og] if og else []; imgs=tuple(_dedupe([urljoin(u,x) for x in imgs if x],lambda x:x))
        w=[]
        if not sku:w.append('SUPPLIER_REFERENCE_NOT_FOUND')
        if not price:w.append('PRICE_NOT_FOUND')
        if not imgs:w.append('IMAGES_NOT_FOUND')
        if not av:w.append('AVAILABILITY_NOT_FOUND')
        w.append('PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER')
        return ProductHydration(u,name,u,sku,brand,price,curr,av,desc,imgs,tuple(),bool(name and sku and price and imgs and av),tuple(w))

# M99-PALLTEX-HYDRATION-ADAPTER-R7J-BEGIN
from app.services.v073_phase45.palltex_product_hydration_adapter import install_adapter as _m99_install_palltex_hydration_adapter
_m99_install_palltex_hydration_adapter(globals())
# M99-PALLTEX-HYDRATION-ADAPTER-R7J-END
