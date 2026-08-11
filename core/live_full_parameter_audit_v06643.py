from collections import Counter
from html.parser import HTMLParser
import re, xml.etree.ElementTree as ET

class H(HTMLParser):
    def __init__(self):
        super().__init__(); self.headings=[]; self.buf=[]; self.tag=None; self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in {"h1","h2","h3","h4","h5","h6"}:
            self.tag=tag.lower(); self.buf=[]
    def handle_endtag(self,tag):
        if self.tag==tag.lower():
            self.headings.append({"tag":self.tag,"text":" ".join("".join(self.buf).split())})
            self.tag=None; self.buf=[]
    def handle_data(self,data):
        self.text.append(data)
        if self.tag: self.buf.append(data)

def analyze_html(html):
    p=H(); html=html or ""
    try:p.feed(html)
    except Exception:pass
    plain=" ".join(" ".join(p.text).split())
    words=re.findall(r"\b[\wÀ-ÿА-Яа-я0-9.-]+\b",plain,re.UNICODE)
    c=Counter(x["tag"] for x in p.headings)
    low=plain.casefold()
    return {"html_length":len(html),"plain_text_length":len(plain),"word_count":len(words),
            "headings":p.headings,"heading_counts":{k:c.get(k,0) for k in ["h1","h2","h3","h4"]},
            "faq_present":any(x in low for x in ["често задавани въпроси","frequently asked questions","faq"])}

def parse_product_xml(xml_text):
    root=ET.fromstring(xml_text); product=root.find(".//product")
    if product is None: raise ValueError("No product node")
    scalar={}; multilingual={}; associations={}
    for child in list(product):
        tag=child.tag.split("}",1)[-1]
        if tag=="associations": continue
        langs=child.findall(".//language")
        if langs:
            multilingual[tag]={str(x.attrib.get("id","")):(x.text or "").strip() for x in langs}
        elif list(child):
            scalar[tag]={x.tag.split("}",1)[-1]:(x.text or "").strip() for x in list(child)}
        else:
            scalar[tag]=(child.text or "").strip()
    ar=product.find("associations")
    if ar is not None:
        for col in list(ar):
            name=col.tag.split("}",1)[-1]; rows=[]
            for rec in list(col):
                item={f.tag.split("}",1)[-1]:(f.text or "").strip() for f in list(rec)}
                if not item and (rec.text or "").strip(): item["value"]=(rec.text or "").strip()
                rows.append(item)
            associations[name]=rows
    return {"scalar_fields":scalar,"multilingual_fields":multilingual,"associations":associations}

def translate_multilingual(snapshot,iso_to_id):
    out={}
    for field,values in snapshot["multilingual_fields"].items():
        out[field]={iso:values.get(lang_id,"") for iso,lang_id in iso_to_id.items()}
        out[field]["by_language_id"]=values
    return out

def content_seo_metrics(snapshot,iso_to_id):
    t=translate_multilingual(snapshot,iso_to_id); result={}
    for iso in ("bg","en"):
        d=t.get("description",{}).get(iso,""); s=t.get("description_short",{}).get(iso,"")
        dm=analyze_html(d)
        result[iso]={"name":t.get("name",{}).get(iso,""),"slug":t.get("link_rewrite",{}).get(iso,""),
                     "meta_title":t.get("meta_title",{}).get(iso,""),
                     "meta_title_length":len(t.get("meta_title",{}).get(iso,"")),
                     "meta_description":t.get("meta_description",{}).get(iso,""),
                     "meta_description_length":len(t.get("meta_description",{}).get(iso,"")),
                     "meta_keywords":t.get("meta_keywords",{}).get(iso,""),
                     "short_description":s,"short_description_metrics":analyze_html(s),
                     "description":d,"description_metrics":dm,
                     "has_h1":dm["heading_counts"]["h1"]>0,"has_h2":dm["heading_counts"]["h2"]>0,
                     "has_h3":dm["heading_counts"]["h3"]>0,"faq_present":dm["faq_present"]}
    return result

def diff_dicts(a,b,path=""):
    diffs=[]
    for k in sorted(set(a)|set(b)):
        av=a.get(k,"__MISSING__"); bv=b.get(k,"__MISSING__"); p=f"{path}.{k}" if path else k
        if isinstance(av,dict) and isinstance(bv,dict): diffs.extend(diff_dicts(av,bv,p))
        elif av!=bv: diffs.append({"path":p,"2076":av,"2100":bv,"status":"DIFFERENT"})
    return diffs

def quality_observations(a,b):
    out={}
    for iso in ("bg","en"):
        x=a.get(iso,{}); y=b.get(iso,{})
        out[iso]={
          "description_word_count":{"2076":x.get("description_metrics",{}).get("word_count",0),"2100":y.get("description_metrics",{}).get("word_count",0)},
          "h1":{"2076":x.get("has_h1",False),"2100":y.get("has_h1",False)},
          "h2":{"2076":x.get("has_h2",False),"2100":y.get("has_h2",False)},
          "h3":{"2076":x.get("has_h3",False),"2100":y.get("has_h3",False)},
          "faq":{"2076":x.get("faq_present",False),"2100":y.get("faq_present",False)},
          "meta_title_length":{"2076":x.get("meta_title_length",0),"2100":y.get("meta_title_length",0)},
          "meta_description_length":{"2076":x.get("meta_description_length",0),"2100":y.get("meta_description_length",0)}}
    return {"global_winner":None,"automatic_master_selection":False,"automatic_content_winner":False,"by_language":out}
