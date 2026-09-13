from __future__ import annotations
import re
from typing import Any

SCHEMA="m99.phase46.r7b.calenda_supplier_reconciliation.v1"

_BOUNDARY_MARKERS=(
    "допълнителна информация","подобни продукти","related products",
    "additional information","препоръчани продукти","recommended products",
)

def normalize_space(v:Any)->str:
    return re.sub(r"\s+"," ",str(v or "")).strip()

def clean_supplier_brand(raw:Any)->str:
    s=normalize_space(raw)
    low=s.casefold()
    cut=len(s)
    for marker in _BOUNDARY_MARKERS:
        i=low.find(marker)
        if i>=0:cut=min(cut,i)
    return s[:cut].strip(" -–—|:;,")

def classify_calenda_page_code(value:Any)->dict:
    raw=normalize_space(value)
    if not raw:
        return {"raw":"","role":"MISSING","safe_supplier_reference":""}
    if re.fullmatch(r"ID\d+",raw,re.I):
        return {"raw":raw,"role":"CALENDA_CATALOG_CODE","safe_supplier_reference":""}
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*-\d+[A-Za-z0-9._/-]*",raw):
        return {"raw":raw,"role":"SUPPLIER_REFERENCE_CANDIDATE","safe_supplier_reference":raw}
    if re.fullmatch(r"\d{2,12}",raw):
        return {"raw":raw,"role":"SUPPLIER_REFERENCE_CANDIDATE","safe_supplier_reference":raw}
    return {"raw":raw,"role":"UNCLASSIFIED_SUPPLIER_TOKEN","safe_supplier_reference":""}

def reconcile_observed_product(row:dict)->dict:
    code=classify_calenda_page_code(row.get("page_code_candidate"))
    brand=clean_supplier_brand(row.get("brand_raw") or row.get("brand"))
    colors=[]
    seen=set()
    for c in row.get("colors") or []:
        key=normalize_space(c).casefold()
        if key and key not in seen:
            seen.add(key);colors.append(normalize_space(c))
    return {
        "schema":SCHEMA,
        "calenda_product_id":normalize_space(row.get("product_id")),
        "title":normalize_space(row.get("title")),
        "supplier_brand_evidence":brand,
        "page_code_raw":code["raw"],
        "page_code_role":code["role"],
        "supplier_reference_candidate":code["safe_supplier_reference"],
        "manufacturer_mpn":"",
        "manufacturer_mpn_status":"UNRESOLVED_REQUIRES_EXACT_MANUFACTURER_EVIDENCE",
        "colors_observed":colors,
        "warnings":[
            *([] if brand else ["SUPPLIER_BRAND_NOT_FOUND"]),
            *(["CALENDA_INTERNAL_CODE_NOT_SUPPLIER_REFERENCE"] if code["role"]=="CALENDA_CATALOG_CODE" else []),
            *(["PAGE_CODE_UNCLASSIFIED"] if code["role"]=="UNCLASSIFIED_SUPPLIER_TOKEN" else []),
        ],
    }

def manufacturer_identity_gate(*, supplier_candidate:str="", manufacturer_evidence:dict|None=None)->dict:
    manufacturer_evidence=manufacturer_evidence or {}
    exact=(
        manufacturer_evidence.get("status")=="OPERATOR_CONFIRMED_EXACT"
        and manufacturer_evidence.get("manufacturer_product_code_status")=="VERIFIED_EXACT_REFERENCE"
        and bool(normalize_space(manufacturer_evidence.get("manufacturer_product_code")))
    )
    mpn=normalize_space(manufacturer_evidence.get("manufacturer_product_code")) if exact else ""
    return {
        "supplier_reference_candidate":normalize_space(supplier_candidate),
        "manufacturer_mpn":mpn,
        "manufacturer_mpn_verified":bool(mpn),
        "same_text_allowed_separate_roles":bool(mpn and normalize_space(supplier_candidate)==mpn),
    }
