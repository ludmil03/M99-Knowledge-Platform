from __future__ import annotations
# M99_BULTEX99_NATIVE_SOURCE_CHANNEL_M5
# M99_BULTEX99_FULL_CATALOG_INTEGRITY_M6
from dataclasses import dataclass
from html.parser import HTMLParser
from html import unescape
from http.client import HTTPSConnection
from urllib.parse import urlparse,urljoin
import json,re,ssl

DOMAIN="bultex99.com"
class Bultex99NativeError(RuntimeError):pass

@dataclass(frozen=True)
class NativeCategory: label:str; url:str
@dataclass(frozen=True)
class NativeVariant: label:str; code:str; url:str; image_url:str=""; value:str=""; sizes:tuple=()
@dataclass(frozen=True)
class NativeProduct:
 name:str; url:str; source_key:str; supplier_reference:str=""; calenda_product_id:str=""; variants:tuple=(); image_url:str=""; integrity_state:str="VALID"; integrity_reason:str=""
@dataclass(frozen=True)
class NativeHydrated:
 name:str;url:str;source_key:str;supplier_reference:str;calenda_product_id:str;brand:str;price_text:str;currency:str;availability_text:str;description:str;images:tuple;variants:tuple;selected_variant_code:str="";warnings:tuple=();hydration_pass:bool=False

def _clean(v):return " ".join(unescape(re.sub(r"<[^>]+>"," ",str(v or ""))).split())
def _host(u):
 h=(urlparse(u).hostname or "").lower();return h[4:] if h.startswith("www.") else h
def _assert_native(u):
 if _host(u)!=DOMAIN:raise Bultex99NativeError("CROSS_DOMAIN_BLOCKED")
def _get(u,timeout=25):
 _assert_native(u);p=urlparse(u);path=p.path or "/";path+=("?"+p.query if p.query else "")
 try:
  import certifi;ctx=ssl.create_default_context(cafile=certifi.where())
 except Exception as exc:raise Bultex99NativeError("TLS_TRUST_STORE_UNAVAILABLE") from exc
 c=HTTPSConnection(DOMAIN,443,timeout=timeout,context=ctx)
 try:
  c.request("GET",path,headers={"User-Agent":"M99Knowledge/6 Bultex99NativeIntegrityReadOnly","Accept":"text/html","Connection":"close"})
  r=c.getresponse();b=r.read()
  if r.status!=200:raise Bultex99NativeError("HTTP_"+str(r.status))
  return b.decode("utf-8","replace")
 except Bultex99NativeError:raise
 except Exception as exc:raise Bultex99NativeError("READ_FAILED") from exc
 finally:
  try:c.close()
  except Exception:pass

def _abs(x):return urljoin("https://bultex99.com/",x)
def _source_key(u):
 m=re.search(r"/products/(\d+)(?:-|/|$)",urlparse(u).path);return m.group(1) if m else urlparse(u).path.rstrip("/").rsplit("/",1)[-1]

_COLOR={"black","white","blue","navy","royal","green","red","grey","gray","beige","brown","pink","purple","orange","yellow","graphite","anthracite","petrol","teal","mauve","fuchsia","smoke","sand","khaki","черен","черна","черно","бял","бяла","бяло","син","синя","синьо","тъмно","светло","кралско","зелен","зелена","червен","червена","сив","сива","бежов","бежова","кафяв","розов","лилав","оранжев","жълт","графит","антрацит","петрол","тюркоаз","бордо","екрю","пепел","рози"}
def _family_key(title):
 w=re.findall(r"[0-9A-Za-zА-Яа-яЁё+./-]+",_clean(title))
 while w and w[-1].casefold() in _COLOR:w.pop()
 return " ".join(w).casefold().strip() or _clean(title).casefold()
def _pure_colour(title):
 w=re.findall(r"[A-Za-zА-Яа-я]+",_clean(title).casefold())
 return bool(w and len(w)<=4 and all(x in _COLOR or x in {"от","рози"} for x in w))

class _CollectionParser(HTMLParser):
 def __init__(self):super().__init__();self.href=None;self.buf=[];self.rows=[]
 def handle_starttag(self,t,a):
  if t=="a":
   d=dict(a);h=d.get("href","")
   if "/collections/" in h:self.href=h;self.buf=[]
 def handle_data(self,d):
  if self.href:self.buf.append(d)
 def handle_endtag(self,t):
  if t=="a" and self.href:
   n=_clean(" ".join(self.buf));self.rows.append((self.href,n));self.href=None;self.buf=[]

class _ProductCardParser(HTMLParser):
 """M6R3 accepts heading- or explicit product-card-class evidence.
 Plain /products/ navigation/recommendation links remain fail-closed."""
 _HINTS=("product-title","product__title","card__heading","card-title","product-item",
         "product-name","product_name","grid-product__title","product-card","product-card__title")
 def __init__(self):
  super().__init__();self.href=None;self.depth=0;self.heading=0;self.title_text=[];self.image="";self.hint=False;self.rows=[]
 def handle_starttag(self,t,a):
  d=dict(a);cls=d.get("class","").casefold()
  if t=="a" and "/products/" in d.get("href","") and self.href is None:
   self.href=d["href"];self.depth=1;self.heading=0;self.title_text=[];self.image=""
   self.hint=any(x in cls for x in self._HINTS)
  elif self.href and t not in ("img","meta","link","input","br","hr","source","area","base","col","embed","param","track","wbr"):self.depth+=1
  if self.href:
   if t in ("h2","h3","h4"):self.heading+=1;self.hint=True
   if any(x in cls for x in self._HINTS):self.hint=True
   if t=="img" and not self.image:self.image=d.get("src") or d.get("data-src") or d.get("srcset","").split(" ")[0]
 def handle_data(self,d):
  if self.href and (self.heading or self.hint):self.title_text.append(d)
 def handle_endtag(self,t):
  if not self.href:return
  if t in ("h2","h3","h4") and self.heading:self.heading-=1
  self.depth-=1
  if t=="a" and self.depth<=0:
   title=_clean(" ".join(self.title_text))
   if self.hint and title:self.rows.append((self.href,title,self.image))
   self.href=None;self.depth=0;self.heading=0;self.title_text=[];self.image="";self.hint=False


class _ProductAnchorDiagnosticParser(HTMLParser):
 def __init__(self):super().__init__();self.rows=[]
 def handle_starttag(self,t,a):
  if t!="a":return
  d=dict(a);h=d.get("href","")
  if "/products/" not in h:return
  cls=_clean(d.get("class",""))[:120]
  self.rows.append((h,cls))

def _product_anchor_diagnostic(h):
 p=_ProductAnchorDiagnosticParser();p.feed(h)
 rows=[];seen=set()
 for href,cls in p.rows:
  path=urlparse(_abs(href)).path
  key=(path,cls)
  if key in seen:continue
  seen.add(key);rows.append(key)
 samples=rows[:8]
 cls_samples=sorted({c for _,c in rows if c})[:8]
 return "PRODUCT_ANCHORS=%d|PATHS=%s|CLASSES=%s"%(len(rows),",".join(x for x,_ in samples),",".join(cls_samples))

def _collection_links(h):
 p=_CollectionParser();p.feed(h);out=[];seen=set()
 skip={"/collections/all","/collections/new-products","/collections/bestellers","/collections/best-selling","/collections/namalenie"}
 for href,name in p.rows:
  u=_abs(href.split("?")[0])
  if name and urlparse(u).path not in skip and u not in seen:seen.add(u);out.append(NativeCategory(name,u))
 return out

def _product_cards(h):
 p=_ProductCardParser();p.feed(h);out=[];seen=set()
 for href,name,img in p.rows:
  u=_abs(href.split("?")[0]);img=_abs(img) if img else ""
  if u not in seen:seen.add(u);out.append((name,u,img))
 return out

_FOOTWEAR=("обув","сабо","чех","боти","ботуш","сандал","маратон","shoe","clog","boot","sandal")
_GARMENT=("туник","пантал","яке","риза","гащер","елек","престил","тениск","блуз","суит","рокл","пола","шап","jacket","shirt","trouser","tunic","vest","overall")
_RESP=("маска","респиратор","филтър","самоспас","детектор","mask","respirator","filter")
_GLOVE=("ръкавиц","glove")
def _has(title,words):return any(x in title.casefold() for x in words)
def _category_profile(label,url):
 x=(label+" "+urlparse(url).path.replace("-"," ")).casefold()
 if "медицин" in x and any(k in x for k in ("обув","сабо","чех")):return "MEDICAL_FOOTWEAR"
 if "медицин" in x:return "MEDICAL_CLOTHING"
 if any(k in x for k in ("работни обув","rabotni obuv","obuvki")):return "WORK_FOOTWEAR"
 if any(k in x for k in ("дихател","respirat","maski-i-filtri")):return "RESPIRATORY"
 if "ръкавиц" in x:return "GLOVES"
 return "SOURCE_COLLECTION"

def _category_integrity(label,url,title):
 p=_category_profile(label,url)
 if p=="WORK_FOOTWEAR":
  return ("VALID","") if _has(title,_FOOTWEAR) else ("CATEGORY_CONFLICT","WORK_FOOTWEAR_REJECTS_NON_FOOTWEAR")
 if p=="MEDICAL_CLOTHING":
  if _has(title,_FOOTWEAR):return ("CATEGORY_CONFLICT","MEDICAL_CLOTHING_REJECTS_FOOTWEAR")
  return ("VALID","") if _has(title,_GARMENT+_GLOVE) else ("AMBIGUOUS","MEDICAL_CLOTHING_UNPROVEN")
 if p=="MEDICAL_FOOTWEAR":
  return ("VALID","") if _has(title,_FOOTWEAR) else ("CATEGORY_CONFLICT","MEDICAL_FOOTWEAR_REJECTS_NON_FOOTWEAR")
 if p=="RESPIRATORY":
  return ("VALID","") if _has(title,_RESP) else ("CATEGORY_CONFLICT","RESPIRATORY_REJECTS_NON_RESPIRATORY")
 if p=="GLOVES":
  return ("VALID","") if _has(title,_GLOVE) else ("CATEGORY_CONFLICT","GLOVES_REJECTS_NON_GLOVES")
 return ("VALID","SOURCE_COLLECTION_CARD_EVIDENCE")

def _group(cards,label="",category_url=""):
 groups={}
 blocked=[]
 for n,u,img in cards:
  if _pure_colour(n):
   blocked.append((n,u,"VARIANT_COLOR_ONLY"));continue
  state,reason=_category_integrity(label,category_url,n)
  if state!="VALID":
   blocked.append((n,u,state+":"+reason));continue
  groups.setdefault(_family_key(n),[]).append((n,u,img))
 out=[]
 for members in groups.values():
  members=sorted(set(members),key=lambda x:(len(x[0]),x[0].casefold(),x[1]));n,u,img=members[0]
  vs=tuple(NativeVariant(x,_source_key(y),y,z,value=x) for x,y,z in members[1:])
  out.append(NativeProduct(n,u,_source_key(u),calenda_product_id=_source_key(u),variants=vs,image_url=img))
 return sorted(out,key=lambda x:x.name.casefold()),tuple(blocked)

def _meta(h,k):
 for tag in re.findall(r"<meta\b[^>]*>",h,re.I):
  if re.search(r'(?:property|name)=["\']'+re.escape(k)+r'["\']',tag,re.I):
   m=re.search(r'content=["\']([^"\']*)',tag,re.I)
   if m:return _clean(m.group(1))
 return ""
def _title(h):
 m=re.search(r"<h1\b[^>]*>(.*?)</h1>",h,re.I|re.S);return _clean(m.group(1)) if m else _meta(h,"og:title")
def _article(h):
 m=re.search(r"Арт\.\s*№\s*:?\s*([A-Za-z0-9._/-]+)",_clean(h),re.I);return m.group(1) if m else ""
def _price(h):
 m=re.search(r"€\s*([0-9][0-9., ]*)",_clean(h));return (m.group(1).strip().replace(" ",""),"EUR") if m else ("","")
def _product_images(h):
 out=[]
 for k in ("og:image","og:image:secure_url"):
  x=_meta(h,k)
  if x:
   x=_abs(x)
   if x not in out:out.append(x)
 for block in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',h,re.I|re.S):
  try:
   data=json.loads(block)
   items=data if isinstance(data,list) else [data]
   for d in items:
    if not isinstance(d,dict) or d.get("@type")!="Product":continue
    ims=d.get("image",[])
    if isinstance(ims,str):ims=[ims]
    for x in ims:
     if isinstance(x,str):
      x=_abs(x)
      if x not in out:out.append(x)
  except Exception:pass
 return tuple(out[:20])

class Bultex99NativeSourceChannel:
 kind="BULTEX99_NATIVE_M6";domain=DOMAIN;read_only=True
 def __init__(self,base_url="https://bultex99.com"):
  if _host(base_url)!=DOMAIN:raise Bultex99NativeError("INVALID_BASE_DOMAIN")
  self.base_url="https://bultex99.com";self.last_integrity_blocks=()
 def list_categories(self):
  x=_collection_links(_get(self.base_url))
  if not x:raise Bultex99NativeError("NO_NATIVE_COLLECTIONS_DISCOVERED")
  return x
 def list_products(self,category_url,category_label=""):
  _assert_native(category_url)
  if "/collections/" not in urlparse(category_url).path:raise Bultex99NativeError("NOT_A_COLLECTION_URL")
  html=_get(category_url);cards=_product_cards(html)
  if not cards:raise Bultex99NativeError("NO_PRODUCT_CARD_EVIDENCE|"+_product_anchor_diagnostic(html))
  x,b=_group(cards,category_label,category_url);self.last_integrity_blocks=b
  if not x:raise Bultex99NativeError("CATEGORY_INTEGRITY_BLOCKED_ALL_PRODUCTS")
  return x
 def get_product(self,product_url):
  _assert_native(product_url)
  if "/products/" not in urlparse(product_url).path:raise Bultex99NativeError("NOT_A_PRODUCT_URL")
  h=_get(product_url);n=_title(h);sku=_article(h);p,c=_price(h);imgs=_product_images(h);warn=[]
  if not n:warn.append("NAME_NOT_OBSERVED")
  if not sku:warn.append("SUPPLIER_SKU_NOT_OBSERVED")
  if not p:warn.append("PRICE_NOT_OBSERVED")
  if not imgs:warn.append("PRODUCT_IMAGE_NOT_PROVEN")
  v=NativeVariant("Observed product",_source_key(product_url),product_url,imgs[0] if imgs else "")
  return NativeHydrated(n,product_url,_source_key(product_url),sku,_source_key(product_url),"",p,c,"UNKNOWN",_meta(h,"og:description"),imgs,(v,),_source_key(product_url),tuple(warn),bool(n and sku and p and imgs))

Bultex99PublicConnector=Bultex99NativeSourceChannel
Bultex99ConnectorError=Bultex99NativeError
