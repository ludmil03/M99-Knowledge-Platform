from __future__ import annotations
from dataclasses import fields,is_dataclass,replace
from typing import Any
import re
from app.services.v073_phase46.calenda_evidence_governance import looks_like_unsafe_reference,known_variant_colors
from app.services.v073_phase46.calenda_supplier_reconciler import clean_supplier_brand,classify_calenda_page_code
SCHEMA="m99.phase46.r7c.calenda_runtime_governance.v1"
def _get(o,k,d=None):return o.get(k,d) if isinstance(o,dict) else getattr(o,k,d)
def _copy(o,**c):
    if isinstance(o,dict):x=dict(o);x.update(c);return x
    if is_dataclass(o):
        allowed={f.name for f in fields(o)};return replace(o,**{k:v for k,v in c.items() if k in allowed})
    return o
def _norm(v):return re.sub(r"\s+"," ",str(v or '').strip()).casefold()
def _variant_rows(o):
    out=[]
    for v in (_get(o,'variants',()) or ()):
        if isinstance(v,dict):out.append(dict(v))
        elif is_dataclass(v):out.append({f.name:getattr(v,f.name) for f in fields(v)})
        else:out.append({'value':getattr(v,'value',None),'code':getattr(v,'code',None),'source_variant_id':getattr(v,'source_variant_id',None),'url':getattr(v,'url',None),'image_url':getattr(v,'image_url',None),'sizes':getattr(v,'sizes',None)})
    return out
def _safe_ref(o):
    raw=str(_get(o,'supplier_reference','') or '').strip();colors=known_variant_colors(o)
    if not raw:return '', 'MISSING'
    if looks_like_unsafe_reference(raw,known_colors=colors):return '', 'REJECTED_COLOR_OR_SIZE_TOKEN'
    role=classify_calenda_page_code(raw)
    if role['role']=='CALENDA_CATALOG_CODE':return '', 'CALENDA_CATALOG_CODE_SEPARATE_ROLE'
    return role.get('safe_supplier_reference',''),role['role']
def _govern_images(rows):
    by={}
    for v in rows:
        img=str(v.get('image_url') or '').strip()
        if img:by.setdefault(img,set()).add(_norm(v.get('value') or v.get('code')))
    out=[];warnings=[]
    for v in rows:
        item=dict(v);img=str(item.get('image_url') or '').strip()
        if img and len(by.get(img,set()))>1:
            item['image_url']='';item['image_provenance']='SUPPLIER_GENERIC_SHARED_REJECTED_AS_VARIANT';item['image_association_exact']=False;warnings.append('VARIANT_SHARED_IMAGE_REMOVED_FROM_EXACT_COLOR_EVIDENCE')
        elif img:item['image_provenance']=item.get('image_provenance') or 'SUPPLIER_VARIANT_UNIQUE_CANDIDATE'
        else:item['image_provenance']=item.get('image_provenance') or 'NO_VARIANT_IMAGE_EVIDENCE'
        out.append(item)
    return out,list(dict.fromkeys(warnings))
def postprocess_calenda_hydrated(hydrated:Any)->Any:
    if hydrated is None:return hydrated
    ref,status=_safe_ref(hydrated);variants,image_warnings=_govern_images(_variant_rows(hydrated));warnings=list(_get(hydrated,'warnings',()) or ())
    if status=='REJECTED_COLOR_OR_SIZE_TOKEN':warnings.append('SUPPLIER_REFERENCE_REJECTED_COLOR_OR_SIZE_TOKEN')
    elif status=='CALENDA_CATALOG_CODE_SEPARATE_ROLE':warnings.append('CALENDA_CATALOG_CODE_NOT_USED_AS_SUPPLIER_REFERENCE')
    warnings.extend(image_warnings)
    return _copy(hydrated,supplier_reference=ref,brand=clean_supplier_brand(_get(hydrated,'brand','') or ''),variants=tuple(variants),warnings=tuple(dict.fromkeys(str(x) for x in warnings if str(x).strip())))
def governance_snapshot(hydrated):
    ref,status=_safe_ref(hydrated);variants,w=_govern_images(_variant_rows(hydrated))
    return {'schema':SCHEMA,'calenda_product_id':str(_get(hydrated,'calenda_product_id','') or ''),'supplier_reference_raw':str(_get(hydrated,'supplier_reference','') or ''),'supplier_reference':ref,'supplier_reference_status':status,'brand_clean':clean_supplier_brand(_get(hydrated,'brand','') or ''),'variants':variants,'warnings':w,'manufacturer_mpn':'','manufacturer_mpn_status':'NOT_DERIVED_FROM_SUPPLIER_HYDRATION','channel_write_allowed':False}
