from __future__ import annotations
from decimal import Decimal
from html import unescape
import re
from urllib.parse import urlparse
from .models import PublicProduct

class Bultex99PublicParseError(ValueError): pass

PRODUCT_RE=re.compile(r"^/products/(?P<id>\d+)(?:-[^/?#]+)?/?$")

def product_id_from_url(url:str)->str:
    m=PRODUCT_RE.match(urlparse(url).path)
    if not m: raise Bultex99PublicParseError("Unsupported Bultex99 product URL")
    return m.group("id")

def _text(html:str)->str:
    s=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",html,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",unescape(s)).strip()

def parse_public_product(html:str,source_url:str)->PublicProduct:
    pid=product_id_from_url(source_url); text=_text(html)
    h1=re.search(r"<h1\b[^>]*>(.*?)</h1>",html,re.I|re.S)
    name=_text(h1.group(1)) if h1 else ""
    sku=re.search(r"Арт\.\s*№\s*:?\s*([A-Za-z0-9._/-]+)",text,re.I)
    price=re.search(r"€\s*(\d+(?:[.,]\d{1,2})?)\s*с\s*ДДС",text,re.I)
    avail=None
    if re.search(r"В наличност",text,re.I): avail="IN_STOCK"
    elif re.search(r"Изчерпано",text,re.I): avail="OUT_OF_STOCK"
    standard=re.search(r"\b(EN\s*\d+(?::\d{4})?(?:\+A\d:\d{4})?)\b",text,re.I)
    if not name: raise Bultex99PublicParseError("Product name missing")
    return PublicProduct(
      supplier_product_id=pid,source_url=source_url,name=name,
      supplier_sku=sku.group(1) if sku else None,
      gross_price_eur=Decimal(price.group(1).replace(",",".")) if price else None,
      availability=avail,standard=standard.group(1) if standard else None)

def extract_collection_product_urls(html:str,base_url="https://bultex99.com")->list[str]:
    hrefs=re.findall(r'href=["\']([^"\']+)["\']',html,re.I)
    out=[]
    for h in hrefs:
      if "/products/" not in h: continue
      clean=h.split("?",1)[0].split("#",1)[0]
      u=clean if clean.startswith("http") else base_url.rstrip("/")+"/"+clean.lstrip("/")
      try: product_id_from_url(u)
      except Bultex99PublicParseError: continue
      if u not in out: out.append(u)
    return out
