from __future__ import annotations
from datetime import datetime,timezone
from html import unescape
from urllib.parse import urljoin
import json,re,requests

UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/150 Safari/537.36"}

MANUFACTURER_URL="https://cherokeeuniforms.com/products/womens-2-pocket-sweetheart-v-neck-scrub-top-ckww601"
STENSO_URL="https://stenso.net/produkt/medicinski-tuniki/4443-damska-medicinska-tunika-cherokee-v-neck-navy-wwe601"

def now(): return datetime.now(timezone.utc).isoformat()
def clean(v): return re.sub(r"\s+"," ",unescape(str(v or ""))).strip()
def norm(v): return re.sub(r"[^a-z0-9а-я]+","",str(v or "").lower())

def fetch(url,timeout=30):
    r=requests.get(url,headers=UA,timeout=timeout,allow_redirects=True)
    r.raise_for_status()
    return {"url":r.url,"html":r.text,"status":r.status_code,"observed_at_utc":now(),"content_type":r.headers.get("content-type","")}

def strip_html(h):
    h=re.sub(r"<script\b[^>]*>.*?</script>"," ",h,flags=re.I|re.S)
    h=re.sub(r"<style\b[^>]*>.*?</style>"," ",h,flags=re.I|re.S)
    return clean(re.sub(r"<[^>]+>"," ",h))

def extract_jsonld_products(html):
    out=[]
    for raw in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html,re.I|re.S):
        try:
            obj=json.loads(unescape(raw))
        except Exception:
            continue
        stack=obj if isinstance(obj,list) else [obj]
        while stack:
            x=stack.pop()
            if isinstance(x,list):
                stack.extend(x); continue
            if not isinstance(x,dict): continue
            typ=x.get("@type")
            types=typ if isinstance(typ,list) else [typ]
            if any(str(t).lower()=="product" for t in types if t):
                out.append(x)
            for v in x.values():
                if isinstance(v,(dict,list)): stack.append(v)
    return out

def meta(html,key):
    pats=[
      rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
      rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(key)}["\']',
      rf'<meta[^>]+name=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)'
    ]
    for pat in pats:
        m=re.search(pat,html,re.I)
        if m:return clean(m.group(1))
    return None

def parse_manufacturer():
    page=fetch(MANUFACTURER_URL)
    text=strip_html(page["html"])
    low=text.lower()
    products=extract_jsonld_products(page["html"])
    product=products[0] if products else {}

    colours=[]
    for c in ["Black","Caribbean Blue","Ciel","Navy","Pewter","Red","Teal Blue","Wine","Royal","Hunter"]:
        if c.lower() in low: colours.append(c)

    facts={
      "brand":"Cherokee",
      "collection":"WW Revolution" if "ww revolution" in low else None,
      "canonical_style":"WW601",
      "manufacturer_item":"CK-WW601--" if "ck-ww601--" in low or "ck-ww601" in low else product.get("sku"),
      "official_name":"Women's 2-Pocket Sweetheart V-Neck Scrub Top" if "2-pocket sweetheart v-neck scrub top" in low else product.get("name"),
      "fit":"Missy relaxed fit" if "missy relaxed fit" in low else None,
      "center_back_length_inches":26 if "center back length: 26" in low else None,
      "neckline":"Curved V-neckline" if "curved v-neckline" in low else None,
      "sleeves":"Short sleeves" if "short sleeves" in low else None,
      "pockets":"2 front patch pockets with instrument loops" if "2 front patch pockets with instrument loops" in low else None,
      "front_back_yokes":True if "front and back yokes" in low else None,
      "mesh_side_panels":True if "mesh side panels" in low else None,
      "shirttail_hem":True if "shirttail hemline" in low else None,
      "material":"78% polyester, 20% rayon, 2% spandex" if "78% polyester, 20% rayon, 2% spandex" in low else None,
      "fabric":"Silky stretch twill fabric" if "silky stretch twill fabric" in low else None,
      "official_colours":colours,
      "navy_variant_proven":"Navy" in colours,
    }

    images=[]
    image=product.get("image")
    if isinstance(image,str): images.append(image)
    elif isinstance(image,list): images.extend([x for x in image if isinstance(x,str)])
    og=meta(page["html"],"og:image")
    if og: images.append(og)

    # Manufacturer commercial observations are kept but not used as M99 selling price.
    offers=product.get("offers") or {}
    if isinstance(offers,list): offers=offers[0] if offers else {}
    return {
      "source_type":"manufacturer",
      "source_name":"Cherokee Uniforms",
      "source_url":page["url"],
      "observed_at_utc":page["observed_at_utc"],
      "authority":"AUTHORITATIVE",
      "facts":facts,
      "official_images":list(dict.fromkeys(images)),
      "commercial_observation":{
        "price":offers.get("price"),
        "currency":offers.get("priceCurrency"),
        "availability":offers.get("availability")
      }
    }

def extract_stenso_title(html):
    for pat in [
      r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
      r'<h1\b[^>]*>(.*?)</h1>',
      r'<title\b[^>]*>(.*?)</title>'
    ]:
        m=re.search(pat,html,re.I|re.S)
        if m:return strip_html(m.group(1))
    return None

def parse_stenso():
    page=fetch(STENSO_URL)
    text=strip_html(page["html"]); low=text.lower()
    title=extract_stenso_title(page["html"])
    ref=None
    for pat in [r"(?:Арт\.?\s*№|Артикул|Reference|SKU)\s*:?\s*([A-Za-z0-9._/-]{4,30})",r"\b(08001931)\b"]:
        m=re.search(pat,text,re.I)
        if m: ref=m.group(1); break

    prices=[]
    for pat,curr in [(r"(\d+[.,]\d{1,2})\s*(?:лв\.?|BGN)","BGN"),(r"(\d+[.,]\d{1,2})\s*(?:€|EUR)","EUR")]:
        for val in re.findall(pat,text,re.I):
            try:
                x={"value":float(val.replace(",",".")),"currency":curr}
                if x not in prices:prices.append(x)
            except: pass

    sizes=[]
    for size in ["2XS","XS","S","M","L","XL","2XL","3XL","4XL","5XL"]:
        if re.search(r"(?<![A-Za-z0-9])"+re.escape(size)+r"(?![A-Za-z0-9])",text,re.I):
            sizes.append(size)

    material=None
    for candidate in [
      "78% polyester, 20% rayon, 2% spandex",
      "78% полиестер, 20% вискоза, 2% еластан"
    ]:
        if norm(candidate) in norm(text): material=candidate; break

    images=[]
    for u in re.findall(r'<img[^>]+(?:src|data-src)=["\']([^"\']+)',page["html"],re.I):
        full=urljoin(page["url"],unescape(u))
        if "wwe601" in full.lower() or "4443" in full.lower(): images.append(full)

    return {
      "source_type":"supplier",
      "source_name":"Stenso",
      "source_url":page["url"],
      "observed_at_utc":page["observed_at_utc"],
      "identity":{
        "brand":"Cherokee" if "cherokee" in low else None,
        "supplier_style_alias":"WWE601" if "wwe601" in low else None,
        "target_colour":"NAVY / DARK BLUE" if ("navy" in low or "dark blue" in low) else None,
        "supplier_reference":ref,
        "title":title,
      },
      "facts":{
        "material":material,
        "sizes_visible":sizes,
      },
      "commercial_observation":{
        "raw_price_observations":prices,
        "availability":"IN_STOCK" if any(x in low for x in ["в наличност","in stock","последна наличност"]) else None,
        "m99_selling_price":None
      },
      "supplier_images":list(dict.fromkeys(images))[:20]
    }

def compare_fact(field,m_value,s_value):
    if not m_value and not s_value:return {"field":field,"status":"UNVERIFIED","selected":None}
    if m_value and not s_value:return {"field":field,"status":"MANUFACTURER_ONLY","selected":m_value,"authority":"manufacturer"}
    if not m_value and s_value:return {"field":field,"status":"SUPPLIER_ONLY","selected":s_value,"authority":"supplier","operator_review":True}
    if norm(m_value)==norm(s_value):return {"field":field,"status":"VERIFIED_CONSENSUS","selected":m_value,"authority":"manufacturer"}
    return {"field":field,"status":"SOURCE_CONFLICT","selected":m_value,"authority":"manufacturer","supplier_value":s_value,"operator_review":True}

def build_canonical(manufacturer,stenso,palltex=None):
    mf=manufacturer["facts"]; sf=stenso["facts"]; si=stenso["identity"]
    identity_conflicts=[]
    if si.get("brand") and norm(si["brand"])!=norm(mf["brand"]):
        identity_conflicts.append("BRAND_CONFLICT")
    # WW601 vs WWE601 is preserved as alias, not treated as destructive conflict.
    canonical={
      "brand":mf["brand"],
      "collection":mf["collection"],
      "canonical_style":mf["canonical_style"],
      "supplier_style_aliases":[x for x in [si.get("supplier_style_alias")] if x],
      "manufacturer_item":mf["manufacturer_item"],
      "target_colour":"NAVY",
      "official_name":mf["official_name"],
      "gender":"Women",
      "product_type":"Scrub top",
    }
    fact_merge=[
      compare_fact("material",mf.get("material"),sf.get("material")),
      {"field":"fit","status":"MANUFACTURER_ONLY","selected":mf.get("fit"),"authority":"manufacturer"},
      {"field":"center_back_length_inches","status":"MANUFACTURER_ONLY","selected":mf.get("center_back_length_inches"),"authority":"manufacturer"},
      {"field":"neckline","status":"MANUFACTURER_ONLY","selected":mf.get("neckline"),"authority":"manufacturer"},
      {"field":"sleeves","status":"MANUFACTURER_ONLY","selected":mf.get("sleeves"),"authority":"manufacturer"},
      {"field":"pockets","status":"MANUFACTURER_ONLY","selected":mf.get("pockets"),"authority":"manufacturer"},
      {"field":"mesh_side_panels","status":"MANUFACTURER_ONLY","selected":mf.get("mesh_side_panels"),"authority":"manufacturer"},
      {"field":"shirttail_hem","status":"MANUFACTURER_ONLY","selected":mf.get("shirttail_hem"),"authority":"manufacturer"},
      {"field":"fabric","status":"MANUFACTURER_ONLY","selected":mf.get("fabric"),"authority":"manufacturer"},
    ]
    conflicts=[x for x in fact_merge if x.get("status")=="SOURCE_CONFLICT"]
    return {
      "canonical_identity":canonical,
      "identity_status":"CANONICAL_READY" if not identity_conflicts else "IDENTITY_CONFLICT",
      "identity_conflicts":identity_conflicts,
      "fact_merge":fact_merge,
      "commercial":{
        "manufacturer":manufacturer["commercial_observation"],
        "Stenso":stenso["commercial_observation"],
        "Palltex":palltex["commercial_observation"] if palltex else None,
        "m99_selling_price":None,
        "operator_price_approval_required":True
      },
      "supplier_identity":{
        "Stenso":{"reference":si.get("supplier_reference"),"style_alias":si.get("supplier_style_alias"),"url":stenso["source_url"]},
        "Palltex":None if palltex is None else palltex.get("identity")
      },
      "assets":{
        "manufacturer_images":manufacturer["official_images"],
        "stenso_images":stenso["supplier_images"],
        "strategy":"PREFER_MANUFACTURER_IMAGES; SUPPLIER_IMAGES_REQUIRE_DEDUP_AND_OPERATOR_REVIEW"
      },
      "sizes":{
        "manufacturer_official_sizes":None,
        "stenso_visible_sizes":sf.get("sizes_visible",[]),
        "note":"Do not infer stock per size unless explicitly proven"
      },
      "content_evidence":{
        "ready":not conflicts and manufacturer["authority"]=="AUTHORITATIVE",
        "allowed_claim_fields":[x["field"] for x in fact_merge if x.get("selected") not in (None,"") and x.get("status")!="SOURCE_CONFLICT"],
        "blocked_conflicts":[x["field"] for x in conflicts],
        "language_targets":{"bg_sites":["bg","en","ru"],"ro_sites":["ro","en"]}
      },
      "m99_reference_proposed":None,
      "m99_productgroup_id_proposed":None,
      "operator_review_required":True,
      "write_allowed":False
    }
