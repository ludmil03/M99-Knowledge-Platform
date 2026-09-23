from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Any, Mapping, Callable
import secrets

ALLOWED_CHANNELS = (
    "mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com",
    "laviro.ro","alviro.ro","toplinka.com"
)
DISCOUNT_MIN = Decimal("0.010")
DISCOUNT_MAX = Decimal("0.017")

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

@dataclass(frozen=True)
class CurrentGateContext:
    m99_identity: str | None
    duplicate_state: str                 # NEW | EXACT_EXISTING | AMBIGUOUS | CONFLICT
    vat_rule_id: str | None
    verified_supplier_gross: str | None
    supplier_currency: str | None
    observed_at: str | None
    persisted_discount: str | None = None
    previous_verified_supplier_gross: str | None = None
    rounding_policy_id: str | None = None
    rounded_target_gross: str | None = None

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

def normalize_channels(channels:list[str]) -> tuple[list[str],list[str]]:
    seen=[]; blocked=[]
    for c in channels:
        if c not in ALLOWED_CHANNELS:
            blocked.append(c); continue
        if c not in seen: seen.append(c)
    return seen, blocked

def _valid_identity(v:str|None)->bool:
    return bool(v and len(v)==10 and v.startswith("M99 ") and v[4:].isdigit())

def _decimal(v:str|None)->Decimal|None:
    if v is None or str(v).strip()=="": return None
    try: return Decimal(str(v))
    except Exception: return None

def choose_discount(ctx:CurrentGateContext, randbelow:Callable[[int],int]|None=None)->Decimal|None:
    old=_decimal(ctx.persisted_discount)
    current=_decimal(ctx.verified_supplier_gross)
    previous=_decimal(ctx.previous_verified_supplier_gross)
    if old is not None and DISCOUNT_MIN <= old <= DISCOUNT_MAX and current == previous:
        return old
    if current is None or current <= 0:
        return None
    rb=randbelow or secrets.randbelow
    # 701 exact basis points-of-percent steps: 1.000% ... 1.700%
    return Decimal(1000 + rb(701)) / Decimal(100000)

def current_governance(c:SupplierProductCandidate, channels:list[str], ctx:CurrentGateContext,
                       randbelow:Callable[[int],int]|None=None)->dict[str,Any]:
    blockers=validate_candidate(c)
    targets, unknown=normalize_channels(channels)
    if not targets: blockers.append("CHANNEL_TARGET_MISSING")
    if unknown: blockers.append("UNKNOWN_CHANNEL_TARGET")
    if not _valid_identity(ctx.m99_identity): blockers.append("M99_IDENTITY_INVALID")
    if ctx.duplicate_state not in {"NEW","EXACT_EXISTING"}: blockers.append("DUPLICATE_GATE_BLOCKED")
    if not ctx.vat_rule_id: blockers.append("VAT_RULE_UNRESOLVED")
    gross=_decimal(ctx.verified_supplier_gross)
    if gross is None or gross <= 0: blockers.append("SUPPLIER_GROSS_NOT_VERIFIED")
    if not ctx.supplier_currency: blockers.append("SUPPLIER_CURRENCY_MISSING")
    if not ctx.observed_at: blockers.append("SUPPLIER_OBSERVED_AT_MISSING")
    discount=choose_discount(ctx,randbelow)
    target_pre=None
    if gross is not None and gross>0 and discount is not None:
        target_pre=gross*(Decimal("1")-discount)
    # Exact commercial rounding remains a governed external decision. Fail closed.
    if not ctx.rounding_policy_id or ctx.rounded_target_gross is None:
        blockers.append("ROUNDING_POLICY_REQUIRED")
    rounded=_decimal(ctx.rounded_target_gross)
    if rounded is not None and gross is not None and not (Decimal("0") < rounded < gross):
        blockers.append("ROUNDED_TARGET_INVALID")
    blockers=sorted(set(blockers))
    return {
        "schema_version":"R7K.4-R3-CANONICAL-INTEGRATION",
        "mode":"READ_ONLY_MAXSIM",
        "supplier_candidate":asdict(c),
        "channel_targets":targets,
        "unknown_channel_targets":unknown,
        "identity":{"m99_identity":ctx.m99_identity,"allocation_owner":"CURRENT_ONLY"},
        "duplicate_guard":{"state":ctx.duplicate_state,"owner":"CURRENT_ONLY"},
        "pricing":{
            "policy":"PRC-004_RANDOM_1_0_TO_1_7_PERSISTED",
            "verified_supplier_gross":ctx.verified_supplier_gross,
            "currency":ctx.supplier_currency,
            "observed_at":ctx.observed_at,
            "discount":str(discount) if discount is not None else None,
            "target_gross_pre_rounding":str(target_pre) if target_pre is not None else None,
            "rounding_policy_id":ctx.rounding_policy_id,
            "rounded_target_gross":ctx.rounded_target_gross,
            "regenerated": not (
                _decimal(ctx.persisted_discount) is not None
                and _decimal(ctx.persisted_discount) is not None
                and DISCOUNT_MIN <= _decimal(ctx.persisted_discount) <= DISCOUNT_MAX
                and _decimal(ctx.verified_supplier_gross)==_decimal(ctx.previous_verified_supplier_gross)
            )
        },
        "vat":{"tax_rule_id":ctx.vat_rule_id,"owner":"CURRENT_CHANNEL_POLICY"},
        "stock":{"supplier_availability_is_m99_physical_stock":False},
        "publish":{"state":"HIDDEN_FIRST","live_write_enabled":False,"readback":"MANDATORY"},
        "legacy_reuse":{"supplier_acquisition":True,"variant_acquisition":True,
                        "commercial_observation":True,"image_urls":True},
        "blockers":blockers,
        "ready_for_hidden_publish_plan":not blockers,
        "writes_performed":False
    }

def build_integration_plan(c:SupplierProductCandidate, channels:list[str], ctx:CurrentGateContext,
                           randbelow:Callable[[int],int]|None=None)->dict[str,Any]:
    return current_governance(c,channels,ctx,randbelow)
