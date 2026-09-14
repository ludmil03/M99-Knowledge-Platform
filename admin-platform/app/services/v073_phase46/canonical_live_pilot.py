from __future__ import annotations
import json, os, re, uuid, xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from xml.sax.saxutils import escape
from app.services.v073_phase46.secure_integration_settings import effective_m99eu_credentials

ENABLE_ENV="M99EU_CANONICAL_PILOT_ENABLED"
API_KEY_ENV="M99EU_API_KEY"
CONFIRMATION="PUBLISH CANONICAL PILOT TO M99.EU"
REQUIRED_LANGS=("EN","BG","RU")
M99_RE=re.compile(r"^(?:M99 [0-9]{6}|M99-[0-9]+)$")

class CanonicalPilotError(RuntimeError):pass

@dataclass(frozen=True)
class CanonicalPilotResult:
    created:bool
    product_id:str
    reference:str
    active:str
    available_for_order:str
    visibility:str
    category_id:str
    http_status:str
    correlation_id:str
    price:str
    languages:tuple[str,...]
    image_upload_status:str="NOT_IN_R7D_PILOT"
    api_truth_verified:bool=False
    truth_summary:str=""

def _money(raw:Any)->str:
    s=str(raw or "").strip().replace(",",".")
    try:v=Decimal(s)
    except (InvalidOperation,ValueError):return ""
    return f"{v:.2f}" if v>0 else ""

def _safe_cdata(v:Any)->str:return str(v or "").replace("]]>","]]]]><![CDATA[>")
def _slug(text:str,fallback:str)->str:
    s=re.sub(r"[^a-z0-9]+","-",str(text or "").lower()).strip("-")
    return (s[:120] or fallback.lower())

def validate_preview(preview:dict)->None:
    if not preview or not preview.get("ready") or preview.get("status")!="READY":
        raise CanonicalPilotError("Canonical Payload Preview is not READY.")
    ids=preview.get("identifiers") or {}
    ref=str(ids.get("channel_reference") or "")
    if not M99_RE.fullmatch(ref):raise CanonicalPilotError("Permanent M99 channel reference is missing or invalid.")
    if ids.get("channel_reference_role")!="PERMANENT_M99_REFERENCE":raise CanonicalPilotError("Channel reference role contract failed.")
    if ids.get("supplier_reference_role")!="SUPPLIER_MAPPING_ONLY":raise CanonicalPilotError("Supplier reference role contract failed.")
    if ids.get("manufacturer_reference_role")!="VERIFIED_MANUFACTURER_MPN_ONLY":raise CanonicalPilotError("Manufacturer MPN role contract failed.")
    mref=str(ids.get("manufacturer_reference") or "").strip()
    if not mref:raise CanonicalPilotError("Verified Manufacturer MPN is missing.")
    docs=preview.get("languages") or {}
    miss=[x for x in REQUIRED_LANGS if x not in docs]
    if miss:raise CanonicalPilotError("Missing canonical languages: "+", ".join(miss))
    for code in REQUIRED_LANGS:
        d=docs.get(code) or {}
        for key in ("product_name","h1","short_description","long_description_html","meta_title","meta_description"):
            if not str(d.get(key) or "").strip():raise CanonicalPilotError(f"{code} canonical field missing: {key}")
        if str(d.get("manufacturer_reference_in_specs") or "").strip()!=mref:
            raise CanonicalPilotError(f"{code} Manufacturer MPN not represented in specs.")
    if int((preview.get("images") or {}).get("count") or 0)<=0:raise CanonicalPilotError("Canonical image evidence is missing.")
    if int((preview.get("variants") or {}).get("rows_count") or 0)<=0:raise CanonicalPilotError("Variant/availability evidence is missing.")

def _lang_xml(field:str,active:list[tuple[str,str]],docs:dict,selector,default_code="EN")->str:
    parts=[f"<{field}>"]
    for lid,iso in active:
        code=str(iso).upper()
        doc=docs.get(code) or docs.get(default_code) or {}
        value=selector(doc,code)
        parts.append(f'<language id="{escape(str(lid))}"><![CDATA[{_safe_cdata(value)}]]></language>')
    parts.append(f"</{field}>")
    return "".join(parts)

def build_canonical_product_xml(preview:dict,price:str,category_id:int,active:list[tuple[str,str]],supported:set[str]|None=None)->str:
    validate_preview(preview)
    p=_money(price)
    if not p:raise CanonicalPilotError("Explicit pilot price must be positive.")
    if int(category_id)<=0:raise CanonicalPilotError("Category ID must be positive.")
    active_isos={iso.lower() for _,iso in active}
    if not {"en","bg","ru"}.issubset(active_isos):raise CanonicalPilotError("m99.eu must expose active EN/BG/RU languages for this pilot.")
    ids=preview["identifiers"];docs=preview["languages"];ref=ids["channel_reference"];sref=str(ids.get("supplier_reference") or "");mpn=str(ids.get("manufacturer_reference") or "")
    supported=supported or {"active","available_for_order","show_price","price","reference","supplier_reference","mpn","id_category_default","visibility","name","description_short","description","meta_title","meta_description","link_rewrite","associations"}
    pieces=['<?xml version="1.0" encoding="UTF-8"?>','<prestashop xmlns:xlink="http://www.w3.org/1999/xlink"><product>']
    def tag(name,val):
        if name in supported:pieces.append(f'<{name}><![CDATA[{_safe_cdata(val)}]]></{name}>')
    tag("active","0");tag("available_for_order","0");tag("show_price","1");tag("visibility","none");tag("price",p);tag("reference",ref);tag("supplier_reference",sref)
    if mpn and "mpn" in supported:tag("mpn",mpn)
    tag("id_category_default",str(category_id))
    if "name" in supported:pieces.append(_lang_xml("name",active,docs,lambda d,c:d.get("product_name") or d.get("h1") or ref))
    if "description_short" in supported:pieces.append(_lang_xml("description_short",active,docs,lambda d,c:d.get("short_description") or ""))
    if "description" in supported:pieces.append(_lang_xml("description",active,docs,lambda d,c:d.get("long_description_html") or ""))
    if "meta_title" in supported:pieces.append(_lang_xml("meta_title",active,docs,lambda d,c:d.get("meta_title") or d.get("product_name") or ref))
    if "meta_description" in supported:pieces.append(_lang_xml("meta_description",active,docs,lambda d,c:d.get("meta_description") or ""))
    if "link_rewrite" in supported:pieces.append(_lang_xml("link_rewrite",active,docs,lambda d,c:_slug(d.get("product_name") or d.get("h1") or ref,ref)))
    if "associations" in supported:pieces.append(f'<associations><categories><category><id><![CDATA[{int(category_id)}]]></id></category></categories></associations>')
    pieces.append('</product></prestashop>');return "".join(pieces)

def _schema_fields(api_key:str)->set[str]:
    from app.services.v073_phase45.m99eu_operator_single_publish import _curl
    status,content=_curl(api_key,"/api/products?schema=blank")
    if status!="200":raise CanonicalPilotError(f"Product blank schema read failed HTTP {status}.")
    try:root=ET.fromstring(content)
    except ET.ParseError as exc:raise CanonicalPilotError("Product blank schema returned invalid XML.") from exc
    p=root.find(".//product")
    if p is None:raise CanonicalPilotError("Product blank schema has no product node.")
    return {str(c.tag).split("}")[-1] for c in list(p)}

def _readback(api_key:str,product_id:str)->dict:
    from app.services.v073_phase45.m99eu_operator_single_publish import _curl
    status,content=_curl(api_key,f"/api/products/{int(product_id)}")
    if status!="200":raise CanonicalPilotError(f"Readback failed HTTP {status}.")
    root=ET.fromstring(content);p=root.find(".//product")
    if p is None:raise CanonicalPilotError("Readback has no product node.")
    def txt(tag):
        n=p.find(tag);return (n.text or "").strip() if n is not None else ""
    return {k:txt(k) for k in ("reference","supplier_reference","mpn","active","available_for_order","visibility","id_category_default","price")}

def publish_canonical_pilot(db,*,user,job,item,preview:dict,category_id:int,price_override:str,confirmation:str)->CanonicalPilotResult:
    if not bool(getattr(user,"is_superuser",False)):raise CanonicalPilotError("Super Admin only.")
    if str(confirmation or "").strip()!=CONFIRMATION:raise CanonicalPilotError(f"Exact confirmation required: {CONFIRMATION}")
    enabled,api_key,credential_source=effective_m99eu_credentials()
    if not enabled:raise CanonicalPilotError("m99.eu publishing is disabled in M99 → Integration Settings.")
    if not re.fullmatch(r"[A-Za-z0-9]{32}",api_key):raise CanonicalPilotError("m99.eu API key is not configured or cannot be decrypted. Open M99 → Integration Settings.")
    if str(getattr(job,"status","")).upper()!="DRAFT":raise CanonicalPilotError("Job must remain DRAFT for first pilot.")
    validate_preview(preview)
    if int(preview.get("job_id") or 0)!=int(job.id) or int(preview.get("item_id") or 0)!=int(item.id):raise CanonicalPilotError("Preview/job/item mismatch.")
    try:
        requested=set(json.loads(getattr(job,"requested_targets","[]") or "[]"));authorized=set(json.loads(getattr(job,"authorized_targets","[]") or "[]"))
    except Exception as exc:raise CanonicalPilotError("Job target metadata invalid.") from exc
    if "m99eu" not in requested or "m99eu" not in authorized:raise CanonicalPilotError("Job is not requested+authorized for m99.eu.")
    p=_money(price_override)
    if not p:raise CanonicalPilotError("Enter an explicit positive pilot price.")
    from app.services.v073_phase45.m99eu_operator_single_publish import _curl,_find_existing,active_languages,ensure_category
    ensure_category(api_key,int(category_id));active=active_languages(api_key)
    fields=_schema_fields(api_key)
    ref=preview["identifiers"]["channel_reference"]
    existing=_find_existing(api_key,ref);corr=uuid.uuid4().hex
    if existing:
        state=_readback(api_key,existing)
        if state["reference"]!=ref or state["active"]!="0" or state["available_for_order"]!="0" or state["visibility"]!="none" or state["id_category_default"]!=str(category_id):
            raise CanonicalPilotError("Duplicate guard found an existing product that is not the exact safe hidden pilot state.")
        created=False;pid=str(existing);http="EXISTING_SAFE_HIDDEN_PILOT"
    else:
        xml=build_canonical_product_xml(preview,p,int(category_id),active,fields)
        status,content=_curl(api_key,"/api/products",method="POST",body=xml)
        if status not in ("200","201"):
            snippet=re.sub(r"\s+"," ",content)[:600];raise CanonicalPilotError(f"PrestaShop create rejected HTTP {status}: {snippet}")
        pid=_find_existing(api_key,ref)
        if not pid:raise CanonicalPilotError("POST succeeded but canonical product ID was not recovered by reference.")
        created=True;http=status
    state=_readback(api_key,pid)
    expected={"reference":ref,"active":"0","available_for_order":"0","visibility":"none","id_category_default":str(category_id)}
    for k,v in expected.items():
        if state.get(k)!=v:raise CanonicalPilotError(f"Readback mismatch {k}: expected {v!r}, got {state.get(k)!r}")
    mref=str(preview["identifiers"].get("manufacturer_reference") or "")
    if "mpn" in fields and mref and state.get("mpn")!=mref:raise CanonicalPilotError("Readback Manufacturer MPN mismatch.")
    from app.services.v073_phase46.live_product_truth_verifier import verify_product_truth
    truth=verify_product_truth(api_key,product_id=pid,reference=ref,expected_category_id=category_id,expected_price=p,require_hidden=True)
    truth_summary="; ".join(truth.blockers) if truth.blockers else ", ".join(truth.evidence)
    from app.models.entities import AuditLog
    details={"canonical_reference":ref,"supplier_reference":preview["identifiers"].get("supplier_reference") or "","manufacturer_mpn":mref,"channel_product_id":str(pid),"category_id":str(category_id),"price":p,"price_source":"OPERATOR_EXPLICIT_PILOT_PRICE","created":created,"active":"0","available_for_order":"0","visibility":"none","languages":[iso for _,iso in active],"image_upload_status":"NOT_IN_R7D_PILOT","correlation_id":corr,"credential_source":credential_source,"secret_logged":False,"api_truth_verified":truth.verified,"truth_evidence":list(truth.evidence),"truth_blockers":list(truth.blockers),"id_shop_default":truth.id_shop_default}
    audit_result="OK" if truth.verified else "NOT_VERIFIED"
    db.add(AuditLog(user_id=int(user.id),action="PHASE46_R7G_CANONICAL_PILOT_TRUTH_M99EU",entity_type="ImportJob",entity_id=str(job.id),result=audit_result,details=json.dumps(details,ensure_ascii=False,sort_keys=True)));db.commit()
    return CanonicalPilotResult(created,str(pid),ref,state["active"],state["available_for_order"],state["visibility"],state["id_category_default"],str(http),corr,p,tuple(iso for _,iso in active),api_truth_verified=truth.verified,truth_summary=truth_summary)
