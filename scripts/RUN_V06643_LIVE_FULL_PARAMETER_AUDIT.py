from datetime import datetime, timezone
from pathlib import Path
import json, xml.etree.ElementTree as ET
from integrations.channel_publish import Mela99ClientConfig,ControlledMela99Publisher
from core.live_channel_metadata import parse_languages_xml
from core.live_full_parameter_audit_v06643 import parse_product_xml,translate_multilingual,content_seo_metrics,diff_dicts,quality_observations

ROOT=Path("."); OUT=ROOT/"output"/"v06643_live_2076_vs_2100"; OUT.mkdir(parents=True,exist_ok=True)
client=ControlledMela99Publisher(Mela99ClientConfig(base_url="https://mela99.com",api_key_env="M99_MELA99_API_KEY",timeout_seconds=30))
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
langs=parse_languages_xml(client.get_resource_xml("languages",{"display":"full"}))
if not langs.get("ready"): raise RuntimeError("BG/EN language mapping not ready")
iso={"bg":str(langs["bg_id"]),"en":str(langs["en_id"])}

x2076=client.get_product_xml("2076"); x2100=client.get_product_xml("2100")
(OUT/f"{ts}_2076.xml").write_text(x2076,encoding="utf-8")
(OUT/f"{ts}_2100.xml").write_text(x2100,encoding="utf-8")
p2076=parse_product_xml(x2076); p2100=parse_product_xml(x2100)
m2076=content_seo_metrics(p2076,iso); m2100=content_seo_metrics(p2100,iso)

def generic(xml):
    root=ET.fromstring(xml); resource=next(iter(root),None)
    if resource is None:return {}
    out={}
    for c in list(resource):
        tag=c.tag.split("}",1)[-1]
        langs=c.findall(".//language")
        if langs: out[tag]={str(x.attrib.get("id","")):(x.text or "").strip() for x in langs}
        elif list(c):
            rows=[]
            for sub in list(c):
                rows.append({f.tag.split("}",1)[-1]:(f.text or "").strip() for f in list(sub)})
            out[tag]=rows
        else: out[tag]=(c.text or "").strip()
    return out

def fetch_combos(pid,snap):
    arr=[]
    for rec in snap["associations"].get("combinations",[]):
        cid=str(rec.get("id") or "").strip()
        if not cid:continue
        try:
            xml=client.get_resource_xml(f"combinations/{cid}")
            (OUT/f"{ts}_{pid}_combination_{cid}.xml").write_text(xml,encoding="utf-8")
            arr.append({"id":cid,"status":"OK","fields":generic(xml)})
        except Exception as e:
            arr.append({"id":cid,"status":"ERROR","error":str(e)[:400]})
    return arr

c2076=fetch_combos("2076",p2076); c2100=fetch_combos("2100",p2100)
n2076={"scalar_fields":p2076["scalar_fields"],"multilingual":translate_multilingual(p2076,iso),"associations":p2076["associations"]}
n2100={"scalar_fields":p2100["scalar_fields"],"multilingual":translate_multilingual(p2100,iso),"associations":p2100["associations"]}
diffs=diff_dicts(n2076,n2100)

report={"schema_version":"0.6.6.4.3","mode":"LIVE_GET_ONLY_FULL_PARAMETER_AUDIT","generated_at_utc":ts,
"http_policy":"GET_ONLY","writes":{"channels":False,"dolibarr":False,"supplier":False},
"freshness":{"uses_prior_product_snapshot_for_values":False,"products_fetched_live_this_run":["2076","2100"]},
"live_languages":langs,
"product_2076":{"raw_snapshot":p2076,"multilingual_by_iso":translate_multilingual(p2076,iso),"content_seo_metrics":m2076,"combination_details_live":c2076},
"product_2100":{"raw_snapshot":p2100,"multilingual_by_iso":translate_multilingual(p2100,iso),"content_seo_metrics":m2100,"combination_details_live":c2100},
"field_differences":diffs,"objective_quality_observations":quality_observations(m2076,m2100),
"decision_policy":{"recommended_master":None,"content_winner":None,"seo_winner":None,"structure_winner":None,"image_winner":None,"combination_winner":None,"operator_review_required":True}}
jp=OUT/f"{ts}_FULL_PARAMETER_AUDIT_2076_VS_2100.json"; jp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def ac(s,k):return len(s["associations"].get(k,[]))
lines=["M99 v0.6.6.4.3 - LIVE 2076 vs 2100 FULL PARAMETER AUDIT","="*68,f"Generated UTC: {ts}","HTTP policy: GET ONLY","Prior product snapshots used for values: NO",f"Languages: BG={iso['bg']} EN={iso['en']}",""]
for pid,s,m,c in [("2076",p2076,m2076,c2076),("2100",p2100,m2100,c2100)]:
    lines += [f"PRODUCT {pid}","-"*40]
    for k in ["id","reference","ean13","upc","id_manufacturer","id_supplier","id_category_default","price","wholesale_price","id_tax_rules_group","active","visibility","condition","available_for_order","show_price","online_only","minimal_quantity","date_add","date_upd"]:
        if k in s["scalar_fields"]: lines.append(f"{k}: {s['scalar_fields'].get(k)}")
    lines += [f"categories: {ac(s,'categories')}",f"images: {ac(s,'images')}",f"combinations: {ac(s,'combinations')}",f"product_features: {ac(s,'product_features')}",f"tags: {ac(s,'tags')}",f"stock_availables: {ac(s,'stock_availables')}"]
    for lang in ("bg","en"):
        mm=m.get(lang,{}); dm=mm.get("description_metrics",{})
        lines.append(f"{lang.upper()} | name={mm.get('name')!r} | meta_title_len={mm.get('meta_title_length')} | meta_desc_len={mm.get('meta_description_length')} | description_words={dm.get('word_count')} | H1={dm.get('heading_counts',{}).get('h1')} H2={dm.get('heading_counts',{}).get('h2')} H3={dm.get('heading_counts',{}).get('h3')} | FAQ={mm.get('faq_present')}")
    lines += [f"live combination resources fetched: {len(c)}",""]
lines += [f"Different parameter paths: {len(diffs)}","Global winner: NOT SELECTED","WRITE ALLOWED: NO",f"JSON report: {jp}"]
sp=OUT/f"{ts}_SUMMARY_2076_VS_2100.txt"; sp.write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines)); print("Summary:",sp)
