from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re, html, json, datetime

PRODUCTS = [
    31940, 36127, 31869, 35140, 40951, 2196, 42577, 50133,
    31945, 31933, 31927, 34418, 31880,
]

def clean(s):
    s=re.sub(r"<script\b[^>]*>.*?</script>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<style\b[^>]*>.*?</style>"," ",s,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",html.unescape(s)).strip()

def extract(txt,pid):
    text=clean(txt)
    brand=""
    m=re.search(r"Марка\s*:\s*([A-ZА-Я0-9 '&+./_-]{2,80})",text,re.I)
    if m:brand=m.group(1).strip()
    code=""
    m=re.search(r"(?:КОД|Код)\s*:\s*([A-Z0-9][A-Z0-9./_-]{1,40})",text)
    if m:code=m.group(1).strip()
    title=""
    mt=re.search(r"<h1[^>]*>(.*?)</h1>",txt,re.I|re.S)
    if mt:title=clean(mt.group(1))
    if not title:
        title=text[:160]
    colors=sorted(set(re.findall(r"\b(?:White|Navy|Black|Red|Green|Yellow|Orange|Blue|Royal Blue|Bright Yellow|ЧЕРЕН|БЯЛ|ЧЕРВЕН|ЗЕЛЕН|СИН|ЖЪЛТ|ОРАНЖЕВ|ЛИЛАВ)\b",text,re.I)))
    return {"product_id":str(pid),"title":title,"brand":brand,"page_code_candidate":code,"colors":colors[:30]}

def main():
    rows=[]
    for pid in PRODUCTS:
        url=f"https://calenda.bg/products/{pid}"
        try:
            req=Request(url,headers={"User-Agent":"Mozilla/5.0 M99-R7A-ReadOnly-Probe/1.0"})
            with urlopen(req,timeout=15) as r:
                raw=r.read().decode("utf-8","replace")
            row=extract(raw,pid);row["url"]=url;row["http_status"]=200
        except Exception as exc:
            row={"product_id":str(pid),"url":url,"error":type(exc).__name__+": "+str(exc)}
        rows.append(row)
        print(row)
    out=Path.home()/"Desktop"/("M99_CALENDA_R7A_READONLY_MATRIX_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".json")
    out.write_text(json.dumps({"read_only":True,"products":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print("[REPORT]",out)
    print("[DONE] READ-ONLY GET probe; no login, no cart, no write.")
if __name__=="__main__":
    main()
