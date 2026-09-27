from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any
from app.services.supplier_product_evidence import EvidenceFact, SupplierProductEvidence

def _fact(value: Any, source: str, url: str | None = None) -> EvidenceFact:
    return EvidenceFact(value=value, source=source, source_url=url)

def from_bultex99(product: Any) -> SupplierProductEvidence:
    url=str(getattr(product,"source_url","") or "")
    sid=str(getattr(product,"supplier_product_id","") or "")
    identity={"supplier_product_id":_fact(sid,"BULTEX99_PUBLIC",url),
              "name":_fact(str(getattr(product,"name","") or ""),"BULTEX99_PUBLIC",url)}
    sku=getattr(product,"supplier_sku",None)
    if sku: identity["supplier_sku"]=_fact(str(sku),"BULTEX99_PUBLIC",url)
    brand=getattr(product,"brand",None)
    if brand: identity["brand"]=_fact(str(brand),"BULTEX99_PUBLIC",url)
    tech={}
    standard=getattr(product,"standard",None)
    if standard: tech["standard"]=_fact(str(standard),"BULTEX99_PUBLIC",url)
    price=getattr(product,"gross_price_eur",None)
    price_fact=_fact(str(price),"BULTEX99_PUBLIC",url) if price is not None else None
    av=getattr(product,"availability",None)
    return SupplierProductEvidence("BULTEX99",sid,url,identity,tech,(),
        price_fact,_fact(av,"BULTEX99_PUBLIC",url) if av else None,(),
        {"legacy_stenso_refs":_fact(tuple(getattr(product,"legacy_stenso_refs",()) or ()),"MIGRATION_EVIDENCE",url)},
        ())

def from_calenda(h: Any) -> SupplierProductEvidence:
    url=str(getattr(h,"url","") or ""); key=str(getattr(h,"source_key","") or "")
    identity={"source_key":_fact(key,"CALENDA_PUBLIC",url),
              "name":_fact(str(getattr(h,"name","") or ""),"CALENDA_PUBLIC",url)}
    ref=getattr(h,"supplier_reference",None)
    if ref: identity["supplier_reference"]=_fact(str(ref),"CALENDA_PUBLIC",url)
    brand=getattr(h,"brand",None)
    if brand: identity["brand"]=_fact(str(brand),"CALENDA_PUBLIC",url)
    imgs=tuple(_fact(str(x),"CALENDA_PUBLIC",url) for x in (getattr(h,"images",()) or ()))
    p=getattr(h,"price_text",None); av=getattr(h,"availability_text",None)
    commercial={}
    cur=getattr(h,"currency",None)
    if cur: commercial["currency"]=_fact(str(cur),"CALENDA_PUBLIC",url)
    pid=getattr(h,"calenda_product_id",None)
    if pid: commercial["calenda_product_id"]=_fact(str(pid),"CALENDA_PUBLIC",url)
    return SupplierProductEvidence("CALENDA",key,url,identity,{},imgs,
        _fact(p,"CALENDA_PUBLIC",url) if p else None,
        _fact(av,"CALENDA_PUBLIC",url) if av else None,
        tuple(getattr(h,"variants",()) or ()),commercial,tuple(getattr(h,"warnings",()) or ()))

def from_palltex(h: Any) -> SupplierProductEvidence:
    url=str(getattr(h,"url","") or getattr(h,"final_url","") or "")
    key=str(getattr(h,"source_key","") or url)
    identity={"source_key":_fact(key,"PALLTEX_PUBLIC",url),
              "name":_fact(str(getattr(h,"name","") or ""),"PALLTEX_PUBLIC",url)}
    ref=getattr(h,"supplier_reference",None)
    if ref: identity["supplier_reference"]=_fact(str(ref),"PALLTEX_PUBLIC",url)
    brand=getattr(h,"brand",None)
    if brand: identity["brand"]=_fact(str(brand),"PALLTEX_PUBLIC",url)
    imgs=tuple(_fact(str(x),"PALLTEX_PUBLIC",url) for x in (getattr(h,"images",()) or ()))
    p=getattr(h,"price_text",None); av=getattr(h,"availability_text",None)
    commercial={}
    cur=getattr(h,"currency",None)
    if cur: commercial["currency"]=_fact(str(cur),"PALLTEX_PUBLIC",url)
    return SupplierProductEvidence("PALLTEX",key,url,identity,{},imgs,
        _fact(p,"PALLTEX_PUBLIC",url) if p else None,
        _fact(av,"PALLTEX_PUBLIC",url) if av else None,
        tuple(getattr(h,"variants",()) or ()),commercial,tuple(getattr(h,"warnings",()) or ()))
