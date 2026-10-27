from __future__ import annotations
from dataclasses import dataclass, field
from html import unescape
import re
from urllib.parse import urljoin, urlparse
from http.client import HTTPSConnection, HTTPException
import ssl

BASE_HOSTS={"bultex99.com","www.bultex99.com"}
class Bultex99ConnectorError(RuntimeError): pass

@dataclass(frozen=True)
class Category:
    label:str
    url:str

@dataclass(frozen=True)
class Product:
    name:str
    url:str
    source_key:str
    supplier_reference:str|None=None
    calenda_product_id:str|None=None
    variants:tuple=()

@dataclass
class Hydrated:
    name:str
    url:str
    source_key:str
    supplier_reference:str|None
    price_text:str|None
    currency:str|None
    availability_text:str|None
    description:str|None
    brand:str|None=None
    images:list[str]=field(default_factory=list)
    variants:list=field(default_factory=list)
    warnings:list[str]=field(default_factory=list)
    hydration_pass:bool=False
    calenda_product_id:str|None=None
    selected_variant_code:str|None=None

def _host(url):
    return (urlparse(url).hostname or "").lower()

def _clean_text(s):
    s=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",unescape(s)).strip()

# M99_BULTEX_ONESHOT_HTTPS_R1
def _get(url, timeout=20):
    parsed=urlparse(url)
    host=(parsed.hostname or "").lower()
    if host not in BASE_HOSTS:
        raise Bultex99ConnectorError("Cross-domain Bultex99 URL blocked.")
    if parsed.scheme.lower() not in {"https","http"}:
        raise Bultex99ConnectorError("Unsupported URL scheme.")
    path=parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    # M99_BULTEX_CERTIFI_VERIFIED_M2
    try:
        import certifi
        tls_context=ssl.create_default_context(cafile=certifi.where())
    except Exception as exc:
        raise Bultex99ConnectorError('TLS_TRUST_STORE_UNAVAILABLE') from exc
    conn=HTTPSConnection(host,443,timeout=timeout,context=tls_context)
    try:
        conn.request("GET",path,headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) M99-Knowledge-Platform/1.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"bg-BG,bg;q=0.9,en;q=0.7",
            "Connection":"close",
        })
        response=conn.getresponse()
        body=response.read(5_000_000)
        if response.status not in range(200,300):
            raise Bultex99ConnectorError(f"HTTP_{response.status}")
        return body.decode("utf-8","replace")
    except Bultex99ConnectorError:
        raise
    except ssl.SSLCertVerificationError as exc:
        raise Bultex99ConnectorError("TLS_CERTIFICATE_VERIFY_FAILED") from exc
    except (TimeoutError,OSError,HTTPException) as exc:
        raise Bultex99ConnectorError("NETWORK_"+type(exc).__name__) from exc
    finally:
        conn.close()

def _abs(base,href):
    u=urljoin(base,href).split("#",1)[0]
    if _host(u) not in BASE_HOSTS:
        raise Bultex99ConnectorError("Cross-domain link blocked.")
    return u

# M99_CATEGORY_INTEGRITY_M3
_FOOTWEAR_POSITIVE=("обув","сабо","бот","сандал","маратон","shoe","safety shoe","low","mid","sneaker","moccas")
_FOOTWEAR_NEGATIVE=("елек","риза","гащеризон","сако","панталон","тенис","яке","суит","шапк","престил","vest","shirt","jacket","trouser","overall")
def _is_footwear_collection(url):
    p=urlparse(url).path.lower()
    return "/collections/176-rabotni-obuvki" in p or "rabotni-obuvki" in p
def _footwear_membership(category_url,name,product_url):
    if not _is_footwear_collection(category_url): return True
    n=_clean_text(name).casefold().strip()
    u=urlparse(product_url).path.casefold()
    url_negative=("vest","elek","shirt","riza","jacket","yake","trouser","pantal","overall","gasherizon","apron","prestil","sako")
    url_positive=("obuv","sabo","boti","botushi","sandal","maraton","shoe","boot","sneaker","moccas","uno-low")
    if any(x in u for x in url_negative): return False
    if any(x in n for x in _FOOTWEAR_NEGATIVE): return False
    if any(x in n for x in _FOOTWEAR_POSITIVE): return True
    if any(x in u for x in url_positive): return True
    try: t=_clean_text(_get(product_url)).casefold()
    except Exception: return False
    safety=any(x in t for x in ("en iso 20345","en iso:20345","s1ps","s3s","s1p","s3 ","s2 "))
    model=bool(re.search(r"\b(?:s1ps?|s2|s3s?|o1|o2|o6|esd|sr|fo|lg)\b",n))
    return bool(safety and model)

# M99_CATALOG_IDENTITY_VARIANTS_M4
_COLOR_WORDS={"черен","черна","черно","черни","бял","бяла","бяло","бели","син","синя","синьо","сини","тъмно син","светло син","зелен","зелена","зелено","зелени","червен","червена","червено","червени","сив","сива","сиво","сиви","тъмно сив","светло сив","жълт","жълта","жълто","жълти","оранжев","оранжева","оранжево","лилав","лилава","лилаво","бежов","бежова","бежово","бордо","екрю","кафяв","кафява","кафяво","розов","розова","розово","антрацит","графит","кралско син","небесно син","navy","black","white","blue","green","red","grey","gray","beige","bordeaux","orange","yellow","purple","brown","pink","anthracite","graphite"}
def _norm_words(value):
    v=_clean_text(value).casefold().replace("/"," ").replace("-"," ")
    return " ".join(v.split())
def _is_color_only_title(name):
    n=_norm_words(name)
    return bool(n and n in _COLOR_WORDS)
def _catalog_selectable_product(category_url,product):
    if _is_color_only_title(product.name): return False
    return _footwear_membership(category_url,product.name,product.url)

class Bultex99PublicConnector:
    def __init__(self,base_url="https://bultex99.com"):
        self.base_url=base_url.rstrip("/")

    def list_categories(self):
        html=_get(self.base_url+"/")
        out=[]; seen=set()
        pattern=r"<a\b[^>]*href=[\"']([^\"']*/collections/[^\"']+)[\"'][^>]*>(.*?)</a>"
        for m in re.finditer(pattern,html,re.I|re.S):
            href=m.group(1).split("?",1)[0]
            label=_clean_text(m.group(2))
            if not label or href.rstrip("/").endswith("/all"):
                continue
            try: u=_abs(self.base_url,href)
            except Bultex99ConnectorError: continue
            if u in seen: continue
            seen.add(u); out.append(Category(label[:180],u))
        if not out:
            out=[Category("Всички продукти",self.base_url+"/collections/all")]
        return out

    def list_products(self,category_url):
        if _host(category_url) not in BASE_HOSTS:
            raise Bultex99ConnectorError("Cross-domain category blocked.")
        html=_get(category_url)
        found={}; order=[]
        pattern=r"<a\b[^>]*href=[\"']([^\"']*/products/\d+[^\"']*)[\"'][^>]*>(.*?)</a>"
        for m in re.finditer(pattern,html,re.I|re.S):
            href=m.group(1).split("?",1)[0].split("#",1)[0]
            try: u=_abs(self.base_url,href)
            except Bultex99ConnectorError: continue
            pidm=re.search(r"/products/(\d+)",urlparse(u).path)
            if not pidm: continue
            name=_clean_text(m.group(2))
            if not name: continue
            if u not in found:
                order.append(u); found[u]=Product(name[:240],u,pidm.group(1))
        return [found[u] for u in order if _catalog_selectable_product(category_url,found[u])]

    def get_product(self,product_url):
        if _host(product_url) not in BASE_HOSTS:
            raise Bultex99ConnectorError("Cross-domain product blocked.")
        pm=re.search(r"/products/(\d+)",urlparse(product_url).path)
        if not pm:
            raise Bultex99ConnectorError("Unsupported Bultex99 product URL.")
        html=_get(product_url); text=_clean_text(html)
        h1=re.search(r"<h1\b[^>]*>(.*?)</h1>",html,re.I|re.S)
        name=_clean_text(h1.group(1)) if h1 else ""
        sku=re.search(r"Арт\.\s*№\s*:?\s*([A-Za-z0-9._/-]+)",text,re.I)
        price=re.search(r"€\s*(\d+(?:[.,]\d{1,2})?)\s*с\s*ДДС",text,re.I)
        availability="IN_STOCK" if re.search(r"В наличност",text,re.I) else ("OUT_OF_STOCK" if re.search(r"Изчерпано",text,re.I) else None)
        warnings=[]
        if not sku: warnings.append("SUPPLIER_SKU_NOT_STATED")
        if not price: warnings.append("GROSS_PRICE_NOT_STATED")
        return Hydrated(name=name,url=product_url,source_key=pm.group(1),
            supplier_reference=sku.group(1) if sku else None,
            price_text=price.group(1).replace(",",".") if price else None,
            currency="EUR" if price else None,availability_text=availability,
            description=None,warnings=warnings,hydration_pass=bool(name and price))
