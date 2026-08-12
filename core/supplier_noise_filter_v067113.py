import re
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

ALIASES=("WWE601","WW601","CK-WW601","CKWW601")
TARGET=("navy","dark blue","тъмно син","тъмносин")
WRONG=("grey","gray","black","сив","черен")

def norm(x):
    return re.sub(r"[^a-z0-9а-я]+","",str(x or "").lower())

def canonical_url(url):
    s=urlsplit(url)
    q=[(k,v) for k,v in parse_qsl(s.query,keep_blank_values=True)
       if not k.lower().startswith(("utm_","fbclid","gclid"))]
    path=re.sub(r"/+$","",s.path) or "/"
    return urlunsplit((s.scheme.lower(),s.netloc.lower(),path,urlencode(q,doseq=True),""))

def page_type(url):
    s=urlsplit(url); p=s.path.lower()
    if re.search(r"\.(jpg|jpeg|png|webp|gif)$",p): return "IMAGE_ASSET"
    if "/produkt/" in p or ("/product/" in p and not s.query): return "PRODUCT_PAGE"
    if "/search" in p or ("product" in p and s.query): return "SEARCH_PAGE"
    if "/cat" in p or re.search(r"/\d+-[^/]+$",p): return "CATEGORY_PAGE"
    return "OTHER"

def strip_tags(h):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",h or "")).strip()

def extract_title(h):
    m=re.search(r"<h1\\b[^>]*>(.*?)</h1>",h or "",re.I|re.S)
    if m and strip_tags(m.group(1)): return strip_tags(m.group(1)),"H1"
    m=re.search(r"<meta[^>]+property=[\"']og:title[\"'][^>]+content=[\"']([^\"']+)",h or "",re.I)
    if m: return m.group(1).strip(),"OG_TITLE"
    m=re.search(r"<title\\b[^>]*>(.*?)</title>",h or "",re.I|re.S)
    if m: return strip_tags(m.group(1)),"TITLE"
    return None,None

def classify(url,title="",text=""):
    pt=page_type(url)
    blob=norm((title or "")+" "+url+" "+(text or "")[:6000])
    brand="cherokee" in blob
    style=next((a for a in ALIASES if norm(a) in blob),None)
    target=next((c for c in TARGET if norm(c) in blob),None)
    wrong=next((c for c in WRONG if norm(c) in blob),None)
    identity={"brand_match":brand,"style_match":style,"target_colour_match":target,"wrong_colour_match":wrong}
    if pt!="PRODUCT_PAGE":
        role,allowed,reason="DISCOVERY_ONLY",False,"NON_PRODUCT_PAGE"
    elif not style:
        role,allowed,reason="REJECT",False,"STYLE_MISMATCH"
    elif wrong and not target:
        role,allowed,reason="SAME_MODEL_WRONG_COLOUR",False,"COLOUR_MISMATCH"
    elif brand and target:
        role,allowed,reason="EXACT_PRODUCT",True,"EXACT_STYLE_COLOUR"
    else:
        role,allowed,reason="REVIEW_REQUIRED",False,"TARGET_COLOUR_NOT_PROVEN"
    return {"page_type":pt,"identity":identity,"evidence_role":role,
            "commercial_allowed":allowed,"reason":reason}

def dedupe(rows):
    out={}
    rank={"EXACT_PRODUCT":5,"SAME_MODEL_WRONG_COLOUR":4,"REVIEW_REQUIRED":3,
          "DISCOVERY_ONLY":2,"REJECT":1}
    for row in rows:
        u=canonical_url(row["source_url"]); x=dict(row); x["canonical_url"]=u
        if u not in out or rank.get(x.get("evidence_role"),0)>rank.get(out[u].get("evidence_role"),0):
            out[u]=x
    return list(out.values())
