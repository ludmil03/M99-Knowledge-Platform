from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Mapping

@dataclass(frozen=True)
class SupplierVariant:
    supplier_variant_code: str
    size: str | None
    barcode: str | None
    currency: str
    purchase_price_ex_vat: str | None
    recommended_price_ex_vat: str | None
    supplier_stock: str | None
    source_url: str

@dataclass(frozen=True)
class SupplierProductCandidate:
    supplier: str
    supplier_product_id: str | None
    supplier_reference: str | None
    name: str
    source_url: str
    variants: tuple[SupplierVariant, ...]
    images: tuple[str, ...] = ()
    acquisition_source: str = "LEGACY_RECOVERED"
    writes_performed: bool = False

def _s(v: Any) -> str | None:
    return None if v is None else str(v)

def from_legacy_bultex_offer(offer: Any) -> SupplierProductCandidate:
    stock=getattr(offer,"warehouse_stock",None)
    code=_s(getattr(offer,"supplier_variant_code","")) or ""
    v=SupplierVariant(
        code,_s(getattr(offer,"size",None)),_s(getattr(offer,"barcode",None)),
        _s(getattr(offer,"currency","")) or "",
        _s(getattr(offer,"purchase_price_ex_vat",None)),
        _s(getattr(offer,"recommended_price_ex_vat",None)),
        _s(getattr(stock,"quantity",None)),
        _s(getattr(offer,"source_url","")) or ""
    )
    ref=code.rsplit(".",1)[0] if "." in code else (code or None)
    return SupplierProductCandidate(
        _s(getattr(offer,"supplier","")) or "",
        _s(getattr(offer,"supplier_product_id",None)),
        ref,_s(getattr(offer,"name","")) or "",v.source_url,(v,)
    )

def from_stenso_observation(o: Mapping[str,Any]) -> SupplierProductCandidate:
    ident=o.get("identity") or {}
    facts=o.get("facts") or {}
    com=o.get("commercial_observation") or {}
    prices=com.get("raw_price_observations") or []
    price=prices[0] if prices else {}
    variants=tuple(
        SupplierVariant(
            str(ident.get("supplier_reference") or ""),str(size),None,
            str(price.get("currency") or ""),None,_s(price.get("value")),None,
            str(o.get("source_url") or "")
        ) for size in (facts.get("sizes_visible") or [])
    )
    return SupplierProductCandidate(
        str(o.get("source_name") or "Stenso"),None,
        _s(ident.get("supplier_reference")),str(ident.get("title") or ""),
        str(o.get("source_url") or ""),variants,tuple(o.get("supplier_images") or ())
    )

def validate_candidate(c: SupplierProductCandidate) -> list[str]:
    b=[]
    if not c.supplier: b.append("SUPPLIER_MISSING")
    if not c.source_url: b.append("SOURCE_URL_MISSING")
    if not c.supplier_reference: b.append("SUPPLIER_REFERENCE_MISSING")
    if not c.variants: b.append("VARIANTS_MISSING")
    if any(not v.currency for v in c.variants): b.append("SUPPLIER_CURRENCY_MISSING")
    return sorted(set(b))

def to_current_draft(c: SupplierProductCandidate,channel_targets:list[str]) -> dict[str,Any]:
    b=validate_candidate(c)
    return {
        "schema_version":"R7K.4-LEGACY-BRIDGE-R2.2","mode":"DRAFT_ONLY",
        "supplier_candidate":asdict(c),
        "channel_targets":list(dict.fromkeys(channel_targets)),
        "legacy_reuse":{
            "supplier_acquisition":True,"variant_acquisition":True,
            "commercial_observation":True,"image_urls":True
        },
        "current_governance":{
            "identity_allocation":"CURRENT_ONLY",
            "duplicate_guard":"CURRENT_ONLY",
            "pricing_policy":"CURRENT_ONLY_RANDOM_1_0_TO_1_7_PERSISTED",
            "vat_resolution":"CURRENT_CHANNEL_POLICY",
            "publish_state":"HIDDEN_FIRST",
            "readback":"MANDATORY"
        },
        "blockers":b,
        "ready_for_current_gates":not b,
        "writes_performed":False
    }
