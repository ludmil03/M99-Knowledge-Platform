from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from hashlib import sha256
from typing import Iterable, Mapping, Sequence
import random, re

M99_RE = re.compile(r"^M99 [0-9]{6}$")

class Gate(str, Enum):
    AUTO_READY="AUTO_READY"
    NEEDS_REVIEW="NEEDS_REVIEW"
    BLOCKED="BLOCKED"

@dataclass(frozen=True)
class SupplierCommercial:
    supplier_id:str
    supplier_reference:str
    verified:bool
    gross_price:Decimal|None
    currency:str
    revision_token:str
    availability:str="UNKNOWN"

@dataclass(frozen=True)
class ChannelConfig:
    channel_id:str
    market:str
    currency:str
    requested:bool
    authorized:bool
    ready:bool
    category_id:int|None
    tax_rules_group_id:int|None
    vat_rate:Decimal|None
    languages:tuple[str,...]
    platform:str

@dataclass(frozen=True)
class Variant:
    key:str
    label:str
    is_default:bool=False
    price_impact:Decimal=Decimal("0")

@dataclass(frozen=True)
class ImageEvidence:
    url:str
    source_role:str
    verified:bool
    relevant:bool
    content_hash:str=""

@dataclass(frozen=True)
class ProductCandidate:
    m99_id:str
    supplier:SupplierCommercial
    manufacturer_mpn:str
    localized_content:Mapping[str,Mapping[str,str]]
    variants:tuple[Variant,...]
    images:tuple[ImageEvidence,...]
    existing_channel_ids:Mapping[str,str]=field(default_factory=dict)

@dataclass(frozen=True)
class PricingDecision:
    gate:Gate
    discount_rate:Decimal|None
    supplier_gross:Decimal|None
    target_gross:Decimal|None
    reason:str
    revision_key:str=""

@dataclass(frozen=True)
class ChannelPlan:
    channel_id:str
    operation:str
    gate:Gate
    blockers:tuple[str,...]
    target_gross:Decimal|None
    target_net:Decimal|None
    discount_rate:Decimal|None
    tax_rules_group_id:int|None
    category_id:int|None
    hidden:bool=True
    available_for_order:bool=False
    visibility:str="none"

def _q(v:Decimal)->Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def deterministic_discount(m99_id:str,supplier_id:str,revision_token:str)->Decimal:
    # Production decision is stable for the supplier-price revision, preventing daily churn.
    seed=sha256(f"{m99_id}|{supplier_id}|{revision_token}|PRC-004".encode()).digest()
    points=int.from_bytes(seed[:4],"big") % 701  # 100..800? mapped below to 100..170 bp in 0.0001 units
    # 1.0000% .. 1.7000%, inclusive, 0.001% granularity
    units=1000 + (points % 701)
    return Decimal(units)/Decimal("100000")

def pricing_decision(product:ProductCandidate, previous:PricingDecision|None=None)->PricingDecision:
    s=product.supplier
    if not s.verified or s.gross_price is None or s.gross_price<=0:
        return PricingDecision(Gate.BLOCKED,None,s.gross_price,None,"VERIFIED_SUPPLIER_PRICE_REQUIRED")
    revision=f"{s.supplier_id}:{s.revision_token}:{s.gross_price}:{s.currency}"
    if previous and previous.revision_key==revision and previous.discount_rate is not None:
        d=previous.discount_rate
    else:
        d=deterministic_discount(product.m99_id,s.supplier_id,s.revision_token)
    raw=s.gross_price*(Decimal("1")-d)
    target=_q(raw)
    if target>=s.gross_price:
        # For tiny prices where cent rounding erases the discount, fail closed instead of violating policy.
        return PricingDecision(Gate.NEEDS_REVIEW,d,s.gross_price,None,"ROUNDING_ERASES_UNDERCUT",revision)
    return PricingDecision(Gate.AUTO_READY,d,s.gross_price,target,"PRC-004",revision)

def validate_product(product:ProductCandidate)->tuple[Gate,tuple[str,...]]:
    b=[]
    if not M99_RE.fullmatch(product.m99_id): b.append("INVALID_PERMANENT_M99_ID")
    if not product.supplier.verified: b.append("SUPPLIER_NOT_VERIFIED")
    if not product.manufacturer_mpn.strip(): b.append("MANUFACTURER_MPN_REQUIRED")
    if not product.localized_content: b.append("LOCALIZED_CONTENT_REQUIRED")
    defaults=sum(1 for v in product.variants if v.is_default)
    if product.variants and defaults!=1: b.append("EXACTLY_ONE_DEFAULT_VARIANT_REQUIRED")
    if not product.variants: b.append("VARIANTS_REQUIRED")
    good_images=[i for i in product.images if i.verified and i.relevant and i.source_role in {"MANUFACTURER","SUPPLIER"}]
    if not good_images: b.append("VERIFIED_RELEVANT_IMAGE_REQUIRED")
    return (Gate.BLOCKED if b else Gate.AUTO_READY, tuple(b))

def plan_channel(product:ProductCandidate, cfg:ChannelConfig, previous_price:PricingDecision|None=None)->ChannelPlan:
    blockers=[]
    if not cfg.requested: blockers.append("CHANNEL_NOT_REQUESTED")
    if not cfg.authorized: blockers.append("CHANNEL_NOT_AUTHORIZED")
    if not cfg.ready: blockers.append("CHANNEL_NOT_READY")
    pg,pb=validate_product(product); blockers.extend(pb)
    if not cfg.category_id or cfg.category_id<=0: blockers.append("CATEGORY_MAPPING_REQUIRED")
    if not cfg.tax_rules_group_id or cfg.tax_rules_group_id<=0 or cfg.vat_rate is None or cfg.vat_rate<=0:
        blockers.append("VAT_RESOLUTION_REQUIRED")
    missing=[x for x in cfg.languages if x not in product.localized_content]
    if missing: blockers.append("MISSING_LANGUAGES:"+",".join(missing))
    price=pricing_decision(product,previous_price)
    if price.gate!=Gate.AUTO_READY: blockers.append(price.reason)
    operation="UPDATE" if str(product.existing_channel_ids.get(cfg.channel_id,"")).strip() else "CREATE"
    gate=Gate.BLOCKED if blockers else Gate.AUTO_READY
    net=None
    if not blockers and price.target_gross is not None:
        net=_q(price.target_gross/(Decimal("1")+cfg.vat_rate))
    return ChannelPlan(cfg.channel_id,operation,gate,tuple(blockers),price.target_gross,net,price.discount_rate,cfg.tax_rules_group_id,cfg.category_id)

def plan_selected_channels(product:ProductCandidate, configs:Sequence[ChannelConfig])->tuple[ChannelPlan,...]:
    # Real write set is REQUESTED ∩ AUTHORIZED ∩ READY; no automatic "all".
    selected=[c for c in configs if c.requested]
    return tuple(plan_channel(product,c) for c in selected)

def quality_readback(plan:ChannelPlan, actual:Mapping[str,str|int|Decimal], *, expected_reference:str,
                     expected_images:int, expected_combinations:int)->tuple[Gate,tuple[str,...]]:
    b=[]
    if plan.gate!=Gate.AUTO_READY: b.append("PLAN_NOT_AUTO_READY")
    if str(actual.get("reference",""))!=expected_reference: b.append("REFERENCE_MISMATCH")
    if str(actual.get("active",""))!="0": b.append("NOT_HIDDEN")
    if str(actual.get("available_for_order",""))!="0": b.append("ORDERABLE_TOO_EARLY")
    if str(actual.get("visibility",""))!="none": b.append("VISIBILITY_MISMATCH")
    if str(actual.get("category_id",""))!=str(plan.category_id): b.append("CATEGORY_MISMATCH")
    try: gross=_q(Decimal(str(actual.get("gross_price",""))))
    except Exception: gross=None
    if gross!=plan.target_gross: b.append("GROSS_PRICE_MISMATCH")
    if str(actual.get("tax_rules_group_id",""))!=str(plan.tax_rules_group_id): b.append("VAT_RULE_MISMATCH")
    if int(actual.get("image_count",0) or 0)<expected_images: b.append("IMAGE_READBACK_MISMATCH")
    if int(actual.get("combination_count",0) or 0)!=expected_combinations: b.append("COMBINATION_READBACK_MISMATCH")
    if expected_combinations and int(actual.get("default_combination_count",0) or 0)!=1: b.append("DEFAULT_COMBINATION_MISMATCH")
    return (Gate.BLOCKED if b else Gate.AUTO_READY, tuple(b))
