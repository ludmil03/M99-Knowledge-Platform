from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

class PricingStatus(str, Enum):
    AUTO_APPROVED="AUTO_APPROVED"
    FLOOR_PROTECTED="FLOOR_PROTECTED"
    OPERATOR_REVIEW="OPERATOR_REVIEW"

@dataclass
class PricingInput:
    stenso_public_price_gross: Decimal
    dolibarr_acquisition_cost_gross: Decimal
    profit_floor_gross: Decimal
    discount_vs_stenso_pct: Decimal = Decimal("1.5")

def _q(v):
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calculate_price(d):
    target = _q(d.stenso_public_price_gross * (Decimal("1") - d.discount_vs_stenso_pct/Decimal("100")))
    floor = max(d.dolibarr_acquisition_cost_gross, d.profit_floor_gross)
    if target >= floor:
        return {"target":target,"floor":_q(floor),"final":target,"status":PricingStatus.AUTO_APPROVED}
    status = PricingStatus.FLOOR_PROTECTED if floor == d.dolibarr_acquisition_cost_gross else PricingStatus.OPERATOR_REVIEW
    return {"target":target,"floor":_q(floor),"final":_q(floor),"status":status}
