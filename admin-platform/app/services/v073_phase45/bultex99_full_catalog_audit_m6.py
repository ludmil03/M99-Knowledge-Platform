from __future__ import annotations
# M99 BULTEX99 FULL CATALOG READ-ONLY AUDIT M6
import csv,json,sys,time
from pathlib import Path
from urllib.parse import urlparse,parse_qsl,urlencode,urlunparse
from app.services.v073_phase45 import bultex99_native_source_channel as m

def page_url(base,page):
 p=urlparse(base);q=dict(parse_qsl(p.query));q["page"]=str(page)
 return urlunparse((p.scheme,p.netloc,p.path,p.params,urlencode(q),p.fragment))

def run(out_dir:Path):
 out_dir.mkdir(parents=True,exist_ok=True)
 ch=m.Bultex99NativeSourceChannel()
 cats=ch.list_categories()
 if not cats:raise RuntimeError("NO_CATEGORIES")
 rows=[];seen_cat=set();total_products=0;blocked=0;missing_images=0
 for ci,c in enumerate(cats,1):
  if c.url in seen_cat:continue
  seen_cat.add(c.url);seen_products=set();page=1
  while page<=200:
   h=m._get(page_url(c.url,page))
   cards=m._product_cards(h)
   fresh=[x for x in cards if x[1] not in seen_products]
   if not fresh:break
   for name,url,img in fresh:
    seen_products.add(url);state,reason=m._category_integrity(c.label,c.url,name)
    if m._pure_colour(name):state,reason="VARIANT","COLOR_ONLY"
    if not img:missing_images+=1
    if state not in ("VALID","VARIANT"):blocked+=1
    rows.append({"category":c.label,"category_url":c.url,"profile":m._category_profile(c.label,c.url),"product":name,"product_url":url,"product_id":m._source_key(url),"state":state,"reason":reason,"card_image":img or "MISSING"})
   page+=1
  total_products+=len(seen_products)
  print(f"[CATALOG {ci}/{len(cats)}] {c.label}: {len(seen_products)} unique product cards")
 if not rows:raise RuntimeError("FULL_CATALOG_EMPTY: collections discovered but product-card discovery returned zero rows")
 fields=list(rows[0])
 with (out_dir/"bultex99_full_catalog_integrity_m6.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 summary={"categories":len(seen_cat),"unique_category_product_memberships":len(rows),"products_scanned_sum":total_products,"blocked_or_ambiguous":blocked,"missing_card_images":missing_images,"status":"PASS" if blocked==0 and missing_images==0 else "REVIEW_REQUIRED"}
 (out_dir/"bultex99_full_catalog_integrity_m6.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print("[FULL CATALOG SUMMARY]",json.dumps(summary,ensure_ascii=False))
 return 0 if summary["status"]=="PASS" else 3
if __name__=="__main__":raise SystemExit(run(Path(sys.argv[1]) if len(sys.argv)>1 else Path("output/m6_catalog_audit")))
