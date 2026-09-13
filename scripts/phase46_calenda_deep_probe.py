from __future__ import annotations
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import re,html,json,datetime,hashlib

PRODUCTS=[31940,36127,31869,35140,40951,2196,42577,50133,31945,31933,31927,34418,31880]

def clean(s):
    s=re.sub(r"<script\\b[^>]*>.*?</script>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<style\\b[^>]*>.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\\s+"," ",html.unescape(s)).strip()

def image_urls(raw,base):
    vals=[]
    pats=[
      r"(?:src|data-src|data-original|href)\\s*=\\s*[\"']([^\"']+\\.(?:jpg|jpeg|png|webp)(?:\\?[^\"']*)?)[\"']",
      r"[\"'](?:image|image_url|imageUrl|src)[\"']\\s*:\\s*[\"']([^\"']+\\.(?:jpg|jpeg|png|webp)(?:\\?[^\"']*)?)[\"']",
    ]
    for pat in pats:
        for u in re.findall(pat,raw,re.I):
            u=html.unescape(u).replace("\\/","/")
            vals.append(urljoin(base,u))
    return list(dict.fromkeys(vals))

def script_excerpts(raw):
    out=[]
    for m in re.finditer(r"<script\\b[^>]*>(.*?)</script>",raw,re.I|re.S):
        body=m.group(1)
        low=body.casefold()
        if any(k in low for k in ("variant","colour","color","size","sku","product")):
            out.append(re.sub(r"\\s+"," ",body).strip()[:12000])
    return out[:12]

def contexts(text,terms,span=180):
    low=text.casefold();out=[]
    for term in terms:
        pos=0
        while True:
            i=low.find(term.casefold(),pos)
            if i<0:break
            out.append(text[max(0,i-span):min(len(text),i+len(term)+span)])
            pos=i+len(term)
            if len(out)>=40:return out
    return out

def extract(pid,raw,url):
    text=clean(raw)
    hm=re.search(r"<h1[^>]*>(.*?)</h1>",raw,re.I|re.S)
    return {
      "product_id":str(pid),
      "url":url,
      "html_sha256":hashlib.sha256(raw.encode("utf-8","replace")).hexdigest(),
      "html_chars":len(raw),
      "title":clean(hm.group(1)) if hm else "",
      "image_urls":image_urls(raw,url),
      "variant_script_excerpt":script_excerpts(raw),
      "code_contexts":contexts(text,["Код","SKU","ID","PUNT-"]),
      "brand_contexts":contexts(text,["Марка","Brand"]),
      "color_contexts":contexts(text,["White","Navy","Black","Red","СИН","ЧЕРЕН","БЯЛ","ЧЕРВЕН"]),
    }

def main():
    rows=[]
    for pid in PRODUCTS:
        url=f"https://calenda.bg/products/{pid}"
        try:
            req=Request(url,headers={"User-Agent":"Mozilla/5.0 M99-R7B-ReadOnly-Deep-Probe/1.0"})
            with urlopen(req,timeout=20) as r:
                raw=r.read().decode("utf-8","replace")
            row=extract(pid,raw,url);row["http_status"]=200
        except Exception as exc:
            row={"product_id":str(pid),"url":url,"error":type(exc).__name__+": "+str(exc)}
        rows.append(row)
        print(f"[{pid}] images={len(row.get('image_urls',[]))} scripts={len(row.get('variant_script_excerpt',[]))} error={row.get('error','')}")
    out=Path.home()/"Desktop"/("M99_CALENDA_R7B_DEEP_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".json")
    out.write_text(json.dumps({"read_only":True,"products":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print("[REPORT]",out)
    print("[DONE] READ-ONLY GET deep probe; no login/cart/write.")
if __name__=="__main__":
    main()
