from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

MIN_MARGIN=Decimal("1.00")
MAX_MARGIN=Decimal("1.70")

@dataclass(frozen=True)
class PriceVatDecision:
    supplier_gross: Decimal
    margin_percent: Decimal
    target_gross: Decimal
    vat_rate: Decimal
    vat_proven: bool
    blockers: tuple[str,...]
    ready: bool
    write_performed: bool=False

def evaluate_price_vat(*, supplier_gross:Decimal, margin_percent:Decimal,
                       vat_rate:Decimal|None, vat_proven:bool)->PriceVatDecision:
    blockers=[]
    supplier_gross=Decimal(supplier_gross)
    margin_percent=Decimal(margin_percent)
    if supplier_gross <= 0: blockers.append("INVALID_SUPPLIER_GROSS")
    if not (MIN_MARGIN <= margin_percent <= MAX_MARGIN):
        blockers.append("MARGIN_OUTSIDE_POLICY")
    if not vat_proven or vat_rate is None:
        blockers.append("VAT_NOT_PROVEN")
        rate=Decimal("0")
    else:
        rate=Decimal(vat_rate)
        if rate < 0: blockers.append("INVALID_VAT_RATE")
    target=(supplier_gross*(Decimal("1")-margin_percent/Decimal("100"))).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP) if supplier_gross>0 else Decimal("0.00")
    if supplier_gross>0 and target>=supplier_gross: blockers.append("TARGET_NOT_BELOW_SUPPLIER")
    return PriceVatDecision(supplier_gross,margin_percent,target,rate,vat_proven,tuple(dict.fromkeys(blockers)),not blockers,False)
