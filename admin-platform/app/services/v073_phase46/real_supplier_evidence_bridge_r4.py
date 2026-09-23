from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse
import re

SCHEMA = "R7K.4-R4-REAL-SUPPLIER-EVIDENCE"
MODE = "READ_ONLY_EVIDENCE"
ALLOWED_SCHEMES = {"https"}
BLOCKED_IMAGE_TOKENS = (
    "logo","icon","sprite","banner","header","footer","cart","search",
    "payment","facebook","instagram","youtube","placeholder","no-image"
)

@dataclass(frozen=True)
class VariantEvidence:
    supplier_variant_code: str | None
    size: str | None
    barcode: str | None
    availability: str                  # IN_STOCK | OUT_OF_STOCK | UNKNOWN
    supplier_quantity: str | None      # supplier evidence only; never M99 stock
    price_gross: str | None
    currency: str | None

@dataclass(frozen=True)
class SupplierEvidence:
    supplier: str
    supplier_reference: str
    product_name: str
    source_url: str
    observed_at: str
    price_gross: str | None
    currency: str | None
    variants: tuple[VariantEvidence, ...]
    image_urls: tuple[str, ...]
    source_status: str                 # VERIFIED | VERIFICATION_FAILED
    failure_reason: str | None = None

def _clean(v: Any) -> str | None:
    if v is None: return None
    s = str(v).strip()
    return s or None

def _dec(v: Any) -> Decimal | None:
    s = _clean(v)
    if s is None: return None
    s = s.replace("\xa0"," ").replace(" ","").replace(",",".")
    s = re.sub(r"[^0-9.\-]", "", s)
    if not s: return None
    try:
        d = Decimal(s)
        return d if d >= 0 else None
    except InvalidOperation:
        return None

def normalize_currency(v: Any) -> str | None:
    s = (_clean(v) or "").upper()
    aliases = {"€":"EUR","EUR":"EUR","EURO":"EUR","ЛВ":"BGN","ЛВ.":"BGN","BGN":"BGN",
               "RON":"RON","LEI":"RON","ЛЕИ":"RON"}
    return aliases.get(s)

def exact_product_url(url: str, expected_host: str | None = None) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme not in ALLOWED_SCHEMES or not p.netloc or not p.path or p.path == "/":
        return False
    host = p.netloc.lower().split(":")[0]
    if expected_host:
        eh = expected_host.lower().removeprefix("www.")
        if host.removeprefix("www.") != eh:
            return False
    if any(x in p.path.lower() for x in ("/category","/search","/cart","/login")):
        return False
    return True

def normalize_availability(value: Any, quantity: Any = None) -> tuple[str,str|None]:
    q = _dec(quantity)
    if q is not None:
        return ("IN_STOCK" if q > 0 else "OUT_OF_STOCK", str(q))
    s = (_clean(value) or "").lower()
    positive = ("in_stock","in stock","available","наличен","налично","на склад")
    negative = ("out_of_stock","out of stock","unavailable","изчерпан","няма наличност")
    if any(x in s for x in negative): return "OUT_OF_STOCK", None
    if any(x in s for x in positive): return "IN_STOCK", None
    return "UNKNOWN", None

def filter_images(urls: Iterable[Any], source_host: str | None = None) -> tuple[str,...]:
    out=[]
    for raw in urls or ():
        u=_clean(raw)
        if not u: continue
        try: p=urlparse(u)
        except Exception: continue
        if p.scheme != "https" or not p.netloc: continue
        low=(p.path+"?"+p.query).lower()
        if any(t in low for t in BLOCKED_IMAGE_TOKENS): continue
        if not re.search(r"\.(?:jpe?g|png|webp)(?:$|\?)", low): continue
        if source_host and p.netloc.lower().removeprefix("www.") != source_host.lower().removeprefix("www."):
            continue
        if u not in out: out.append(u)
    return tuple(out)

def _variant_from_mapping(v: Mapping[str,Any], default_currency: str|None) -> VariantEvidence:
    status, qty = normalize_availability(v.get("availability"), v.get("supplier_quantity"))
    cur = normalize_currency(v.get("currency")) or default_currency
    pg = _dec(v.get("price_gross"))
    return VariantEvidence(
        _clean(v.get("supplier_variant_code")), _clean(v.get("size")),
        _clean(v.get("barcode")), status, qty,
        str(pg) if pg is not None else None, cur
    )

def from_public_page_observation(o: Mapping[str,Any], expected_host: str|None=None) -> SupplierEvidence:
    url=_clean(o.get("source_url")) or ""
    supplier=_clean(o.get("supplier")) or ""
    ref=_clean(o.get("supplier_reference")) or ""
    name=_clean(o.get("product_name")) or ""
    observed=_clean(o.get("observed_at")) or ""
    cur=normalize_currency(o.get("currency"))
    price=_dec(o.get("price_gross"))
    failures=[]
    if not exact_product_url(url, expected_host): failures.append("SOURCE_URL_NOT_EXACT")
    if not supplier: failures.append("SUPPLIER_MISSING")
    if not ref: failures.append("SUPPLIER_REFERENCE_MISSING")
    if not name: failures.append("PRODUCT_NAME_MISSING")
    if not observed: failures.append("OBSERVED_AT_MISSING")
    if price is None or price <= 0: failures.append("PRICE_GROSS_NOT_VERIFIED")
    if cur is None: failures.append("CURRENCY_NOT_VERIFIED")
    host=urlparse(url).netloc if url else None
    images=filter_images(o.get("image_urls") or (), host if expected_host else None)
    variants=tuple(_variant_from_mapping(v,cur) for v in (o.get("variants") or ()))
    if not variants: failures.append("VARIANT_EVIDENCE_MISSING")
    status="VERIFICATION_FAILED" if failures else "VERIFIED"
    return SupplierEvidence(supplier,ref,name,url,observed,
        str(price) if price is not None else None,cur,variants,images,status,
        ",".join(sorted(set(failures))) if failures else None)

def from_legacy_b2b_offer(offer: Any, observed_at: str) -> SupplierEvidence:
    code=_clean(getattr(offer,"supplier_variant_code",None))
    ref=(code.rsplit(".",1)[0] if code and "." in code else code) or ""
    stock=getattr(offer,"warehouse_stock",None)
    qty=getattr(stock,"quantity",None) if stock is not None else None
    avail, q=normalize_availability(None,qty)
    cur=normalize_currency(getattr(offer,"currency",None))
    # Legacy B2B model stores ex-VAT prices. They are evidence, but NOT silently relabeled as gross.
    v=VariantEvidence(code,_clean(getattr(offer,"size",None)),
        _clean(getattr(offer,"barcode",None)),avail,q,None,cur)
    url=_clean(getattr(offer,"source_url",None)) or ""
    failures=[]
    if not exact_product_url(url): failures.append("SOURCE_URL_NOT_EXACT")
    if not ref: failures.append("SUPPLIER_REFERENCE_MISSING")
    if not cur: failures.append("CURRENCY_NOT_VERIFIED")
    if not observed_at: failures.append("OBSERVED_AT_MISSING")
    # Gross price must be independently resolved by current VAT/commercial policy.
    failures.append("PRICE_GROSS_NOT_VERIFIED")
    return SupplierEvidence(_clean(getattr(offer,"supplier",None)) or "",ref,
        _clean(getattr(offer,"name",None)) or "",url,observed_at,None,cur,(v,),(),
        "VERIFICATION_FAILED",",".join(sorted(set(failures))))

def evidence_gate(e: SupplierEvidence) -> dict[str,Any]:
    blockers=[]
    if e.source_status!="VERIFIED":
        blockers.extend((e.failure_reason or "VERIFICATION_FAILED").split(","))
    if not e.image_urls: blockers.append("IMAGE_EVIDENCE_MISSING")
    if not e.variants: blockers.append("VARIANT_EVIDENCE_MISSING")
    if not e.price_gross: blockers.append("SUPPLIER_PRICE_NOT_VERIFIED")
    if not e.currency: blockers.append("SUPPLIER_CURRENCY_MISSING")
    blockers=sorted(set(x for x in blockers if x))
    return {
        "schema":SCHEMA,"mode":MODE,"evidence":asdict(e),
        "supplier_stock_is_m99_physical_stock":False,
        "source_failure_means_zero_stock":False,
        "commercial_observation_only":True,
        "image_processing_stage":"DISCOVERY_ONLY_NO_DOWNLOAD",
        "ready_for_r3_canonical_bridge":not blockers,
        "blockers":blockers,
        "writes_performed":False,
        "network_performed_by_bridge":False,
        "website_write_enabled":False
    }
