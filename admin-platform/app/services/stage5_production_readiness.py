from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import re, xml.etree.ElementTree as ET
from urllib.parse import urlencode
from app.services.stage5_final_ui_publish import _get_once, FinalPublishBlocked

RID=re.compile(r"^M99 ([0-9]{6})$")
LANGS=("en","bg","ru")

@dataclass(frozen=True)
class ProductionReadiness:
    ready: bool
    blockers: tuple[str,...]
    language_map: dict[str,int]
    blank_schema_fields: tuple[str,...]
    tax_rules_group_id: int|None
    vat_rate: str|None
    next_reference: str|None
    price_semantics: str
    publish_enabled: bool=False
    write_allowed: bool=False
    write_performed: bool=False

def gross_to_net(gross,vat_rate):
    g=Decimal(str(gross)); v=Decimal(str(vat_rate))
    if g<=0 or v<0: raise ValueError("INVALID_PRICE_OR_VAT")
    return (g/(Decimal("1")+v)).quantize(Decimal("0.000001"),rounding=ROUND_HALF_UP)

def _xml(text):
    try:return ET.fromstring(text)
    except ET.ParseError as e:raise FinalPublishBlocked("INVALID_XML_READBACK") from e

def _language_map(cfg):
    root=_xml(_get_once(cfg,"/api/languages",{"display":"[id,iso_code,active]"}))
    found={}
    for row in root.findall(".//language"):
        iso=(row.findtext("iso_code") or "").strip().lower()
        active=(row.findtext("active") or "1").strip()
        rid=(row.findtext("id") or row.attrib.get("id") or "").strip()
        if iso in LANGS and active!="0" and rid.isdigit(): found[iso]=int(rid)
    if set(found)!=set(LANGS):raise FinalPublishBlocked("MANDATORY_LANGUAGE_MAP_UNPROVEN")
    if len(set(found.values()))!=3:raise FinalPublishBlocked("LANGUAGE_ID_COLLISION")
    return found

def _blank_schema(cfg):
    root=_xml(_get_once(cfg,"/api/products",{"schema":"blank"}))
    product=root.find(".//product")
    if product is None:raise FinalPublishBlocked("BLANK_PRODUCT_SCHEMA_UNPROVEN")
    fields=tuple(sorted({c.tag for c in product}))
    required={"id_category_default","price","reference","name","description","description_short","meta_title","meta_description"}
    if not required.issubset(fields):raise FinalPublishBlocked("BLANK_PRODUCT_SCHEMA_REQUIRED_FIELDS_MISSING")
    return fields

def _used_references(cfg,floor=100019,window=500):
    # Read-only bounded scan. No allocation is persisted here.
    root=_xml(_get_once(cfg,"/api/products",{"display":"[id,reference]","filter[reference]":"[M99%]"}))
    used=set()
    for row in root.findall(".//product"):
        ref=(row.findtext("reference") or "").strip()
        m=RID.fullmatch(ref)
        if m:used.add(int(m.group(1)))
    for n in range(floor,floor+window):
        if n not in used:return f"M99 {n:06d}"
    raise FinalPublishBlocked("M99_ID_ALLOCATION_WINDOW_EXHAUSTED")

def _tax_proof(cfg):
    # Operator rate is authoritative for M99 calculations; never guess tax-group identity.
    from app.services.operator_vat_settings import get_setting
    setting=get_setting("m99.eu")
    if setting is None: raise FinalPublishBlocked("OPERATOR_VAT_NOT_CONFIGURED")
    rate=Decimal(setting["vat_percent"])
    gid=setting["tax_group_id"]
    if gid is None: raise FinalPublishBlocked("PRESTASHOP_TAX_GROUP_ID_NOT_CONFIGURED")
    # Read-only check: tax rules for this exact group must resolve to one rate.
    rr=_xml(_get_once(cfg,"/api/tax_rules",{"display":"full","filter[id_tax_rules_group]":f"[{gid}]"}))
    rates=set(); matching=0
    for row in rr.findall(".//tax_rule"):
        row_group=(row.findtext("id_tax_rules_group") or "").strip()
        if row_group and row_group!=str(gid):continue
        tax_id=(row.findtext("id_tax") or "").strip()
        if not tax_id.isdigit():continue
        matching+=1
        tx=_xml(_get_once(cfg,f"/api/taxes/{tax_id}"))
        actual=(tx.findtext(".//tax/rate") or "").strip()
        if not actual:raise FinalPublishBlocked("TAX_RATE_MISSING")
        rates.add(Decimal(actual))
    if matching==0 or rates!={rate}:
        raise FinalPublishBlocked("OPERATOR_VAT_MISMATCH_WITH_PRESTASHOP_TAX_RULES")
    return gid,rate/Decimal("100")

def run_production_readiness(cfg):
    blockers=[];lm={};fields=();gid=None;vat=None;ref=None
    for key,fn in (
        ("LANGUAGE",lambda:_language_map(cfg)),
        ("SCHEMA",lambda:_blank_schema(cfg)),
        ("IDENTITY",lambda:_used_references(cfg)),
        ("TAX",lambda:_tax_proof(cfg)),
    ):
        try:
            v=fn()
            if key=="LANGUAGE":lm=v
            elif key=="SCHEMA":fields=v
            elif key=="IDENTITY":ref=v
            else:gid,vat=v
        except Exception as exc:
            blockers.append(key+":"+str(exc))
    ready=not blockers
    return ProductionReadiness(
        ready,tuple(blockers),lm,fields,gid,
        None if vat is None else str(vat),ref,
        "M99_GROSS_VAT_INCLUDED__PS_BASE_PRICE_REQUIRES_GROSS_TO_NET",
        False,False,False
    )

def build_blank_create_xml(blank_xml,*,reference,category_id,net_price,tax_rules_group_id,language_map,content):
    root=_xml(blank_xml);p=root.find(".//product")
    if p is None:raise FinalPublishBlocked("BLANK_PRODUCT_SCHEMA_UNPROVEN")
    def set1(tag,val):
        e=p.find(tag)
        if e is None:raise FinalPublishBlocked("SCHEMA_FIELD_MISSING:"+tag)
        e.text=str(val)
    set1("reference",reference);set1("id_category_default",category_id)
    set1("price",net_price);set1("id_tax_rules_group",tax_rules_group_id)
    for tag in ("active","available_for_order"):
        e=p.find(tag)
        if e is not None:e.text="0"
    vis=p.find("visibility")
    if vis is not None:vis.text="none"
    for field in ("name","description_short","description","meta_title","meta_description"):
        parent=p.find(field)
        if parent is None:raise FinalPublishBlocked("SCHEMA_FIELD_MISSING:"+field)
        for old in list(parent):parent.remove(old)
        for lang in LANGS:
            data=content.get(lang) or {}
            key={"description":"long","description_short":"short"}.get(field,field)
            value=str(data.get(key,"")).strip()
            if not value:raise FinalPublishBlocked("CONTENT_INCOMPLETE:"+lang+":"+key)
            e=ET.SubElement(parent,"language",{"id":str(language_map[lang])});e.text=value
    return ET.tostring(root,encoding="unicode")
