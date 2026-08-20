from __future__ import annotations
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

UA = "M99KnowledgePlatform/0.7.0.5 (+controlled supplier read; no write)"

class SupplierReadError(RuntimeError):
    pass

def normalize_url(url:str)->str:
    url=url.strip()
    if not url.startswith(("http://","https://")):
        url="https://"+url
    return url

def same_host(url:str, base_url:str)->bool:
    return urlparse(url).netloc.lower().split(":")[0] == urlparse(base_url).netloc.lower().split(":")[0]

def fetch_html(url:str, timeout:float=20.0)->tuple[str,str,int]:
    url=normalize_url(url)
    try:
        with httpx.Client(follow_redirects=True,timeout=timeout,headers={"User-Agent":UA}) as c:
            r=c.get(url)
            if r.status_code>=400:
                raise SupplierReadError(f"HTTP {r.status_code}")
            ctype=(r.headers.get("content-type") or "").lower()
            if "html" not in ctype and "text" not in ctype:
                raise SupplierReadError(f"Unexpected content-type: {ctype}")
            return str(r.url),r.text,r.status_code
    except httpx.HTTPError as e:
        raise SupplierReadError(str(e)) from e

def page_title(soup:BeautifulSoup)->str:
    h1=soup.find("h1")
    if h1 and h1.get_text(" ",strip=True):
        return h1.get_text(" ",strip=True)[:500]
    if soup.title:
        return soup.title.get_text(" ",strip=True)[:500]
    return ""

def detect_stenso_supplier_ref(text:str)->str:
    patterns=[
        r"(?:Код|Референтен\s*номер|Артикул(?:ен)?\s*номер|Reference|Ref\.?)\s*[:#]?\s*([0-9A-Za-z._/-]{4,40})",
        r"\b(0[0-9]{7})\b",
    ]
    for p in patterns:
        m=re.search(p,text,re.I)
        if m:return m.group(1).strip()
    return ""

def classify_page(url:str,soup:BeautifulSoup)->str:
    path=urlparse(url).path.lower()
    if "/produkt/" in path or soup.select_one('[itemtype*="Product"], .product-info, .product-prices'):
        return "product"
    if re.search(r"/\d+[-_/]",path) or soup.select(".product-miniature, .product-container, article.product-miniature"):
        return "category"
    return "unknown"

def extract_product_links(final_url:str,soup:BeautifulSoup,limit:int=200)->list[dict]:
    host=urlparse(final_url).netloc.lower()
    found={}
    selectors=[
        "a.product-thumbnail","a.product-name","h2.product-title a","h3.product-title a",
        ".product-miniature a[href]","article.product-miniature a[href]",
        ".product-container a[href]"
    ]
    for sel in selectors:
        for a in soup.select(sel):
            href=a.get("href")
            if not href:continue
            u=urljoin(final_url,href)
            if urlparse(u).netloc.lower()!=host:continue
            path=urlparse(u).path.lower()
            if "/produkt/" not in path and "/product/" not in path:
                continue
            title=(a.get("title") or a.get_text(" ",strip=True) or "").strip()
            found.setdefault(u,{"url":u,"title":title[:500]})
            if len(found)>=limit:return list(found.values())
    if not found:
        for a in soup.find_all("a",href=True):
            u=urljoin(final_url,a["href"])
            if urlparse(u).netloc.lower()!=host:continue
            if "/produkt/" in urlparse(u).path.lower():
                title=(a.get("title") or a.get_text(" ",strip=True) or "").strip()
                found.setdefault(u,{"url":u,"title":title[:500]})
                if len(found)>=limit:break
    return list(found.values())

def inspect_supplier_page(url:str, supplier_base_url:str)->dict:
    final_url,html,http=fetch_html(url)
    if supplier_base_url and not same_host(final_url,supplier_base_url):
        raise SupplierReadError("URL host does not match selected supplier.")
    soup=BeautifulSoup(html,"html.parser")
    typ=classify_page(final_url,soup)
    title=page_title(soup)
    text=soup.get_text(" ",strip=True)
    result={"url":final_url,"http":http,"type":typ,"title":title,"supplier_reference":"" ,"products":[]}
    if typ=="product":
        result["supplier_reference"]=detect_stenso_supplier_ref(text)
        result["products"]=[{"url":final_url,"title":title,"supplier_reference":result["supplier_reference"]}]
    elif typ=="category":
        result["products"]=extract_product_links(final_url,soup)
    return result
