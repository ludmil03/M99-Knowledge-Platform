from __future__ import annotations
from decimal import Decimal, InvalidOperation
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from collections.abc import Mapping
import re
from typing import Any
from app.services.supplier_product_evidence import EvidenceFact, SupplierProductEvidence

def _fact(value: Any, source: str, url: str | None = None) -> EvidenceFact:
    return EvidenceFact(value=value, source=source, source_url=url)

def _bultex_price(product: Any, url: str, commercial: dict, warnings: list) -> EvidenceFact | None:
    """Normalize observed values, never infer a number from surrounding page text."""
    gross = getattr(product, "gross_price_eur", None)
    raw = gross if gross is not None else getattr(product, "price_text", None)
    currency = "EUR" if gross is not None else str(getattr(product, "currency", "") or "").strip()
    if currency:
        commercial["currency"] = _fact(currency, "BULTEX99_PUBLIC", url)
    if raw is None or not str(raw).strip():
        return None
    commercial["price_text"] = _fact(str(raw), "BULTEX99_PUBLIC", url)
    # Native hydration supplies numeric price_text and a separate currency. A
    # thousands separator or multiple amounts needs source review, not guessing.
    text = str(raw).strip()
    if not re.fullmatch(r"[0-9]+(?:[.,][0-9]{1,2})?", text):
        warnings.append("PRICE_AMBIGUOUS_OR_INVALID")
        return None
    try:
        value = Decimal(text.replace(",", "."))
    except InvalidOperation:
        warnings.append("PRICE_AMBIGUOUS_OR_INVALID")
        return None
    if not value.is_finite() or value <= 0:
        warnings.append("PRICE_AMBIGUOUS_OR_INVALID")
        return None
    if not re.fullmatch(r"[A-Z]{3}", currency):
        warnings.append("PRICE_CURRENCY_NOT_PROVEN")
        return None
    # This remains a supplier observation. Native price_text does not prove VAT
    # inclusion; only the historical gross_price_eur field explicitly does so.
    if gross is not None:
        commercial["price_basis"] = _fact("GROSS", "BULTEX99_PUBLIC", url)
    return _fact(str(value), "BULTEX99_PUBLIC", url)


def from_bultex99(product: Any) -> SupplierProductEvidence:
    source = "BULTEX99_PUBLIC"
    url = str(getattr(product, "source_url", "") or getattr(product, "url", "") or "")
    sid = str(getattr(product, "supplier_product_id", "") or getattr(product, "source_key", "") or "")
    identity = {
        "supplier_product_id": _fact(sid, source, url),
        "name": _fact(str(getattr(product, "name", "") or ""), source, url),
    }
    sku = getattr(product, "supplier_sku", None) or getattr(product, "supplier_reference", None)
    if sku:
        identity["supplier_sku"] = _fact(str(sku), source, url)
        identity["supplier_reference"] = _fact(str(sku), source, url)
    brand = getattr(product, "brand", None)
    if brand:
        identity["brand"] = _fact(str(brand), source, url)
    tech = {}
    for field in ("standard", "description"):
        value = getattr(product, field, None)
        if value:
            tech[field] = _fact(str(value), source, url)
    images = tuple(_fact(str(image), source, url) for image in (getattr(product, "images", ()) or ()))
    warnings = list(getattr(product, "warnings", ()) or ())
    variants = []
    for variant in (getattr(product, "variants", ()) or ()):
        if isinstance(variant, Mapping):
            variants.append(deepcopy(dict(variant)))
        elif is_dataclass(variant) and not isinstance(variant, type):
            variants.append(asdict(variant))
        else:
            warnings.append("VARIANT_SHAPE_UNSUPPORTED")
    commercial = {
        "legacy_stenso_refs": _fact(tuple(getattr(product, "legacy_stenso_refs", ()) or ()), "MIGRATION_EVIDENCE", url),
    }
    price_fact = _bultex_price(product, url, commercial, warnings)
    availability = getattr(product, "availability", None) or getattr(product, "availability_text", None)
    return SupplierProductEvidence(
        "BULTEX99", sid, url, identity, tech, images, price_fact,
        _fact(availability, source, url) if availability else None,
        tuple(variants), commercial, tuple(dict.fromkeys(warnings)),
    )

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
