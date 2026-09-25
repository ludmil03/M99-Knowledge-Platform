from __future__ import annotations
import base64
from urllib.request import Request as UrlRequest, urlopen
from urllib.error import HTTPError
from xml.etree import ElementTree as ET
PRODUCT_ID=2041
REFERENCE="M99 100018"
def _auth(key): return "Basic "+base64.b64encode((key+":").encode()).decode()
def _request(url,key,method="GET",body=None,content_type="application/xml"):
    h={"Authorization":_auth(key),"Accept":"application/xml"}
    if body is not None:h["Content-Type"]=content_type
    req=UrlRequest(url,data=body,headers=h,method=method)
    try:
        with urlopen(req,timeout=25) as r:return int(getattr(r,"status",200)),r.read()
    except HTTPError as e:return int(e.code),e.read()
def _txt(root,path):
    n=root.find(path);return (n.text or "").strip() if n is not None else ""
def _langs(node):
    if node is None:return {}
    return {str(x.attrib.get("id","")):(x.text or "") for x in node.findall("language")}
def _set_langs(node,values):
    if node is None:return
    for x in node.findall("language"):
        lid=str(x.attrib.get("id",""))
        if lid in values:x.text=str(values[lid])
def build_safe_update_xml(current_xml,canonical):
    root=ET.fromstring(current_xml);p=root.find("product") if root.tag!="product" else root
    if p is None:raise RuntimeError("PRODUCT_XML_MISSING")
    if _txt(p,"id")!=str(PRODUCT_ID):raise RuntimeError("PRODUCT_IDENTITY_ID_MISMATCH")
    if _txt(p,"reference").replace(" ","")!="M99100018":raise RuntimeError("PRODUCT_IDENTITY_REFERENCE_MISMATCH")
    for field,value in (("active","0"),("available_for_order","0"),("visibility","none")):
        n=p.find(field)
        if n is None:raise RuntimeError("MISSING_SAFETY_FIELD_"+field.upper())
        n.text=value
    docs=dict(canonical.get("languages") or {});mapping={"1":"bg","2":"en"}
    fields={"name":"product_name","description_short":"short_description","description":"long_description_html","meta_title":"meta_title","meta_description":"meta_description"}
    for xmlfield,ckey in fields.items():
        n=p.find(xmlfield);existing=_langs(n);changes={}
        for lid,code in mapping.items():
            val=str((docs.get(code) or {}).get(ckey) or "").strip()
            if val and lid in existing:changes[lid]=val
        _set_langs(n,changes)
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)
def validate_post_readback(xml):
    root=ET.fromstring(xml);p=root.find("product") if root.tag!="product" else root;b=[]
    if p is None:return False,["PRODUCT_XML_MISSING"]
    if _txt(p,"id")!=str(PRODUCT_ID):b.append("ID_MISMATCH")
    if _txt(p,"reference").replace(" ","")!="M99100018":b.append("REFERENCE_MISMATCH")
    if _txt(p,"active") not in ("0",""):b.append("ACTIVE_NOT_ZERO")
    if _txt(p,"available_for_order") not in ("0",""):b.append("ORDERABLE_NOT_ZERO")
    if _txt(p,"visibility") not in ("none",""):b.append("VISIBILITY_NOT_NONE")
    return not b,b
def controlled_update(base,key,canonical,transport=_request):
    if not canonical.get("ready"):return {"status":"BLOCKED","write":False,"blockers":["CANONICAL_NOT_READY"]}
    url=base.rstrip("/")+"/api/products/2041"
    s,b=transport(url,key,"GET",None)
    if s!=200:return {"status":"BLOCKED","write":False,"blockers":["PREWRITE_GET_HTTP_"+str(s)]}
    try:payload=build_safe_update_xml(b,canonical)
    except Exception as e:return {"status":"BLOCKED","write":False,"blockers":[str(e)]}
    s2,b2=transport(url,key,"PUT",payload)
    if s2 not in (200,201):return {"status":"FAILED","write":True,"blockers":["PUT_HTTP_"+str(s2)]}
    s3,b3=transport(url,key,"GET",None)
    if s3!=200:return {"status":"FAILED","write":True,"blockers":["READBACK_HTTP_"+str(s3)]}
    ok,blockers=validate_post_readback(b3)
    return {"status":"SUCCESS" if ok else "FAILED","write":True,"readback":ok,"blockers":blockers,"mode":"UPDATE_EXISTING_2041","reference":REFERENCE}
