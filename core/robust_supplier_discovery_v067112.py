import re
from html import unescape
from urllib.parse import quote,urljoin,urlparse
from datetime import datetime,timezone
import requests
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/150 Safari/537.36"}
ALIASES=("WWE601","WW601","CK-WW601","CKWW601")
COLOURS=("dark blue","navy","тъмно син","тъмносин")
def now(): return datetime.now(timezone.utc).isoformat()
def norm(v): return re.sub(r"[^a-z0-9а-я]+","",str(v or "").lower())
def clean(v): return re.sub(r"\s+"," ",unescape(str(v or ""))).strip()
def fetch(url,timeout=30):
 r=requests.get(url,headers=UA,timeout=timeout,allow_redirects=True); r.raise_for_status()
 return {"url":r.url,"html":r.text,"status":r.status_code,"observed_at_utc":now()}
def links(html,base,domain):
 out=[]
 for raw in re.findall("href\\s*=\\s*[\"']([^\"']+)",html,re.I):
  u=urljoin(base,unescape(raw))
  if domain in urlparse(u).netloc and u not in out: out.append(u)
 return out
def relevant(v): return any(norm(a) in norm(v) for a in ALIASES)
def discover_stenso():
 found=[]; attempts=[]; domain="stenso.net"
 known="https://stenso.net/produkt/medicinski-tuniki/4443-damska-medicinska-tunika-cherokee-v-neck-navy-wwe601"
 for url,method in [(known,"DIRECT_KNOWN_URL"),("https://stenso.net/search?controller=search&s="+quote("Cherokee WWE601"),"SUPPLIER_INTERNAL_SEARCH"),("https://stenso.net/39-medicinski-tuniki","SUPPLIER_CATEGORY_SCAN")]:
  try:
   x=fetch(url); attempts.append({"method":method,"url":x["url"],"ok":True})
   if relevant(x["url"]+" "+x["html"]) and not any(y["url"]==x["url"] for y in found): found.append({"url":x["url"],"method":method})
   for u in links(x["html"],x["url"],domain):
    if relevant(u) and not any(y["url"]==u for y in found): found.append({"url":u,"method":method})
  except Exception as e: attempts.append({"method":method,"url":url,"ok":False,"error":str(e)[:200]})
 return {"supplier":"Stenso","candidates":found,"attempts":attempts}
def discover_palltex():
 found=[]; attempts=[]; domain="palltex.bg"
 for url in ["https://palltex.bg/bg/cat?brand%5B4291%5D=4291","https://palltex.bg/en/cat?brand%5B4291%5D=4291"]:
  try:
   x=fetch(url); attempts.append({"method":"SUPPLIER_CATEGORY_SCAN","url":x["url"],"ok":True})
   for u in links(x["html"],x["url"],domain):
    if relevant(u) and not any(y["url"]==u for y in found): found.append({"url":u,"method":"SUPPLIER_CATEGORY_SCAN"})
  except Exception as e: attempts.append({"method":"SUPPLIER_CATEGORY_SCAN","url":url,"ok":False,"error":str(e)[:200]})
 return {"supplier":"Palltex","candidates":found,"attempts":attempts}
def textify(h):
 h=re.sub(r"<script\\b[^>]*>.*?</script>"," ",h,flags=re.I|re.S); h=re.sub(r"<style\\b[^>]*>.*?</style>"," ",h,flags=re.I|re.S)
 return clean(re.sub(r"<[^>]+>"," ",h))
def extract(supplier,c):
 x=fetch(c["url"]); t=textify(x["html"]); title=None
 m=re.search(r"<h1\\b[^>]*>(.*?)</h1>",x["html"],re.I|re.S)
 if m:title=textify(m.group(1))
 ref=None
 for pat in [r"(?:Арт\.?\s*№|Item code|Reference|SKU)\s*:?\s*([A-Za-z0-9._/-]{4,30})",r"\b(0[0-9]{7})\b"]:
  m=re.search(pat,t,re.I)
  if m:ref=m.group(1);break
 prices=[]
 for pat,curr in [(r"(\d+[.,]\d{1,2})\s*(?:лв\.?|BGN)","BGN"),(r"(\d+[.,]\d{1,2})\s*(?:€|EUR)","EUR")]:
  for val in re.findall(pat,t,re.I)[:10]:
   try:
    z={"value":float(val.replace(",",".")),"currency":curr}
    if z not in prices:prices.append(z)
   except:pass
 low=t.lower()
 stock="OUT_OF_STOCK" if any(q in low for q in ["няма наличност","out of stock","изчерпан"]) else ("IN_STOCK" if any(q in low for q in ["в наличност","in stock","последна наличност","last items in stock"]) else None)
 sizes=[s for s in ["2XS","XS","S","M","L","XL","2XL","3XL","4XL","5XL"] if re.search(r"(?<![A-Za-z0-9])"+re.escape(s)+r"(?![A-Za-z0-9])",t,re.I)]
 blob=norm((title or "")+" "+t[:6000]); style=next((a for a in ALIASES if norm(a) in blob),None); colour=next((q for q in COLOURS if norm(q) in blob),None); brand="cherokee" in blob
 cls,score=("EXACT",100) if brand and style and colour else (("VERY_STRONG",85) if brand and style else (("NEAR_MATCH",50) if style else ("REJECT",0)))
 return {"supplier":supplier,"source_url":x["url"],"discovery_method":c["method"],"title":title,"supplier_reference":ref,"identity":{"class":cls,"score":score,"style":style,"colour":colour},"raw_price_observations":prices,"availability":stock,"sizes":sizes,"commercial_quarantined":cls not in ("EXACT","VERY_STRONG"),"observed_at_utc":x["observed_at_utc"]}
def run(d):
 rows=[];errors=[]
 for c in d["candidates"]:
  try:rows.append(extract(d["supplier"],c))
  except Exception as e:errors.append({"url":c["url"],"error":str(e)[:300]})
 rows.sort(key=lambda x:x["identity"]["score"],reverse=True); return {**d,"pages":rows,"errors":errors}
def merge(a,b):
 elig={s["supplier"]:[x for x in s["pages"] if not x["commercial_quarantined"]] for s in [a,b]}
 return {"supplier_eligible":elig,"supplier_evidence_present":any(elig.values()),"policy":{"manufacturer_identity_required":True,"prices_separate":True,"stock_separate":True,"m99_selling_price":None}}
